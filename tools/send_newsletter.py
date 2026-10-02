"""Emails a newsletter article (from newsletter/articles.json) to subscribers through Kit.

  python3 tools/send_newsletter.py <slug>           # create a Kit draft, send nothing
  python3 tools/send_newsletter.py <slug> --test    # send now to the "Test send (Jack only)" tag
  python3 tools/send_newsletter.py <slug> --all     # send now to every subscriber

Publish the article on the site (build + push) before sending, so the
"read on the website" link and images resolve. API key: ~/.kit/credentials.json
"""
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build import ROOT, SITE_URL, SITE_NAME, ADDRESS  # noqa: E402

API = "https://api.kit.com/v4"
TEST_TAG_ID = 24221697  # "Test send (Jack only)" -> jackryanandersoniii@gmail.com


def kit(method, path, body=None):
    # curl rather than urllib: python.org Python on this Mac has no CA certificates.
    key = json.load(open(os.path.expanduser("~/.kit/credentials.json")))["api_key"]
    cmd = ["curl", "-sS", "--fail-with-body", "-X", method, API + path, "-H", f"X-Kit-Api-Key: {key}",
           "-H", "Content-Type: application/json", "-H", "Accept: application/json"]
    if body is not None:
        cmd += ["--data-binary", "@-"]
    r = subprocess.run(cmd, input=json.dumps(body) if body is not None else None,
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"Kit API error: {r.stdout or r.stderr}")
    return json.loads(r.stdout or "{}")


def email_html(a):
    url = f"{SITE_URL}newsletter/{a['slug']}.html"
    base = f"{SITE_URL}newsletter/"
    body = re.sub(r'src="(?!https?:)([^"]+)"', lambda m: f'src="{base}{m.group(1)}"', a["body"])
    body = re.sub(r'href="(?!https?:|mailto:|#)([^"]+)"', lambda m: f'href="{base}{m.group(1)}"', body)
    body = body.replace('loading="lazy"', 'style="max-width:100%;height:auto"')
    return f"""<h1>{html.escape(a['title'])}</h1>
{body}
<p><a href="{url}">Read this on our website</a></p>
<p>Jack Anderson<br>{SITE_NAME}<br>{ADDRESS}</p>"""


def preview_text(a):
    text = re.sub(r"<[^>]+>", " ", a["body"])
    return " ".join(html.unescape(text).split())[:140]


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    slug, mode = args[0], (args[1] if len(args) > 1 else "--draft")
    a = next((x for x in json.load(open(os.path.join(ROOT, "newsletter", "articles.json"))) if x["slug"] == slug), None)
    if not a:
        sys.exit(f"No article with slug {slug!r}")

    if mode == "--test":
        filt = [{"all": [{"type": "tag", "ids": [TEST_TAG_ID]}], "any": None, "none": None}]
        subject = "[TEST] " + a["title"]
    elif mode in ("--all", "--draft"):
        filt = [{"all": [{"type": "all_subscribers"}], "any": None, "none": None}]
        subject = a["title"]
    else:
        sys.exit(f"Unknown option {mode}")

    payload = {"subject": subject, "content": email_html(a), "description": a["title"],
               "preview_text": preview_text(a), "public": False, "published_at": None,
               "send_at": None, "subscriber_filter": filt}
    # Always create as an unsent draft first and check who it is addressed to.
    b = kit("POST", "/broadcasts", payload)["broadcast"]
    got = [{k: v for k, v in g.items() if v is not None} for g in b.get("subscriber_filter") or []]
    want = [{k: v for k, v in g.items() if v is not None} for g in filt]
    if got != want:
        sys.exit(f"Draft {b['id']} has unexpected recipients {got}; NOT sending.")
    if mode == "--draft":
        print(f"Draft {b['id']} created in Kit: {subject!r} (not sent)")
        return
    payload["send_at"] = (datetime.now(timezone.utc) + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    b = kit("PUT", f"/broadcasts/{b['id']}", payload)["broadcast"]
    print(f"Broadcast {b['id']}: {subject!r} sending at {b['send_at']} to {mode[2:]}")

if __name__ == "__main__":
    main()
