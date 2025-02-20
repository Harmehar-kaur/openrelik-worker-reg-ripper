# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess

from openrelik_worker_common.file_utils import create_output_file
from openrelik_worker_common.task_utils import create_task_result, get_input_files

from .app import celery

# Task name used to register and route the task to the correct queue.
TASK_NAME = "openrelik-worker-reg-ripper.tasks.registry"

# Task metadata for registration in the core system.
TASK_METADATA = {
    "display_name": "RegRipper",
    "description": "Registry analysis tool for forensic investigation",
    # Configuration that will be rendered as a web for in the UI, and any data entered
    # by the user will be available to the task function when executing (task_config).
    "task_config": [],
}

logger = get_task_logger(__name__)

@celery.task(bind=True, name=TASK_NAME, metadata=TASK_METADATA)
def command(
    self,
    pipe_result: str = None,
    input_files: list = None,
    output_path: str = None,
    workflow_id: str = None,
    task_config: dict = None,
) -> str:
    """Run <REPLACE_WITH_COMMAND> on input files.

    Args:
        pipe_result: Base64-encoded result from the previous Celery task, if any.
        input_files: List of input file dictionaries (unused if pipe_result exists).
        output_path: Path to the output directory.
        workflow_id: ID of the workflow.
        task_config: User configuration for the task.

    Returns:
        Base64-encoded dictionary containing task results.
    """
    input_files = get_input_files(pipe_result, input_files or [])
    output_files = []

    for input_file in input_files:
        output_file = create_output_file(
            output_path,
            display_name="RegRipper_Output.txt",
            data_type="openrelik:worker:regripper:txt_log",
        )
        command = [
            "wine",
            "/opt/regripper/rip.exe",
            "-r",
            "",
            "-f",
            "sam",
            "-l",
            "-u",
        ]
    logger.debug("Creating temporary directory for RegRipper processing.")
    with TemporaryDirectory(dir=output_path) as temp_dir:
        # Prepare input files
        logger.debug("Copying input registry files for processing.")
        for input_file in input_files:
            filename = os.path.basename(input_file.get("path"))
            target_path = os.path.join(temp_dir, filename)
            os.link(input_file.get("path"), target_path)
            command[2] = target_path  # Set the registry hive file to process

            # Run RegRipper
            logger.debug("Running RegRipper")
            progress_update_interval_in_s: Final[int] = 2
            with open(rip_output.path, "w") as output_file:
                with subprocess.Popen(command, stdout=output_file) as proc:
                    logger.debug("Waiting for RegRipper to finish")
                    while proc.poll() is None:
                        self.send_event("task-progress", data=None)
                        time.sleep(progress_update_interval_in_s)

    # Populate the list of resulting output files.
    logger.debug("Collecting output files")
    if os.stat(rip_output.path).st_size > 0:
        output_files.append(rip_output.to_dict())
        
    return create_task_result(
        output_files=output_files,
        workflow_id=workflow_id,
        command=base_command_string,
        meta={},
    )
