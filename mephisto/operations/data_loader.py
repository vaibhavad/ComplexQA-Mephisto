from dataclasses import dataclass
import json
import random

class TopiOCQAQADataLoader():
    
    def __init__(self, opt, shared=None):
        self.data = {}
        with open (opt.datapath) as f:
            data = json.load(f)
        for turn in data:
            if turn["Conversation_no"] not in self.data:
                self.data[turn["Conversation_no"]] = []
            self.data[turn["Conversation_no"]].append(turn)
        self.conv_ids = list(self.data.keys())
        random.shuffle(self.conv_ids)
        self.current_conv_id_index = 0
        self.num_turns = opt.num_turns

    def act(self):
        idx = self.current_conv_id_index
        self.current_conv_id_index += 1
        if self.current_conv_id_index >= len(self.conv_ids):
            self.current_conv_id_index = 0
        
        conv_id = self.conv_ids[idx]
        conv = self.data[conv_id]
        return conv[:self.num_turns]

    def get(self, conv_id=1, turn_id=1):
        for turn in self.data:
            if turn["Conversation_no"] == conv_id and turn["Turn_no"] == turn_id:
                return turn
        return None
