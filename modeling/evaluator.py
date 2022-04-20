import argparse
from collections import Counter
import json
import re
import string

parser = argparse.ArgumentParser(description="Computes scores on ComplexQA.")
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
    help="Path to model predictions.",
)


class ComplexQAEvaluator:
    """Computes F1 score and exact match score on ComplexQA.

    This implementation is based upon:
        https://github.com/McGill-NLP/topiocqa/blob/main/evaluate_reader.py
    """
    def __init__(self, gold_file, prediction_file):
        self._gold_file = gold_file
        self._prediction_file = prediction_file
        self.gold_data = self._load_data(self._gold_file)
        self.predictions = self._load_data(self._prediction_file)

    def _load_data(self, data_file):
        with open(data_file, "r") as f:
            examples = json.load(f)

        result = {}
        for example in examples:
            id_ = example["id"]
            answer = example["answer"]
            result[id_] = answer

        return result

    def _normalize_text(self, text):
        regex = re.compile(r"\b(a|an|the)\b", re.UNICODE)
        text = text.lower()
        text = "".join(char for char in text if char not in set(string.punctuation))
        text = re.sub(regex, " ", text)
        text = " ".join(text.split())
        return text

    def _get_tokens(self, text):
        if not text:
            return []
        return self._normalize_text(text).split()

    def _compute_exact_match(self, gold, prediction):
        return int(self._normalize_text(gold) == self._normalize_text(prediction))

    def _compute_f1(self, gold, prediction):
        gold_tokens = self._get_tokens(gold)
        prediction_tokens = self._get_tokens(prediction)
        common = Counter(gold_tokens) & Counter(prediction_tokens)
        num_same = sum(common.values())

        if len(gold_tokens) == 0 or len(prediction_tokens) == 0:
            # If either is no-answer, then F1 is 1 if they agree, 0 otherwise.
            return int(gold_tokens == prediction_tokens)

        if num_same == 0:
            return 0

        precision = 1.0 * num_same / len(prediction_tokens)
        recall = 1.0 * num_same / len(gold_tokens)
        f1 = (2 * precision * recall) / (precision + recall)

        return f1

    def compute_scores(self):
        exact_scores = []
        f1_scores = []
        for id_ in self.gold_data:
            gold = self.gold_data[id_]
            prediction = self.predictions[id_]
            exact_scores.append(self._compute_exact_match(gold, prediction))
            f1_scores.append(self._compute_f1(gold, prediction))

        # Average across examples.
        avg_f1 = (sum(f1_scores) / len(f1_scores)) * 100
        avg_exact = (sum(exact_scores) / len(exact_scores)) * 100

        return avg_f1, avg_exact


if __name__ == "__main__":
    args = parser.parse_args()

    evaluator = ComplexQAEvaluator(args.gold_file, args.prediction_file)
    f1, exact_match = evaluator.compute_scores()

    print(f"F1 Score: {f1:.3f}.")
    print(f"Exact Match Score: {exact_match:.3f}.")
