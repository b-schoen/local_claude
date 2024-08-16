import contextlib
import tempfile
import os


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
