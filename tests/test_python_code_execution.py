import contextlib
import tempfile
import os
import json

from local_claude.libs.tools.python_code_execution import (
    execute_python_code_and_write_python_code_to_file,
    DEFAULT_PYTHON_CODE_GENERATED_FILE_DIRECTORY,
)
from local_claude.libs.tools.bash_code_execution import BashCommandResult
from local_claude.libs.directory_utils import temporary_working_directory


# TODO(bschoen): Check error case, timeout, etc
def test_execute_python_code_and_write_python_code_to_file() -> None:

    with temporary_working_directory() as tmp_dir:

        python_code_to_execute = (
            "values = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]\n\nprint(sorted(values))"
        )

        filename_for_given_python_code = tmp_dir + "/test_file.py"

        # actual filepath used
        filepath_used_for_python_code = filename_for_given_python_code.replace(
            "/test_file.py",
            f"/{DEFAULT_PYTHON_CODE_GENERATED_FILE_DIRECTORY}/test_file.py",
        )

        result_json = execute_python_code_and_write_python_code_to_file(
            python_code_to_execute=python_code_to_execute,
            filename_for_given_python_code=filename_for_given_python_code,
        )

        result = BashCommandResult(**json.loads(result_json))

        # check we used the file to execute the python code
        assert result.command == "python " + filepath_used_for_python_code
        assert result.exit_code == 0
        assert result.output == "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n"

        # check `filename_for_given_python_code` now contains `python_code_to_execute`
        with open(filepath_used_for_python_code, "r") as file:
            file_contents = file.read()

        assert file_contents.strip() == python_code_to_execute.strip()
