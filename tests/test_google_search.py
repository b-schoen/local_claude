import json
import dataclasses

from local_claude.libs.tools.google_search import (
    SearchResult,
    search_google_and_return_list_of_results,
)


def test_search_google_and_return_list_of_results() -> None:

    result = search_google_and_return_list_of_results(
        search_query="OpenAI function calling"
    )

    search_results = [SearchResult(**x) for x in json.loads(result)]

    assert len(search_results) > 0

    for result in search_results:
        print(json.dumps(dataclasses.asdict(result), indent=2))
