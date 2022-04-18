#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from email import message
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.examine_utils import run_examine_or_review, print_results
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit
import json

db = None

QUAL_ID_SANDBOX = '3QG4W3BIFAZMGUY838Z4EKY6FWDWNM'
QUAL_ID = '3DA2M59FD03MKSVQ6KIPVI7Q8Y2RXF'
BONUS_AMOUNT = 1.0

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


def calculate_qual_bonus(worker):
    worker_name = worker.worker_name
    if 'sandbox' in worker.provider_type:
        qualification_id = QUAL_ID_SANDBOX
    else:
        qualification_id = QUAL_ID
    
    bonus_message = f"Hi {worker_name},\n\nYou have received a bonus of ${BONUS_AMOUNT} for passing the qualification test {qualification_id} and submitting a HIT. Thank you for participating in our tasks!\n\nBest,\nQA Research"
    return BONUS_AMOUNT, bonus_message, f"{worker_name}_{qualification_id}"

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
            output_string += f"Complex Question: {message['text']}\n"
            final_data.append({
                "question": message['text'],
                "answer": latest_answer,
                "conversation_no": conv_id,
                "turn_no": turn_id
            })

    with open("final_complex_dataset.json", "w") as f:
        json.dump(final_data, f, indent=4)

    return f"-------------------\n{metadata_string}{output_string}"


def main():
    global db
    db = LocalMephistoDB()
    run_examine_or_review(db, format_for_printing_data, \
        calculate_task_bonus_from_data, calculate_qual_bonus)


if __name__ == "__main__":
    main()