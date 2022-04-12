from dataclasses import dataclass
import json
import random

class TopiOCQAQADataLoader():
    
    def __init__(self, opt, shared=None):
        self.data = None
        with open (opt.datapath) as f:
            self.data = json.load(f)
        self.num_of_convs = self.data[-1]["Conversation_no"]
        self.num_turns = opt.num_turns

    def act(self):
        idx = random.randrange(1, self.num_of_convs)
        data = []
        for turn in self.data:
            if turn["Conversation_no"] == idx:
                data.append(turn)
        return data[:self.num_turns]

    def get(self, conv_id=1, turn_id=1):
        for turn in self.data:
            if turn["Conversation_no"] == conv_id and turn["Turn_no"] == turn_id:
                return turn
        return None
