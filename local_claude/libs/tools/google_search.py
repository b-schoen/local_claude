import os
import json
import dataclasses

import serpapi


@dataclasses.dataclass(frozen=True)
class SearchResult:
    """
    Results of Serp API search, specifically just an item in `organic_results` for now.

    Ex: (showing all fields)

        {
            "position": 1,
            "title": "Function Calling",
            "link": "https://platform.openai.com/docs/guides/function-calling",
            "redirect_link": "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://platform.openai.com/docs/guides/function-calling&ved=2ahUKEwiejI_E2fqHAxVYL0QIHQ2GBaQQFnoECAgQAQ&usg=AOvVaw0-tot91fwDE_BSmPiKyF5b",
            "displayed_link": "https://platform.openai.com › docs › guides › function-...",
            "favicon": "https://serpapi.com/searches/66bfe54bfab27390aa461509/images/4f4c0a71ab51a8370e9bb6d10f3a27533fb23b7deec83ab81d6fa0bdb41278d1.png",
            "snippet": "Function calling allows you to connect models like gpt-4o to external tools and systems. This is useful for many things such as empowering AI assistants ...",
            "snippet_highlighted_words": [
                "Function calling"
            ],
            "source": "OpenAI"
        }

        -->

        {
            "position": 1,
            "title": "Function Calling",
            "link": "https://platform.openai.com/docs/guides/function-calling",
            "displayed_link": "https://platform.openai.com \u203a docs \u203a guides \u203a function-...",
            "snippet": "Function calling allows you to connect models like gpt-4o to external tools and systems. This is useful for many things such as empowering AI assistants ...",
            "snippet_highlighted_words": [
                "Function calling"
            ],
            "source": "OpenAI"
        }

    """

    position: int
    title: str
    link: str
    displayed_link: str
    snippet: str
    snippet_highlighted_words: list[str]
    source: str


# TODO(bschoen): Just have a wrapper that does this dict conversion, since it loses so much information (or just have internal underscore function, but that can be confusing to users)
# TODO(bschoen): Mention in description that often used with visit url in browser tool
# TODO(bschoen): We can actually return a list to claude
def search_google_and_return_list_of_results(search_query: str) -> str:
    """
    Search Google and return the first page of results.

    Useful any time the user needs information from the web. You will usually need to use
    `open_url_with_users_local_browser_and_get_all_content_as_html` on the `link` field of
    whatever result you want.

    Returns a list of dictionary objects, each representing a search result.

    Each search result contains:
        - position: The position of the search result on the page (ex: 1, 2, 3, etc).
        - title: Title of the linked content (ex: "Function Calling")
        - link: The actual link to visit to get the content (ex: "https://platform.openai.com/docs/guides/function-calling")
        - displayed_link: Link normally shown to user (ex: "https://platform.openai.com › docs › guides › function-...")
        - snippet: Snippet of the result's content (ex: "Function calling allows you to connect models like gpt-4o to external tools and systems")
        - snippet_highlighted_words: The primary words in the result content causing this to be selected as relevant (ex: ['Function calling'])
        - source: Where this result comes from (ex: "OpenAI")

    Args:
        search_query (str): String to use as the google search query (equivalent to typing it into the search bar in a browser).

    """

    search = serpapi.GoogleSearch(
        {
            "q": search_query,
            "location": "United States",
            "hl": "en",
            "gl": "us",
            # TODO(bschoen): Expose this as a model param?
            # "num": "Number of Results",
            "google_domain": "google.com",
            "api_key": os.environ["SERP_API_KEY"],
        }
    )

    # TODO(bschoen): Probably just want to return `organic_results`
    # TODO(bschoen): Related questions could be helpful
    results = search.get_dict()

    # take only the fields we want from organic results
    parsed_search_results: list[SearchResult] = []
    desired_search_result_fields = [x.name for x in dataclasses.fields(SearchResult)]

    for organic_result in results["organic_results"]:

        parsed_search_results.append(
            SearchResult(
                **{
                    k: v
                    for k, v in organic_result.items()
                    if k in desired_search_result_fields
                }
            )
        )

    # convert to json string for returning
    parsed_search_results_as_json = json.dumps(
        [dataclasses.asdict(x) for x in parsed_search_results], indent=2
    )

    return parsed_search_results_as_json
