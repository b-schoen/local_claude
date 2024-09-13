from local_claude.libs.tools.save_to_workspace_file import (
    save_content_to_persistent_file_in_workspace,
    read_file_from_persistent_workspace,
)
from local_claude.libs import directory_utils

import pytest


def test_read_and_write_to_workspace() -> None:

    with directory_utils.temporary_working_directory() as tmp_dir:

        filename = "test_file.txt"
        content = "Hello, World!"

        # check first that reading fails if the file doesn't exist
        # (and that the file doesn't exist)
        with pytest.raises(FileNotFoundError):
            read_file_from_persistent_workspace(filename=filename)

        # create a file
        save_content_to_persistent_file_in_workspace(
            filename=filename,
            content=content,
        )

        # check successfully wrote it
        content_from_file = read_file_from_persistent_workspace(filename=filename)

        # and that it matches the original content
        assert content == content_from_file
