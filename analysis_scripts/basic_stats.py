import json

DATASET_FILE = "final_complex_dataset.json"
HOTPOTQA_FILE = "hotpotqa_data.json"

def main():

    with open(DATASET_FILE, "r") as f:
        data = json.load(f)
    
    with open(HOTPOTQA_FILE, "r") as f:
        hotpot = json.load(f)
    
    unique_convs = set()
    for unit in data:
        unique_convs.add(unit["conversation_no"])
    
    print("Number of conversations:", len(unique_convs))
    print("Number of questions:", len(data))

    num_question_tokens = []
    num_answer_tokens = []

    for unit in data:
        num_question_tokens.append(len(unit["question"].split()))
        num_answer_tokens.append(len(unit["answer"].split()))
    
    print("Average number of question tokens:", sum(num_question_tokens) / len(num_question_tokens))
    print("Average number of answer tokens:", sum(num_answer_tokens) / len(num_answer_tokens))

    num_question_tokens = []
    num_answer_tokens = []

    for unit in hotpot:
        num_question_tokens.append(len(unit["question"].split()))
        num_answer_tokens.append(len(unit["answer"].split()))
    
    print("Average number of question tokens (hotpotqa):", sum(num_question_tokens) / len(num_question_tokens))
    print("Average number of answer tokens (hotpotqa):", sum(num_answer_tokens) / len(num_answer_tokens))



if __name__ == "__main__":
    main()