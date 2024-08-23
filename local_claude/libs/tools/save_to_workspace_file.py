import pathlib

from local_claude.libs import directory_utils


def _check_filepath_is_filename(filename: str) -> None:
    # check that it's a filename, not a path, since it makes dealing with tests easier,
    # and model doesn't need nested paths right now
    if pathlib.Path(filename).name != filename:
        raise ValueError(
            "`filename` argument must be a filename, " 'not a path (ex: "file.txt")'
        )

    return None


# TODO(bschoen): Is the name content throwing it off? It keeps forgetting to pass the actual content in full
def save_content_to_persistent_file_in_workspace(filename: str, content: str) -> None:
    """Save arbitrary content to the specified filename in the model's workspace.

    The model's workspace is accessible by all tools and persistent over the lifetime of the conversation.

    This function is often useful for passing arbitrary data to `execute_python_code_and_write_python_code_to_file` or `execute_bash_command`.

    USE THIS FUNCTION TO PASS ACTUAL DATA INSTEAD OF PLACEHOLDERS.

    For example:

        # say the user wants to get all the content from a link, and we want to then parse that with python
        html_content = open_url_with_users_local_browser_and_get_all_content_as_html(url=<some_user_specified_url>)

        # save the html content to a file
        save_content_to_persistent_file_in_workspace("html_context.txt", content=html_content)

        # now we can pass the file easy to `execute_python_code_and_write_python_code_to_file`
        parsed_result = execute_python_code_and_write_python_code_to_file(
            python_code_to_execute='''
                from bs4 import BeautifulSoup

                with open("html_context.txt", "r") as file:
                    html_content = file.read()

                soup = BeautifulSoup(html_content, "html.parser")
                # do something with the soup...
            ''',
            filename_for_given_python_code="html_parser.py",
        )

    Args:
        filename (str): The filename to save the content to.
        content (str): The content to save to the file.
    """
    # check inputs
    _check_filepath_is_filename(filename)

    filepath = directory_utils.get_current_model_workspace_directory() / pathlib.Path(
        filename
    )

    with open(filepath, "wt") as file:
        file.write(content)


# Note: Claude is usually smart enough to use the `ls` bash command to write a file
def read_file_from_persistent_workspace(filename: str) -> str:
    """Read the entirety of the given file as text.

    If the user asks to read a file, or a file comes from another tool use, you can use this function
    to read all data from the file.

    Args:
        filename (str): The filename to read the data from. This will often be either supplied by the user or produced by another tool.

    Returns:
        str: All data in the file as a string

    """

    # check inputs
    _check_filepath_is_filename(filename)

    filepath = directory_utils.get_current_model_workspace_directory() / pathlib.Path(
        filename
    )

    return filepath.read_text()
