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
BONUS_AMOUNT = 1.0


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
    total_bonus_amount = round(total_bonus_amount, 5)
    bonus_message = f"Hi {worker_name},\n\nYou have received a bonus of ${total_bonus_amount} for completing assignment {assignment_id}. In this assignment you provided {num_bool_messages} yes/no answers and {num_text_messages} complex questions. Thank you for participating in our tasks! \n\nBest,\nQA Research"
    return total_bonus_amount, bonus_message


def format_for_printing_data(data):
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
    complex_questions = 0
    for message in messages:
        if message["id"] == 'System' and 'question' in message and 'answer' in message:
            output_string += f"\nQuestion: {message['question']}\nAnswer: {message['answer']}\n"
        elif message["id"] == 'Chat Agent' and "text" in message:
            complex_questions += 1
            output_string += f"Complex Question: {message['text']}\n"
    if complex_questions > 0:
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
                print(formatted + '\n\n')
                print("Worker name: " + worker.worker_name)
                print("task amount (Bonus + base pay): " + str(calculate_task_bonus_from_data(data)[0] + 0.01))

            except Exception as e:
                print(f"Unexpected error formatting data for {unit}: {e}")
                # Print the full exception, as this could be user error on the
                # formatting function
                traceback.print_exc()

            







def main():
    global db
    db = LocalMephistoDB()
    examine_unfinished_results()


if __name__ == "__main__":
    main()
