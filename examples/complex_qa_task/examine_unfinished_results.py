import json
from email import message
from glob import glob

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.agent import Agent
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker
from mephisto.tools.data_browser import DataBrowser
from mephisto.tools.examine_utils import prompt_for_options
import traceback

db = None

QUAL_ID_SANDBOX = '3QG4W3BIFAZMGUY838Z4EKY6FWDWNM'
QUAL_ID = '3DA2M59FD03MKSVQ6KIPVI7Q8Y2RXF'
BASE_AMOUNT = 0.01

with open("/Users/vaibhav.adlakha/Desktop/topiocqa/topiocqa_train.json", "r") as f:
    topiocqa_data = json.load(f)

def get_ids(question, answer, conv_id):
    matches = []
    for turn in topiocqa_data:
        if conv_id != -1:
            if turn['Conversation_no'] == conv_id and turn['Question'] == question and turn['Answer'] == answer:
                matches.append((turn['Conversation_no'], turn['Turn_no']))
        else:
            if turn['Question'] == question and turn['Answer'] == answer:
                matches.append((turn['Conversation_no'], turn['Turn_no']))
    if len(matches) == 0:
        print(f"No matches found for {question} and {answer}")
        return -1, -1
    elif len(matches) > 1:
        print(f"Multiple matches found for {question} and {answer}")
        return -1, -1
    else:
        return matches[0]


def calculate_task_bonus_from_data(data):
    global db

    worker_name = Worker.get(db, data["worker_id"]).worker_name
    unit = Unit.get(db, data["unit_id"])
    assignment_id = unit.get_mturk_assignment_id()

    bool_message_amount = 0.05
    text_message_amount = 0.2

    messages = [message for message in data["data"]["messages"] if "id" in message]
    num_bool_messages = 0
    num_text_messages = 0
    for message in messages:
        if message["id"] == 'Chat Agent' and "boolValue" in message:
            num_bool_messages += 1
        elif message["id"] == 'Chat Agent' and "text" in message:
            num_text_messages += 1
        else:
            continue
    
    total_bonus_amount = num_bool_messages * bool_message_amount + num_text_messages * text_message_amount
    return total_bonus_amount, num_bool_messages, num_text_messages


def format_for_printing_data(data):

    with open("final_complex_dataset.json", "r") as f:
        final_data = json.load(f)

    global db
    # Custom tasks can define methods for how to display their data in a relevant way
    worker_name = Worker.get(db, data["worker_id"]).worker_name
    duration = data["task_end"] - data["task_start"]
    metadata_string = (
        f"Worker: {worker_name}\nUnit: {data['unit_id']}\n"
        f"Duration: {int(duration)}\nStatus: {data['status']}\n"
    )

    messages = [message for message in data["data"]["messages"] if "id" in message]
    output_string = ''
    latest_answer = ''
    conv_id = -1
    turn_id = -1

    complex_questions = 0
    for message in messages:
        if message["id"] == 'System' and 'question' in message and 'answer' in message:
            output_string += f"\nQuestion: {message['question']}\nAnswer: {message['answer']}\n"
            latest_answer = message['answer']
            if 'conv_id' in message and 'turn_id' in message:
                conv_id = message['conv_id']
                turn_id = message['turn_id']
            else:
                conv_id, turn_id = get_ids(message['question'], message['answer'], conv_id)
        elif message["id"] == 'Chat Agent' and "text" in message:
            complex_questions += 1
            output_string += f"Complex Question: {message['text']}\n"
            final_data.append({
                "question": message['text'],
                "answer": latest_answer,
                "conversation_no": conv_id,
                "turn_no": turn_id
            })
    if complex_questions > 0:
        with open("final_complex_dataset.json", "w") as f:
            json.dump(final_data, f, indent=4)
        return f"-------------------\n{metadata_string}{output_string}"
    else:
        return ""


def examine_unfinished_results():
    global db
    data_browser = DataBrowser(db=db)

    task_name, block_qualification, approve_qualification = prompt_for_options()

    tasks = db.find_tasks(task_name=task_name)
    assert len(tasks) >= 1, f"No task found under name {task_name}"

    units = data_browser.get_units_for_task_name(task_name, return_incomplete=True)

    worker_payment_dict = {}

    for unit in units:
        assignment = unit.get_assignment()
        assignment_dir = unit.get_assignment().get_data_dir()

        data_files = glob(assignment_dir + "/**/state.json", recursive=True)
        for data_file in data_files:
            agent_id = data_file.split('/')[-2]
            if unit.agent_id is not None and unit.agent_id == agent_id:
                continue
            agent = Agent.get(db, agent_id)
            worker = agent.get_worker()

            with open(data_file, 'r') as f:
                file_data = json.load(f)
            
            messages = file_data["outputs"]["messages"]

            data = {}
            data["status"] = unit.get_status()
            data["worker_id"] = worker.db_id
            data["unit_id"] = unit.db_id
            data["assignment_id"] = assignment.db_id
            data["task_start"] = 0
            data["task_end"] = 0
            data["data"] = {}
            data["data"]["messages"] = messages

            try:
                formatted = format_for_printing_data(data)
                if len(formatted) > 0:
                    print(formatted)
                bonus_amount, num_bool_messages, num_text_messages = calculate_task_bonus_from_data(data)
                bonus_amount = bonus_amount + BASE_AMOUNT
                if worker.worker_name not in worker_payment_dict:
                    worker_payment_dict[worker.worker_name] = {"amount": 0.0, "num_bool_messages": 0, "num_text_messages": 0, "num_tasks": 0}
                worker_payment_dict[worker.worker_name]["amount"] += bonus_amount
                worker_payment_dict[worker.worker_name]["num_bool_messages"] += num_bool_messages
                worker_payment_dict[worker.worker_name]["num_text_messages"] += num_text_messages
                worker_payment_dict[worker.worker_name]["num_tasks"] += 1

            except Exception as e:
                print(f"Unexpected error formatting data for {unit}: {e}")
                # Print the full exception, as this could be user error on the
                # formatting function
                traceback.print_exc()
    
    for worker_name, payment_dict in worker_payment_dict.items():
        print(f"{worker_name}:\nAmount: {round(payment_dict['amount'],5)}\n"
            f"Reason: According to our records, you worked on {payment_dict['num_tasks']} tasks, contributed {payment_dict['num_bool_messages']} yes/no answers and {payment_dict['num_text_messages']} complex questions.\n\n")


def main():
    global db
    db = LocalMephistoDB()
    examine_unfinished_results()


if __name__ == "__main__":
    main()
