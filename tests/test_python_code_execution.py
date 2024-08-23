import contextlib
import tempfile
import os
import json

from local_claude.libs.tools import constants
from local_claude.libs.tools.python_code_execution import (
    execute_python_code_and_write_python_code_to_file,
)
from local_claude.libs.tools.bash_code_execution import BashCommandResult
from local_claude.libs import directory_utils
from local_claude.libs.tools.save_to_workspace_file import (
    read_file_from_persistent_workspace,
)


# TODO(bschoen): Check error case, timeout, etc
def test_execute_python_code_and_write_python_code_to_file() -> None:

    with directory_utils.temporary_working_directory() as tmp_dir:

        python_code_to_execute = (
            "values = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]\n\nprint(sorted(values))"
        )

        filename_for_given_python_code = "test_file.py"

        result_json = execute_python_code_and_write_python_code_to_file(
            python_code_to_execute=python_code_to_execute,
            filename_for_given_python_code=filename_for_given_python_code,
        )

        result = BashCommandResult(**json.loads(result_json))

        # check we used the file to execute the python code
        assert result.command == "python " + filename_for_given_python_code
        assert result.exit_code == 0
        assert result.output == "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n"

        # check `filename_for_given_python_code` now contains `python_code_to_execute`
        file_contents = read_file_from_persistent_workspace(
            filename_for_given_python_code
        )

        assert file_contents.strip() == python_code_to_execute.strip()
