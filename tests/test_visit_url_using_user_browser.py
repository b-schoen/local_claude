import json

from local_claude.libs.tools.visit_url_using_user_browser import (
    open_url_with_users_local_browser_and_get_all_content_as_html,
)


def test_open_url_with_users_local_browser_and_get_all_content_as_html() -> None:

    result = open_url_with_users_local_browser_and_get_all_content_as_html(
        url="https://platform.openai.com/docs/guides/function-calling",
    )

    # choose an arbitrary string from the page that we actually expect to be
    # in there
    expected_string = (
        "In an assistant use case you will typically want to show this response to "
        "the user and let them respond to it"
    )

    assert expected_string in result
