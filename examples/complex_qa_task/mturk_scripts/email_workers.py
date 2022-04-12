import json
import time

from examples.complex_qa_task.mturk_scripts.constants import *
from mephisto.abstractions.providers.mturk.mturk_utils import email_worker

import boto3

if IS_SANDBOX:
    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
else:
    endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

client = boto3.client('mturk',
                      region_name='us-east-1',
                      endpoint_url=endpoint_url)

with open('workers.txt', 'r') as f:
    workers = f.read().splitlines()

subject = "New Tasks in 1 Hours! - Complex Question Creation"
text = open('email_texts/promotional.txt', 'r').read()

for worker in workers:
    try:
        success, message = email_worker(client=client, worker_id=worker, subject=subject, message_text=text)
        if success:
            print(f"Email sent successfully: {worker}")
        else:
            print(f"Email sending failed: {worker}, Error Message: {message}")

    except Exception as e:
        print(f"Email sending failed: {worker}, Error Message: {e}")
        # time.sleep(5)
