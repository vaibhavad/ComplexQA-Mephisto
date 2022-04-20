import argparse
import json
import os
import random

import openai
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Gets GPT-3 predictions for ComplexQA.")
parser.add_argument(
    "--gold_file",
    action="store",
    type=str,
    required=True,
    help="Path to the ComplexQA dataset.",
)
parser.add_argument(
    "--prediction_file",
    action="store",
    type=str,
    required=True,
    help="Path to write GPT-3 predictions to.",
)
parser.add_argument(
    "--prompt_type",
    action="store",
    type=str,
    choices=["zero", "few"],
    required=True,
    help="Whether to use zero-shot or few-shot prompt.",
)


class _ComplexQAExample:
    def __init__(
        self, id_: int, question: str, answer: str, conversation_no: int, turn_no: int
    ):
        self.id_ = id_
        self.question = question
        self.answer = answer
        self.conversation_no = conversation_no
        self.turn_no = turn_no


class _GPT3Runner:
    def __init__(self, data, prompt_type="zero"):
        self._data = data
        self._prompt_type = prompt_type

    def __call__(self):
        results = []
        for example in tqdm(self._data, desc="Collecting GPT-3 continuations"):
            results.append(
                {"id": example.id_, "prediction": self.get_prediction(example)}
            )
        return results

    def get_prediction(self, example):
        # Create zero-shot or few-shot prompt.
        prompt = self._create_prompt(example)

        # Factual answering: https://beta.openai.com/examples/default-factual-answering
        # Only samples one completion.
        return openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            temperature=0,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )["choices"][0]["text"]

    def _create_prompt(self, example):
        if self._prompt_type == "zero":
            return f"Q: {example.question}\nA:"

        else:
            # To avoid including the answer to the example as input.
            population = [x for x in self._data if x.id_ != example.id_]

            # Create few-shot prompt.
            sample = random.sample(population, k=5)
            prompt = "\n\n".join([f"Q: {x.question}\nA: {x.answer}" for x in sample])
            prompt += f"\n\nQ: {example.question}\nA:"
            return prompt


if __name__ == "__main__":
    args = parser.parse_args()

    # Load the dataset.
    with open(args.gold_file, "r") as f:
        data = json.load(f)

    examples = [
        _ComplexQAExample(
            id_=x["id"],
            question=x["question"],
            answer=x["answer"],
            conversation_no=x["conversation_no"],
            turn_no=x["turn_no"],
        )
        for x in data
    ]

    # Collect predictions from GPT-3.
    runner = _GPT3Runner(examples, prompt_type=args.prompt_type)
    predictions = runner()

    with open(args.prediction_file, "w") as f:
        json.dump(predictions, f)
