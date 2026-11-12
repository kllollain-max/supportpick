"""Read-only Threads post insights collector, opt-in and fail-closed.

Uses an existing account token. Does not create posts, modify the publication
ledger, or log token-bearing URLs. API fields can be unavailable; report null.
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

ALLOWED = {"views", "likes", "replies", "reposts", "quotes", "shares"}
POST_ID = re.compile(r"^[0-9]{5,30}$")


def collect(post_id, token, opener=urllib.request.urlopen):
    if not isinstance(post_id, str) or not POST_ID.fullmatch(post_id):
        raise ValueError("valid_post_id_required")
    if not isinstance(token, str) or not token:
        raise ValueError("token_required")
    params = urllib.parse.urlencode({"metric": ",".join(sorted(ALLOWED))})
    url = "https://graph.threads.net/v1.0/" + post_id + "/insights?" + params
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token,
                                               "Accept": "application/json"}, method="GET")
    try:
        with opener(req, timeout=20) as response:
            payload = json.load(response)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, ValueError):
        raise RuntimeError("insights_read_failed_no_post_mutation") from None
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ValueError("invalid_insights_response")
    result = {"views": None, "likes": None, "comments": None,
              "reposts": None, "shares": None, "saves": None,
              "profile_visits": None, "new_followers": None, "site_visits": None}
    aliases = {"replies": "comments"}
    for item in payload["data"]:
        if not isinstance(item, dict) or item.get("name") not in ALLOWED:
            continue
        values = item.get("values")
        if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict):
            continue
        value = values[0].get("value")
        if type(value) is int and value >= 0:
            key = aliases.get(item["name"], item["name"])
            if key in result:
                result[key] = value
    return result


def main():
    post_id = os.environ.get("SUPPORTPICK_THREADS_INSIGHTS_POST_ID", "")
    token = os.environ.get("SUPPORTPICK_THREADS_ACCESS_TOKEN", "")
    print(json.dumps({"post_id": post_id, "metrics": collect(post_id, token)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
