import contextlib
import tempfile
import os
import json

from local_claude.libs.tools.bash_code_execution import (
    execute_bash_command,
    BashCommandResult,
)
from local_claude.libs.directory_utils import temporary_working_directory


# TODO(bschoen): Check error case, timeout, etc
def test_execute_bash_command() -> None:

    with temporary_working_directory() as tmp_dir:

        # create a file
        example_output_filepath = "test_file.txt"
        with open(example_output_filepath, "w") as file:
            file.write("Hello, World!")

        # check that we can see it
        command = "ls"
        result_json = execute_bash_command(command="ls")

        result = BashCommandResult(**json.loads(result_json))

        print(result)

        assert result.command == command
        assert result.exit_code == 0
        assert example_output_filepath in result.output

        # check we can access the file in this environment
        command = f"cat {example_output_filepath}"
        result_json = execute_bash_command(command=command)

        # load the results dict
        result = BashCommandResult(**json.loads(result_json))

        print(result)

        # check the result
        assert result.command == command
        assert result.exit_code == 0
        assert result.output == "Hello, World!"
