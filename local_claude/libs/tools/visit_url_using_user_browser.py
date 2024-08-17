import subprocess
from typing import Any
import json
import re


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


# TODO(bschoen): Full description
def open_url_with_users_local_browser_and_get_all_content_as_html(url: str) -> str:
    """

    Args:
        url (str): _description_

    Returns:
        str: _description_
    """
    page_content = _get_safari_content(url=url)

    # strip down page content
    # TODO(bschoen): Likely want to limit this to max, plus see what we're discarding
    page_content = _extract_text_content(page_content)

    return page_content
