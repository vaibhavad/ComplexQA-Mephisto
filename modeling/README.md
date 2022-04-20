# ComplexQA-Modeling
## Install
```bash
git clone git@github.com:ncmeade/ComplexQA-Modeling.git
cd ComplexQA-Modeling
pip install -e .
```

## GPT-3 Results
To get the GPT-3 scores, run:
```bash
# Set this variable to your secret key.
export OPENAI_API_KEY=<key>

python gpt3_runner.py --gold_file ./data.json --prediction_file ./prediction.json
python evaluator.py --gold_file ./data.json --prediction_file ./prediction.json
```
