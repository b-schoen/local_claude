# TODO(bschoen): Each tool in separate file?


def search_google(query):
    url = "https://www.google.com/search?q=" + query
    webbrowser.open(url)


def open_url_with_users_local_browser_and_get_all_content_as_html():
    url = "https://www.google.com"
    webbrowser.open(url)
