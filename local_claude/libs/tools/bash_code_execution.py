import subprocess
import dataclasses
import json
import os


@dataclasses.dataclass(frozen=True)
class BashCommandResult:
    command: str
    exit_code: int
    output: str  # note: we don't separate stdout and sterr since docker doesn't when streaming


# TODO(bschoen): Common higher level abstraction args like `timeout_in_seconds` are really a property of the workspace, but do I want a shared class here with them?`
def execute_bash_command(command: str) -> str:
    """A tool that executes a bash command in a persistent bash shell and returns the output.

    The persistent bash shell maintains state between commands, including the working directory. This
    can be used for multi-step commands, for example creating a file at one step, then later
    using that file. (ex: `ls -l`, `Hello world`, etc)

    If you encounter a timeout error, you can retry the command with a higher timeout.

    The output will be provided as a json string, containing:
        - command: The bash command that was run.
        - exit_code: The exit code of the command.
        - output: The standard output and error of the command.

    Args:
        command (str): The bash command to execute.

    """
    # Don't check the result, just pass `stdout` and `stderr` to model
    #
    # from docs:
    #
    #   If you wish to capture and combine both streams into one,
    #     - set stdout to PIPE
    #     - stderr to STDOUT
    #     - instead of using capture_output
    #
    DEFAULT_TIMEOUT_IN_SECONDS = 60.0

    result: subprocess.CompletedProcess = subprocess.run(
        command,
        text=True,
        check=False,
        timeout=DEFAULT_TIMEOUT_IN_SECONDS,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )

    # convert result to json dict
    bash_command_result = BashCommandResult(
        command=result.args,
        exit_code=result.returncode,
        output=result.stdout,
    )

    result_json = json.dumps(dataclasses.asdict(bash_command_result))

    return result_json
