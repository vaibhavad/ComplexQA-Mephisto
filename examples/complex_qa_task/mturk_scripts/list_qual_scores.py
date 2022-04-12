import boto3
from mephisto.abstractions.providers.mturk.mturk_utils import get_qualification_scores
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

scores = get_qualification_scores(client=client, qual_id=qual_id)

for score in scores:
    print(f"{score[0]}: {score[1]}")