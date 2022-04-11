import json
import time

from mephisto.abstractions.providers.mturk.mturk_utils import get_mailable_workers
from examples.complex_qa_task.mturk_scripts.constants import *

import boto3

if IS_SANDBOX:
    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
else:
    endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

client = boto3.client('mturk',
                      region_name='us-east-1',
                      endpoint_url=endpoint_url)

workers = get_mailable_workers(client)

with open('workers-temp.txt', 'w') as f:
    for worker in workers:
        f.write(worker + '\n')
