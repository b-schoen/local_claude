import contextlib
import tempfile
import os
import json

from local_claude.libs.tools.bash_code_execution import (
    execute_bash_command,
    BashCommandResult,
)
from local_claude.libs.tools.save_to_workspace_file import (
    save_content_to_persistent_file_in_workspace,
)
from local_claude.libs import directory_utils


# TODO(bschoen): Check error case, timeout, etc
def test_execute_bash_command() -> None:

    with directory_utils.temporary_working_directory() as tmp_dir:

        # create a file
        save_content_to_persistent_file_in_workspace(
            filename="test_file.txt",
            content="Hello, World!",
        )

        # check that we can see it
        command = "ls"
        result_json = execute_bash_command(command="ls")

        result = BashCommandResult(**json.loads(result_json))

        print(result)

        assert result.command == command
        assert result.exit_code == 0
        assert "test_file.txt" in result.output

        # check we can access the file in this environment
        command = f"cat test_file.txt"
        result_json = execute_bash_command(command=command)

        # load the results dict
        result = BashCommandResult(**json.loads(result_json))

        print(result)

        # check the result
        assert result.command == command
        assert result.exit_code == 0
        assert result.output == "Hello, World!"
