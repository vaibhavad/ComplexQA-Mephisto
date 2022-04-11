import boto3
import sys
import os


# endpoint_url = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
endpoint_url = "https://mturk-requester.us-east-1.amazonaws.com"

print(f"Deploying to {endpoint_url}.")

thisdir = os.path.dirname(os.path.abspath(__file__))

with open(f"{thisdir}/questions.xml", "r") as f:
    questions = f.read()

with open(f"{thisdir}/answers.xml", "r") as f:
    answers = f.read()

mturk = boto3.client("mturk", region_name="us-east-1", endpoint_url=endpoint_url)

try:
    qual_response = mturk.create_qualification_type(
        Name="Complex QA v0.1.0",
        Keywords="question,answer,complex,dialog,conversation,reasoning",
        Description="This is a brief qualification test showing how to form complex questions from dialogues. You can take it multiple times.",
        QualificationTypeStatus="Active",
        Test=questions,
        AnswerKey=answers,
        RetryDelayInSeconds=0,
        TestDurationInSeconds=30000,
    )

except:
    qual_response = mturk.update_qualification_type(
        QualificationTypeId=input(
            "Qualification already exists. Enter its id to be updated: "
        ),
        Description="This is a brief qualification test showing how to form complex questions from dialogues. You can take it multiple times.",
        QualificationTypeStatus="Active",
        Test=questions,
        AnswerKey=answers,
        RetryDelayInSeconds=0,
        TestDurationInSeconds=30000,
    )

if "sandbox" in endpoint_url:
    print(
        f'https://workersandbox.mturk.com/qualifications/{qual_response["QualificationType"]["QualificationTypeId"]}'
    )
else:
    print(
        f'https://worker.mturk.com/qualifications/{qual_response["QualificationType"]["QualificationTypeId"]}'
    )
