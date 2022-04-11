import boto3
from mephisto.abstractions.providers.mturk.mturk_utils import get_workers_with_qualification
from examples.complex_qa_task.mturk_scripts.constants import *

if IS_SANDBOX:
    endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    qual_id = QUAL_ID_SANDBOX
else:
    endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'
    qual_id = QUAL_ID

client = boto3.client('mturk',
                      region_name='us-east-1', 
                      endpoint_url=endpoint_url)

qualified_workers = get_workers_with_qualification(client=client, qual_id=qual_id, min_score=MIN_SCORE)

for worker in qualified_workers:
    print(worker)
print('TOTAL AMOUNT OF QUALIFIED WORKERS: ' + str(len(qualified_workers)))