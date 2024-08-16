import contextlib
import tempfile
import os
import json

from local_claude.libs.tools.bash_code_execution import (
    execute_bash_command,
    BashCommandResult,
)


@contextlib.contextmanager
def temporary_working_directory() -> str:
    """

    Creates a temporary working directory and changes to it, resetting the working directory when done.

    This is useful for tests that invoke subproccesses, as we essentially give each a clean working directory.

    We don't just add this to the functions under test as input arguments, since we don't want the model to
    have to worry about this.

    """

    # save the current working directory
    current_dir = os.getcwd()

    # create a temporary directory and change to it
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            os.chdir(tmp_dir)
            yield tmp_dir
        finally:
            # change back to the previous working directory
            os.chdir(current_dir)


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
