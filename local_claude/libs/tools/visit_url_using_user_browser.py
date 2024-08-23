import subprocess
import re
import json

import bs4

from local_claude.libs.tools.save_to_workspace_file import (
    save_content_to_persistent_file_in_workspace,
)


class AppleScriptError(Exception):
    pass


def _run_applescript(script: str) -> str:
    """Run an AppleScript and return its output."""
    try:
        result = subprocess.run(
            ["osascript", "-s", "s"],  # '-s s' for strict compilation
            input=script,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:

        error_message = (
            "Note: Sometimes when this fails, need to take safari "
            "out of full screen and back, then works "
            "again for a while, TODO(bschoen) to understand why. "
        )

        error_message += f"AppleScript Error: {e.stderr.strip()}"

        if e.stdout:
            error_message += f"\nOutput: {e.stdout.strip()}"

        # printed so we can easily copy into script editor,
        # as otherwise failing in pytest prefixes every line with `E`
        print(f"\nScript: {script}")

        raise AppleScriptError(error_message)


# note: this is the 'less robust' version produced by claude but is saner to understand
def _get_safari_content(url: str, max_wait: int = 30, check_interval: int = 1) -> str:
    script = f"""
    on run
        set log_messages to {{}}
        
        try
            tell application "Safari"
                set log_messages to log_messages & "Safari activated"
                activate
                
                if (count of windows) = 0 then
                    make new document
                    set log_messages to log_messages & "New document created"
                end if
                
                set targetWindow to front window
                set log_messages to log_messages & "Target window set"
                
                set currentURL to URL of current tab of targetWindow
                set log_messages to log_messages & ("Current URL: " & currentURL)
                
                -- Try to create a new tab, fall back to using current tab if it fails
                try
                    set newTab to make new tab at end of tabs of targetWindow with properties {{URL:"{url}"}}
                    set log_messages to log_messages & "New tab created"
                on error createTabError
                    set log_messages to log_messages & ("Error creating new tab: " & createTabError)
                    set newTab to current tab of targetWindow
                    set URL of newTab to "{url}"
                    set log_messages to log_messages & "Using current tab"
                end try
                
                set current tab of targetWindow to newTab
                set log_messages to log_messages & "Current tab set"
                
                set startTime to current date
                repeat
                    delay {check_interval}
                    set currentURL to URL of newTab
                    set log_messages to log_messages & ("Current URL: " & currentURL)
                    if currentURL starts with "{url}" then
                        try
                            if (do JavaScript "document.readyState" in newTab) is "complete" then
                                set log_messages to log_messages & "Page loaded"
                                exit repeat
                            end if
                        on error jsError
                            set log_messages to log_messages & ("JavaScript error: " & jsError)
                        end try
                    end if
                    if ((current date) - startTime) > {max_wait} then
                        set log_messages to log_messages & "Page load timeout"
                        error "Page load timeout"
                    end if
                end repeat
                
                set pageContent to do JavaScript "document.documentElement.outerHTML" in newTab
                set log_messages to log_messages & "Content retrieved"
                
                return pageContent & "
" & (log_messages as string)
            end tell
        on error errorMessage
            set log_messages to log_messages & ("Error: " & errorMessage)
            error errorMessage & "
" & (log_messages as string)
        end try
    end run
    """

    return _run_applescript(script)


def _extract_text_content(html: str) -> str:
    # Parse the HTML using BeautifulSoup
    soup = bs4.BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for element in soup(["script", "style"]):
        element.decompose()

    # Remove comments
    for comment in soup.find_all(text=lambda text: isinstance(text, bs4.Comment)):
        comment.extract()

    # Convert the modified soup back to a string
    clean_html = str(soup)

    return clean_html.strip()


def _collapse_whitespace(html: str) -> str:
    """
    Collapse multiple whitespace characters within HTML tags to a single space,
    and standardize newlines between tags.
    """
    # Collapse whitespace within tags
    html = re.sub(r">(\s+)<", "> <", html)

    # Standardize newlines between tags
    html = re.sub(r">\s*\n+\s*<", ">\n<", html)

    # Remove leading and trailing whitespace
    return html.strip()


# TODO(bschoen): Full description
def open_url_with_users_local_browser_and_get_all_content_as_html(
    url: str,
    output_filepath: str = "default_output_filepath_open_url_with_users_local_browser_and_get_all_content_as_html.html",
) -> str:
    """
    Open url with user's local browser and get all content as html.

    Use this whenever you want to visit a link. This is especially useful
    when used on the results of the `search_google_and_return_list_of_results`, as
    it can get the content of the `link` field.

    Together with `search_google_and_return_list_of_results`, these two tools allow
    you to browse the web just like a human would, an incredibly powerful tool.

    The results are returned to you as a string and written to the file `output_filepath`,
    which is useful to pass onto other tools like `execute_python_code_and_write_python_code_to_file`.

    Args:
        url (str): URL to open in the user's browser.
        output_filepath (str): The filename to save the html content to. This is useful for passing the content to other tools.
    """
    page_content = _get_safari_content(url=url)

    # strip down page content
    # TODO(bschoen): Likely want to limit this to max, plus see what we're discarding
    page_content = _extract_text_content(page_content)

    # collapse whitespace, otherwise HTML has insane number of newline and tab tokens, like 50-100 between headings
    page_content = _collapse_whitespace(page_content)

    # save the content to a file, so claude can do things like parsing it in python
    # for more complex operations
    if output_filepath:
        save_content_to_persistent_file_in_workspace(
            filename=output_filepath,
            content=page_content,
        )

    return page_content
