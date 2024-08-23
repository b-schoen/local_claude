import subprocess
import re

from local_claude.libs.tools.save_to_workspace_file import (
    save_content_to_persistent_file_in_workspace,
)


class AppleScriptError(Exception):
    pass


def _run_applescript(script: str) -> str:
    """Run an AppleScript and return its output."""

    # TODO(bschoen): Can we just use `subprocess.run` here?
    process = subprocess.Popen(
        ["osascript", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate(script)

    if stderr:
        raise AppleScriptError(f"AppleScript Error: {stderr}")

    return stdout.strip()


# note: this is the 'less robust' version produced by claude but is saner to understand
def _get_safari_content(url: str, max_wait: int = 30, check_interval: int = 1) -> str:
    script = f"""
    on run
        tell application "Safari"
            set wasRunning to running
            activate
            if (count of windows) = 0 then
                make new document
            end if
            set targetWindow to front window
            tell targetWindow
                set newTab to make new tab with properties {{URL:"{url}"}}
                set current tab to newTab
            end tell
            set startTime to current date
            repeat
                delay {check_interval}
                if (do JavaScript "document.readyState" in newTab) is "complete" then exit repeat
                if ((current date) - startTime) > {max_wait} then
                    error "Page load timeout"
                end if
            end repeat
            
            set pageContent to do JavaScript "document.documentElement.outerHTML" in newTab
            
            close newTab
            if not wasRunning then quit
            
            do shell script "echo " & quoted form of pageContent
        end tell
    end run
    """

    return _run_applescript(script)


def _extract_text_content(html: str) -> str:

    # Remove script and style elements
    script_style_regex = re.compile("<(script|style).*?</\\1>|<[^>]+>", re.DOTALL)
    text = re.sub(script_style_regex, "", html)

    return text.strip()


def _collapse_whitespace(text: str) -> str:
    """
    Replace any combination of newlines and tabs with a single newline,
    collapse multiple spaces into a single space, and strip leading/trailing whitespace.

    Args:
    text (str): The input text to process.

    Returns:
    str: The processed text with collapsed whitespaces and standardized newlines.
    """
    # Replace any combination of newlines and tabs with a single newline
    text = re.sub(r"[\n\t]+", "\n", text)

    # Collapse multiple spaces into a single space
    text = re.sub(r" +", " ", text)

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Collapse patterns of newline followed by spaces
    text = re.sub(r"\n +", "\n", text)

    # Collapse multiple newlines into a single newline
    text = re.sub(r"\n+", "\n", text)

    # Strip leading and trailing whitespace
    return text.strip()


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
