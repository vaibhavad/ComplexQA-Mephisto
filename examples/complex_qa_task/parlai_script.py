#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import task_script
from mephisto.operations.hydra_config import build_default_task_config
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import (
    BLUEPRINT_TYPE_PARLAI_CHAT,
    SharedParlAITaskState,
)
from mephisto.operations.data_loader import TopiOCQAQADataLoader

from omegaconf import DictConfig
from dataclasses import dataclass, field

@dataclass
class DataLoaderConfig:
    module_name: str = field(
        default="",
        metadata={"help": ""}
    )
    class_name: str = field(
        default="",
        metadata={"help": ""}
    )
    datapath: str = field(
        default="",
        metadata={"help": ""}
    )
    num_turns: int = field(
        default=10,
        metadata={"help": ""}
    )


@dataclass
class ParlAITaskConfig(build_default_task_config("example")):  # type: ignore
    num_turns: int = field(
        default=3,
        metadata={"help": "Number of turns before a conversation is complete"},
    )
    turn_timeout: int = field(
        default=300,
        metadata={
            "help": "Maximum response time before kicking "
            "a worker out, default 300 seconds"
        },
    )
    dataloader: DataLoaderConfig = DataLoaderConfig()


@task_script(config=ParlAITaskConfig)
def main(operator: "Operator", cfg: DictConfig) -> None:

    world_opt = {"num_turns": cfg.num_turns, "turn_timeout": cfg.turn_timeout}

    custom_bundle_path = cfg.mephisto.blueprint.get("custom_source_bundle", None)
    if custom_bundle_path is not None:
        assert os.path.exists(custom_bundle_path), (
            "Must build the custom bundle with `npm install; npm run dev` from within "
            f"the {cfg.task_dir}/webapp directory in order to demo a custom bundle "
        )
        world_opt["send_task_data"] = True
    
    data_opt = cfg.dataloader
    dataloader = TopiOCQAQADataLoader(data_opt)
    world_opt["dataloader"] = dataloader

    shared_state = SharedParlAITaskState(
        world_opt=world_opt, onboarding_world_opt=world_opt
    )

    shared_state.mturk_specific_qualifications = [
    {
        "QualificationTypeId": "00000000000000000040",
        "Comparator": "GreaterThanOrEqualTo",
        "IntegerValues": [cfg.mephisto.task.minimum_hits_done],
        "ActionsGuarded": "DiscoverPreviewAndAccept",
    },
    {
        "QualificationTypeId": "000000000000000000L0",
        "Comparator": "GreaterThanOrEqualTo",
        "IntegerValues": [cfg.mephisto.task.minimum_acceptance_rate],
        "ActionsGuarded": "DiscoverPreviewAndAccept",
    }]

    task_qualification_type_id = None
    if cfg.mephisto.provider._provider_type == 'mturk':
        task_qualification_type_id = cfg.mephisto.task.qualification
    else:
        task_qualification_type_id = cfg.mephisto.task.qualification_sandbox

    if task_qualification_type_id is not None:
        shared_state.mturk_specific_qualifications.append(
        {
            "QualificationTypeId": task_qualification_type_id,
            "Comparator": "GreaterThanOrEqualTo",
            "IntegerValues": [cfg.mephisto.task.minimum_qual_score],
            "ActionsGuarded": "Accept",
        })

    operator.launch_task_run(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)


if __name__ == "__main__":
    main()
