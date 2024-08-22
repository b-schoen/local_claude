import subprocess
import pathlib

from local_claude.libs.tools.bash_code_execution import (
    execute_bash_command,
)

DEFAULT_PYTHON_CODE_GENERATED_FILE_DIRECTORY = pathlib.Path("model_workspace")


# TODO(bschoen): We use a non-temporary file because:
#                - it's easier to debug
#                - it let's the model give it a persistent name
def execute_python_code_and_write_python_code_to_file(
    python_code_to_execute: str,
    filename_for_given_python_code: str,
) -> str:
    """Executes `python_code_to_execute` in a sandboxed python interpreter and returns the `sys.stdout` and `sys.stderror` from executing the code as a string.

    This executes the given `python_code_to_execute` in a sandboxed python interpreter and
    returns to output as if the user had executed it on their terminal.

    MAKE SURE TO EXPLICITLY CALL `print(<variable>)` FOR ANY VARIABLE YOU NEED RETURNED IN YOUR RESULT.

    Use this whenever the result of python code is needed. Example use cases include:
     * The user provides python code that they would like executed
     * The model provides python code and the user would like it executed
     * The model believes python code execution would product results that would help provide a better response, in which case the model will generate the python code itself and pass it to this function.

    Example:

        > assert execute_in_sandboxed_python_interpreter(python_code_to_execute='import math; print(math.sqrt(16))') == '4.0'

    This is the same as if the user had executed the `python_code_to_execute` in their terminal:

        > python -c 'import math; print(math.sqrt(16))'

    Args:
        python_code_to_execute (str): Python code to run inside a sandboxed python interpreter
        filename_for_given_python_code (str): The filename where the given python code is written before execution

    """
    # TODO(bschoen): Does this specifically matter vs just giving an example
    #                using the bash tool?

    # note: we do everything in a `model_workspace` directory as a poor man's sandboxing
    directory = DEFAULT_PYTHON_CODE_GENERATED_FILE_DIRECTORY
    directory.mkdir(exist_ok=True)

    original_filepath = pathlib.Path(filename_for_given_python_code)

    # ex: `/foo/bar.py` -> `/foo/model_workspace/bar.py`
    filepath = str(original_filepath).replace(
        str(original_filepath.stem),
        str(directory / original_filepath.stem),
    )

    print(f"Writing python code to file: {filepath}")

    with open(filepath, "wt") as file:
        file.write(python_code_to_execute)

    return execute_bash_command(command=f"python {filepath}")
