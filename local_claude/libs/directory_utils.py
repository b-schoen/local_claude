import contextlib
import tempfile
import os
import pathlib

from local_claude.libs.tools import constants


# TODO(bschoen): We probably don't want to return this, as it shouldn't directly be used
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


# TODO(bschoen): Consolidate explanation somewhere
# TODO(bschoen): Make this a context manager?
def get_current_model_workspace_directory() -> pathlib.Path:
    """Get the current model workspace directory, creating it if it doesn't exist."""

    directory = pathlib.Path(os.getcwd()) / constants.DEFAULT_MODEL_WORKSPACE_DIRECTORY

    directory.mkdir(exist_ok=True)

    return directory
