#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.crowdsourcing.utils.worlds import CrowdOnboardWorld, CrowdTaskWorld  # type: ignore
from parlai.core.worlds import validate  # type: ignore
from joblib import Parallel, delayed  # type: ignore


class MultiAgentDialogOnboardWorld(CrowdOnboardWorld):
    def __init__(self, opt, agent):
        super().__init__(opt, agent)
        self.opt = opt

    def parley(self):
        self.agent.agent_id = "Onboarding Agent"
        self.agent.observe({"id": "System", "text": "Welcome onboard!"})
        x = self.agent.act(timeout=self.opt["turn_timeout"])
        self.agent.observe(
            {
                "id": "System",
                "text": "Thank you for your input! Please wait while "
                "we match you with another worker...",
                "episode_done": True,
            }
        )
        self.episodeDone = True


class MultiAgentDialogWorld(CrowdTaskWorld):
    """
    Basic world where each agent gets a turn in a round-robin fashion, receiving as
    input the actions of all other agents since that agent last acted.
    """

    def __init__(self, opt, agents=None, dataloader=None, shared=None):
        # Add passed in agents directly.
        self.agents = agents
        # As we are working with only one agent
        self.agent = agents[0]
        self.dataloader = dataloader
        self.act = None
        self.episodeDone = False
        self.max_turns = opt.get("max_turns", 2)
        self.current_turns = 0
        self.send_task_data = opt.get("send_task_data", False)
        self.opt = opt
        self.agent.agent_id = f"Chat Agent"
    
    def get_message(self, turn=None, turns_remaining=-1, requires_bool=False, provide_more_questions=False):
        if turn:
            return {
                "id": "System",
                "requires_bool_input": requires_bool,
                "provide_more_questions": provide_more_questions,
                "text": " ",
                "question": turn["Question"],
                "answer": turn["Answer"],
                "turn_id": turn["Turn_no"],
                "conv_id": turn["Conversation_no"],
                "turns_remaining": turns_remaining,
                "episode_done": False,
            }
        return {
            "id": "System",
            "requires_bool_input": requires_bool,
            "provide_more_questions": provide_more_questions,
            "text": "",
            "episode_done": False,
        }

    def parley(self):
        conv = self.dataloader.act()
        self.max_turns = len(conv)

        # Display two conversation turns at the start of interaction.
        self.current_turns += 1
        self.agent.observe(self.get_message(conv[0], self.max_turns - 1, requires_bool=True))

        for i, turn in enumerate(conv[1:], start=2):
            self.current_turns += 1
            try:
                self.agent.observe(self.get_message(turn, self.max_turns - i, requires_bool=True))

                self.act = self.agent.act(timeout=self.opt["turn_timeout"])

                if 'boolValue' in self.act and self.act["boolValue"]:
                    self.agent.observe(self.get_message())
                    self.act = self.agent.act(timeout=self.opt["turn_timeout"])
                    if "text" in self.act and len(self.act["text"].strip()) > 0:
                        print(f"COMPLEX QUESTION - {self.act['text']}")

                    provide_more_questions = True
                    while provide_more_questions:
                        self.agent.observe(self.get_message(provide_more_questions=True))
                        self.act = self.agent.act(timeout=self.opt["turn_timeout"])
                        provide_more_questions = self.act["boolValueProvideMoreQuestions"]
                        if provide_more_questions:
                            self.agent.observe(self.get_message())
                            self.act = self.agent.act(timeout=self.opt["turn_timeout"])
                            if "text" in self.act and len(self.act["text"].strip()) > 0:
                                print(f"COMPLEX QUESTION - {self.act['text']}")

                if self.send_task_data:
                    self.act.force_set(
                        "task_data",
                        {
                            "last_acting_agent": self.agent.agent_id,
                            "current_dialogue_turn": self.current_turns,
                            "utterance_count": self.current_turns,
                        },
                    )
            except TypeError:
                self.act = self.agent.act()  # not MTurkAgent
            if self.act["episode_done"]:
                self.episodeDone = True
            if self.current_turns >= self.max_turns:
                self.episodeDone = True

    def prep_save_data(self, agent):
        """Process and return any additional data from this world you may want to store"""
        return {"example_key": "example_value"}

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        """
        Shutdown all mturk agents in parallel, otherwise if one mturk agent is
        disconnected then it could prevent other mturk agents from completing.
        """
        global shutdown_agent

        def shutdown_agent(agent):
            try:
                agent.shutdown(timeout=None)
            except Exception:
                agent.shutdown()  # not MTurkAgent

        Parallel(n_jobs=len(self.agents), backend="threading")(
            delayed(shutdown_agent)(agent) for agent in self.agents
        )


def make_onboarding_world(opt, agent):
    return MultiAgentDialogOnboardWorld(opt, agent)


def validate_onboarding(data):
    """Check the contents of the data to ensure they are valid"""
    print(f"Validating onboarding data {data}")
    return True


def make_world(opt, agents):
    return MultiAgentDialogWorld(opt, agents, dataloader=opt["dataloader"])


def get_world_params():
    return {"agent_count": 1}
