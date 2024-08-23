import json
import pathlib

import html5lib

from local_claude.libs.tools.visit_url_using_user_browser import (
    open_url_with_users_local_browser_and_get_all_content_as_html,
)

from local_claude.libs.tools.save_to_workspace_file import (
    read_file_from_persistent_workspace,
)
from local_claude.libs import directory_utils


def check_is_valid_html(html_content: str) -> bool:
    """
    Validate HTML content using html5lib.

    Note:
        - This method isn't perfect and won't catch all possible HTML errors.
        - It mainly checks if Beautiful Soup can parse the HTML without losing any content
        - Good enough for our use case

    Args:
        html_content (str): The HTML content to validate.

    """
    print("Parsing HTML to ensure it's valid...")
    parser = html5lib.HTMLParser(strict=True)

    # will raise if error, otherwise we parsed successfully
    parser.parse(html_content)


def test_open_url_with_users_local_browser_and_get_all_content_as_html() -> None:

    with directory_utils.temporary_working_directory():

        output_filepath = pathlib.Path("html_content.html")

        # check output filepath doesn't already exist
        assert not output_filepath.exists()

        html_content_from_function_call = (
            open_url_with_users_local_browser_and_get_all_content_as_html(
                url="https://platform.openai.com/docs/guides/function-calling",
                output_filepath=str(output_filepath),
            )
        )

        # choose an arbitrary string from the page that we actually expect to be
        # in there
        expected_string = (
            "In an assistant use case you will typically want to show this response to "
            "the user and let them respond to it"
        )

        assert expected_string in html_content_from_function_call

        # check that the file was written and that it's valid HTML
        html_content_from_file = read_file_from_persistent_workspace(
            filename=str(output_filepath),
        )

        # check contents of file match function call
        assert html_content_from_file == html_content_from_function_call

        # check content of file is valid HTML
        # note: this is useful because often claude will use downstream bs4 HTML parsing via python
        # TODO(b)
        # check_is_valid_html(html_content_from_function_call)
