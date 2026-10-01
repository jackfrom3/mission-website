"""One-time import of evergreen Substack articles into site article data.

Each old Substack issue mixed one real article with dated news (merch drops,
food drives, schedules). This pulls out only the article sections listed in
ARTICLES, cleans Substack-specific markup, downloads images locally, and writes
newsletter/articles.json for build.py.

Usage: python3 tools/import_substack.py <unzipped substack export dir>
"""
import html
import json
import os
import re
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slug, title, source file prefix, section heading to take (None = text before first heading)
ARTICLES = [
    ("season-transitions", "The Biggest Mistake I'm Seeing Athletes Make", "185447574", None),
    ("spring-sleep-habits", "Spring Into Solid Sleep Habits", "187719593", None),
    ("returning-from-a-concussion", "Returning Properly From a Concussion", "158260111", None),
    ("road-warriors", "Road Warriors: Peak Performance for Away Games", "156131946", "Road Warriors"),
    ("compression-vs-ice", "Compression vs. Ice: Which Is Better?", "156129622", "Compression vs. Ice"),
    ("nutrition-checklist", "A Simple Nutrition Checklist for Athletes", "156127290", "Nutrition Checklist"),
    ("lift-in-season", "Lift In-Season, Stay Strong", "153546128", "Lift In-Season"),
    ("dont-forget-about-fats", "Don't Forget About Fats", "153546128", "Forget About Fats"),
    ("caffeine", "The Buzz Around Caffeine", "153546550", "The Buzz Around Caffeine"),
    ("ncaa-recruiting-changes-2025", "What to Make of the 2025 NCAA Recruiting Changes", "152500873", "NCAA Recruiting Changes"),
    ("carbohydrates", "Carbohydrates Are the Secret Stuff", "152179732", "Carbohydrates are the Secret Stuff"),
    ("dont-skip-breakfast", "Don't Skip Breakfast", "151911382", "Skip Breakfast"),
    ("three-pillars-of-sleep", "The Three Pillars of Sleep", "151543352", "The Three Pillars of Sleep"),
    ("creatine", "Should Athletes Take Creatine?", "151201944", "Should Athletes Take Creatine?"),
    ("college-recruiting", "How to Win the College Recruiting Process", "150854786", "Win the College Recruiting Process"),
    ("ncaa-eligibility", "NCAA Eligibility Requirements", "150503561", "NCAA Eligibility Requirements"),
]

# Sentences/paragraphs that are newsletter boilerplate, not article content
BOILERPLATE = [
    r"Thanks for reading Mission Performance Newsletter!.*",
    r"Welcome back to the Mission Performance Newsletter!.*",
    r"^Subscribe now$",
]


def find_post(export_dir, prefix):
    posts = os.path.join(export_dir, "posts")
    for f in os.listdir(posts):
        if f.startswith(prefix + ".") and f.endswith(".html"):
            return os.path.join(posts, f)
    raise FileNotFoundError(prefix)


def take_section(src, heading):
    parts = re.split(r"(<h[1-4][^>]*>.*?</h[1-4]>)", src, flags=re.S)
    if heading is None:
        return parts[0]
    for i in range(1, len(parts), 2):
        if heading.lower() in html.unescape(re.sub(r"<[^>]+>", "", parts[i])).lower().replace("’", "'"):
            return parts[i + 1]
    raise ValueError("heading not found: " + heading)


def shrink(path):
    """Cap width and recompress; large PNG photos become JPEGs. Returns final path."""
    from PIL import Image
    im = Image.open(path)
    if os.path.getsize(path) <= 250_000 and im.width <= 1400:
        return path
    im.thumbnail((1400, 1400))
    out = os.path.splitext(path)[0] + ".jpg"
    im.convert("RGB").save(out, quality=82, optimize=True, progressive=True)
    if out != path:
        os.remove(path)
    return out


def localize_images(body, slug):
    out_dir = os.path.join(ROOT, "newsletter", "img")
    n = 0

    def repl(m):
        nonlocal n
        block = m.group(0)
        src = re.search(r'<img[^>]+src="([^"]+)"', block).group(1)
        ext = os.path.splitext(src.split("?")[0])[1].lower() or ".jpg"
        n += 1
        base = os.path.join(out_dir, f"{slug}-{n}")
        done = [base + e for e in (ext, ".jpg") if os.path.exists(base + e)]
        if done:
            path = shrink(done[0])
        else:
            path = base + ext
            # curl, not urllib: this Mac's python.org build lacks root certs
            subprocess.run(["curl", "-sSfL", "-o", path, src], check=True)
            path = shrink(path)
        name = os.path.basename(path)
        return f'<figure><img src="img/{name}" alt="" loading="lazy"></figure>'

    return re.sub(r'<div class="captioned-image-container">.*?</figure></div>', repl, body, flags=re.S)


def clean(body, slug):
    body = localize_images(body, slug)
    # Drop subscribe widgets / buttons
    body = re.sub(r'<div class="subscription-widget-wrap.*?</form></div></div></div>', "", body, flags=re.S)
    body = re.sub(r'<p class="button-wrapper".*?</p>', "", body, flags=re.S)
    body = re.sub(r"<form.*?</form>", "", body, flags=re.S)
    # Strip Substack attributes but keep links and basic structure
    body = re.sub(r"<(p|ul|ol|li|strong|em|h[1-4]|blockquote)\s[^>]*>", r"<\1>", body)
    body = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>', r'<a href="\1" target="_blank" rel="noopener">', body)
    body = re.sub(r"</?(span|div)[^>]*>", "", body)
    # Remove boilerplate paragraphs
    def drop_boiler(m):
        text = html.unescape(re.sub(r"<[^>]+>", "", m.group(0))).strip()
        return "" if any(re.match(b, text) for b in BOILERPLATE) else m.group(0)
    body = re.sub(r"<p>.*?</p>", drop_boiler, body, flags=re.S)
    body = re.sub(r"<p>\s*</p>", "", body)
    return body.strip()


def main(export_dir):
    import csv
    dates = {r["post_id"].split(".")[0]: r["post_date"][:10] for r in csv.DictReader(open(os.path.join(export_dir, "posts.csv")))}
    out = []
    for slug, title, prefix, heading in ARTICLES:
        src = open(find_post(export_dir, prefix), encoding="utf-8").read()
        body = clean(take_section(src, heading), slug)
        d = date.fromisoformat(dates[prefix])
        out.append({"slug": slug, "title": title, "date": d.isoformat(), "body": body})
        print(f"{slug}: {len(re.sub('<[^>]+>', '', body))} chars")
    out.sort(key=lambda a: a["date"], reverse=True)
    json.dump(out, open(os.path.join(ROOT, "newsletter", "articles.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1])
