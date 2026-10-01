"""Builds the Mission Performance SB website into static HTML files.

Edit page content below, then run:  python3 build.py
Every page shares the same head, header and footer, so a change to the nav,
address or hours only needs to be made once here.
"""
import html
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))

# While the site is at the GitHub test address, keep it out of Google.
# Flip to False when the real domain points here.
TESTING = True

# Free form handler that emails submissions to jack@missionperformsb.com.
# Get a key at https://web3forms.com (enter the email, the key arrives by email).
WEB3FORMS_KEY = "YOUR_WEB3FORMS_KEY"

SITE_NAME = "Mission Performance SB"
EMAIL = "jack@missionperformsb.com"
INSTAGRAM = "https://www.instagram.com/missionperformsb"
ADDRESS = "135 E Carrillo St, Santa Barbara, CA 93101"
HOURS = [("Monday – Friday", "3:00 – 8:30 PM"), ("Saturday", "11:30 AM")]

NAV = [
    ("how-it-works.html", "How It Works"),
    ("about.html", "About"),
    ("athletes.html", "Where Our Athletes Go"),
    ("newsletter/", "Newsletter"),
]

# Ordered roughly biggest program first. Name + school + sport, no years.
ATHLETES = [
    ("Quinn Melton", "Michigan", "Baseball"),
    ("Emmett Mack", "USC", "Track & Field"),
    ("Sonia Mancuso", "Pepperdine", "Beach Volleyball"),
    ("Griffin Arnold", "Pepperdine", "Baseball"),
    ("Brooks Firestone", "Cal Poly", "Soccer"),
    ("Cason Goodman", "UC Davis", "Soccer"),
    ("Kelham Wolf", "UC San Diego", "Soccer"),
    ("Paddy Blinderman", "Iona", "Golf"),
    ("Logan Reed", "Claremont-Mudd-Scripps", "Football"),
    ("Bear Goodman", "Westmont", "Soccer"),
    ("Gizela Zermeno", "Westmont", "Soccer"),
    ("Parker Hellekson", "SBCC", "Baseball"),
]

MENU_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'


def esc(s):
    return html.escape(s, quote=True)


def page(path, title, description, body, depth=0, og_image="assets/og.jpg"):
    """Wrap page body in the shared head/header/footer and write it to path."""
    up = "../" * depth
    current = path.replace("index.html", "")
    nav_links = "".join(
        f'<a href="{up}{href}"{" aria-current=\"page\"" if current == href else ""}>{label}</a>'
        for href, label in NAV
    )
    hours = "".join(f"<li>{d}: {t}</li>" for d, t in HOURS)
    full_title = title if title == SITE_NAME else f"{title} | {SITE_NAME}"
    robots = '<meta name="robots" content="noindex, nofollow">' if TESTING else ""
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
{robots}
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{up}{og_image}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0c0c0d">
<link rel="icon" type="image/png" href="{up}assets/favicon.png">
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Barlow+Condensed:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/site.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{up}./" aria-label="{SITE_NAME} home"><img src="{up}img/logo.svg" alt="{SITE_NAME}"></a>
    <button class="menu-toggle" aria-label="Menu" aria-expanded="false" onclick="var n=document.querySelector('.nav');n.classList.toggle('open');this.setAttribute('aria-expanded',n.classList.contains('open'))">{MENU_ICON}</button>
    <nav class="nav">{nav_links}<a class="btn" href="{up}consult.html">Request a Consult</a></nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div>
        <img src="{up}img/logo.svg" alt="{SITE_NAME}">
        <p>Strength and performance training for youth athletes in Santa Barbara.</p>
      </div>
      <div>
        <h4>Visit</h4>
        <p>{ADDRESS.replace(", Santa", "<br>Santa")}</p>
        <ul>{hours}</ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram @missionperformsb</a></li>
          <li><a href="{up}consult.html">Request a Consult</a></li>
          <li><a href="{up}newsletter/">Newsletter</a></li>
        </ul>
      </div>
    </div>
    <p class="legal">© {date.today().year} {SITE_NAME} LLC</p>
  </div>
</footer>
<script>
document.querySelectorAll('form[data-web3]').forEach(function (f) {{
  f.addEventListener('submit', function (e) {{
    e.preventDefault();
    var s = f.querySelector('.form-status'), b = f.querySelector('button[type=submit]');
    b.disabled = true; s.className = 'form-status show'; s.textContent = 'Sending…';
    fetch('https://api.web3forms.com/submit', {{ method: 'POST', body: new FormData(f) }})
      .then(function (r) {{ return r.json(); }})
      .then(function (d) {{
        if (!d.success) throw new Error(d.message);
        s.className = 'form-status show ok'; s.textContent = f.dataset.ok; f.reset();
      }})
      .catch(function () {{
        s.textContent = 'Something went wrong. Please email {EMAIL} instead.';
      }})
      .finally(function () {{ b.disabled = false; }});
  }});
}});
</script>
</body>
</html>
"""
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)


def cta(up=""):
    return f"""
<section class="block cta">
  <div class="wrap">
    <h2>Ready to get started?</h2>
    <p class="lede">Every athlete starts with a consultation: athlete and parent, together. Tell us a little about your athlete and we'll reach out to set it up.</p>
    <div class="btn-row"><a class="btn" href="{up}consult.html">Request a Consult</a></div>
  </div>
</section>"""


def build_home():
    schools = []
    for _, school, _ in ATHLETES:
        if school not in schools:
            schools.append(school)
    school_tags = "".join(f"<span>{esc(s)}</span>" for s in schools)
    body = f"""
<section class="hero home">
  <img src="img/gym-squat-logo.jpg" alt="Athlete squatting in a Mission Performance shirt">
  <div class="wrap">
    <h1>Mission Performance SB</h1>
    <p class="lede">Youth athlete strength and performance training, education and mentorship in Santa Barbara, California.</p>
    <div class="btn-row">
      <a class="btn" href="consult.html">Request a Consult</a>
      <a class="btn ghost" href="how-it-works.html">How It Works</a>
    </div>
  </div>
</section>

<section class="block mission">
  <div class="wrap">
    <p class="eyebrow">Our Mission</p>
    <blockquote>To prolong and enhance the careers of youth athletes in Santa Barbara through proper training, education and preparation.</blockquote>
    <p class="mission-sub">Every athlete is on their own journey — good coaching and mentorship are part of what gets them there.</p>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">The Program</p>
      <h2>What training looks like</h2>
    </div>
    <div class="grid two">
      <div class="card"><img src="img/gym-coaching-jump.jpg" alt="Coach cueing an athlete through a jump" loading="lazy"><div class="pad"><h3>Small groups</h3><p>Sessions run with 2–7 athletes. Athletes get the energy of a group with the attention of private training.</p></div></div>
      <div class="card"><img src="img/gym-db-bench.jpg" alt="Athlete pressing dumbbells on a bench" loading="lazy"><div class="pad"><h3>Your own program</h3><p>Every athlete has a program built around their sport, season, history and goals, delivered straight to their phone.</p></div></div>
      <div class="card"><img src="img/outdoor-timing-gates.jpg" alt="Athlete sprinting through timing gates" loading="lazy"><div class="pad"><h3>Measured progress</h3><p>Force plates, timing gates and regular testing show exactly where an athlete is improving and where they need work. No guessing.</p></div></div>
      <div class="card"><img src="img/outdoor-demo.jpg" alt="Coach demonstrating a drill to a group of athletes" loading="lazy"><div class="pad"><h3>The whole athlete</h3><p>Sleep, nutrition, recovery and workload all matter as much as the weight room. We coach all of it, from the fueling station to the monthly Speaker Series.</p></div></div>
    </div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="split">
      <div>
        <p class="eyebrow">Who It's For</p>
        <h2>Athletes with a goal</h2>
        <p class="lede" style="margin-top:18px">We work with middle school, high school and college athletes in every sport, from baseball (our biggest group) to volleyball, soccer, basketball, football, water polo, tennis and more.</p>
        <p class="dim">The athletes who get the most out of Mission are the ones chasing something specific: making varsity, playing in college, staying healthy through a long season.</p>
      </div>
      <img src="img/outdoor-sprint-yellow.jpg" alt="Athlete sprinting across the grass" loading="lazy">
    </div>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Results</p>
      <h2>Where our athletes go</h2>
      <p class="lede">Mission athletes are competing at programs across the country.</p>
    </div>
    <div class="schools">{school_tags}</div>
    <div class="btn-row"><a class="btn ghost" href="athletes.html">See the full list</a></div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="split flip">
      <div>
        <p class="eyebrow">The Facility</p>
        <h2>135 E Carrillo St</h2>
        <p class="lede" style="margin-top:18px">An 1,800 sq ft training space in downtown Santa Barbara with full racks, turf, force plates and a fueling station stocked for athletes before and after they train.</p>
        <div class="info" style="margin-top:28px">
          {"".join(f'<div><h3>{d}</h3><p>{t}</p></div>' for d, t in HOURS)}
        </div>
      </div>
      <img src="img/gym-overhead-press.jpg" alt="Athlete pressing a barbell overhead" loading="lazy">
    </div>
  </div>
</section>
{cta()}"""
    page("index.html", SITE_NAME,
         "Strength and performance training for youth athletes in Santa Barbara, CA. Small groups, individualized programs and measured progress.",
         body)


def build_how():
    body = f"""
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">How It Works</p>
    <h1>From first call to game day</h1>
    <p class="lede">Here's what to expect when your athlete starts at Mission Performance.</p>
  </div>
</section>

<section class="block">
  <div class="wrap narrow">
    <ol class="steps">
      <li><div><h3>Request a consult</h3><p>Fill out the short form with some information about your athlete. Jack will reach out personally to set up a time.</p></div></li>
      <li><div><h3>The consultation</h3><p>Athlete and parent meet with Jack together. We talk through the athlete's sports journey, injury history, strengths and weaknesses, life outside of sports, goals, and daily habits like sleep and nutrition. Then we walk you through exactly how the program works and answer every question.</p></div></li>
      <li><div><h3>Assessment</h3><p>Every athlete starts with a movement screen, including hip mobility, and baseline testing on force plates. Assessment doesn't stop there. We keep learning about each athlete through their first weeks of training.</p></div></li>
      <li><div><h3>An individualized program</h3><p>Each athlete gets their own program built around their sport, position, training age and goals. It lives in an app on their phone, so they always know what they're doing and why.</p></div></li>
      <li><div><h3>Train in small groups</h3><p>Sessions run 60–90 minutes with 2–7 athletes. Athletes book their own sessions each week from our group times. Most train twice a week, year-round.</p></div></li>
      <li><div><h3>Test, report, adjust</h3><p>Athletes retest on force plates and get a performance report showing their progress. Programs adjust through the year, including in-season, when volume comes down but strength work continues.</p></div></li>
    </ol>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <div class="split">
      <img src="img/gym-coaching-sprint-start.jpg" alt="Coach watching an athlete drive out of a sprint start" loading="lazy">
      <div>
        <p class="eyebrow">In-Season</p>
        <h2>Training doesn't stop when the season starts</h2>
        <p class="lede" style="margin-top:18px">In-season is when athletes are most likely to lose strength and pick up injuries. We keep training through it, adjusted week to week:</p>
        <ul class="list">
          <li>Less volume, but intensity stays high enough to hold onto strength</li>
          <li>Less sprinting, jumping and high-impact work</li>
          <li>More mobility, arm care and injury-prevention work</li>
          <li>Constant communication about how the athlete is feeling</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Beyond the Weight Room</p>
      <h2>Coaching the whole athlete</h2>
    </div>
    <div class="grid three">
      <div class="card"><div class="pad"><h3>Fueling Station</h3><p>A stocked fridge and snack bar at the gym, so athletes can refuel before and after training instead of running on empty.</p></div></div>
      <div class="card"><div class="pad"><h3>Speaker Series</h3><p>Each month we bring in experts and high-level performers to talk with athletes and parents about nutrition, mental performance, recruiting and building good habits.</p></div></div>
      <div class="card"><div class="pad"><h3>Education</h3><p>Sleep, nutrition, recovery and workload are part of the coaching, not an afterthought. Our <a href="newsletter/">newsletter</a> covers the topics we talk about most.</p></div></div>
    </div>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Schedule</p><h2>When we train</h2></div>
    <div class="info">
      {"".join(f'<div><h3>{d}</h3><p>{t}</p></div>' for d, t in HOURS)}
      <div><h3>Summer</h3><p>Group times shift to mornings and midday.</p></div>
      <div><h3>Location</h3><p>{ADDRESS}</p></div>
    </div>
  </div>
</section>
{cta()}"""
    page("how-it-works.html", "How It Works",
         "From the first consultation to game day: assessment, individualized programming, small-group training and regular testing.",
         body)


def build_about():
    body = f"""
<section class="hero">
  <img src="img/outdoor-jack-logo.jpg" alt="Coach Jack Anderson from behind in a black Mission Performance shirt" style="object-position:center 20%">
  <div class="wrap">
    <p class="eyebrow">About</p>
    <h1>Jack Anderson, MS, CSCS</h1>
    <p class="lede">Founder and head coach, Mission Performance SB</p>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="split">
      <div>
        <p>I've loved sports for as long as I can remember. That started as a three-year-old NFL fan and carried through playing youth sports, and then spending years in and around professional sport.</p>
        <p>Before coaching, I worked in sports media as a credentialed NFL reporter and radio producer for SiriusXM. Competitive powerlifting pulled me toward strength and conditioning, and I went on to earn a Master's in Exercise Science and become a Certified Strength and Conditioning Specialist (CSCS).</p>
        <p>Since then I've coached in professional and college settings, including the San Jose Sharks, the Buffalo Bills, Canisius University, the University at Buffalo and the University of Mary Washington. I also privately trained professional athletes from the NHL, NBA, MLB, MLS and AVP.</p>
        <p>Of everything I've done, coaching youth athletes here in Santa Barbara has been the most fulfilling. I started Mission Performance in 2024 because I believe young athletes deserve better guidance than most of them get: training that's built for them, and real education about sleep, nutrition, recovery and how to navigate the world of sports.</p>
      </div>
      <img src="img/jack-headshot.jpg" alt="Headshot of Jack Anderson" style="aspect-ratio:4/5" loading="lazy">
    </div>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">Experience</p><h2>Where I've coached</h2></div>
    <div class="info">
      <div><h3>Professional</h3><p>San Jose Sharks<br>Buffalo Bills</p></div>
      <div><h3>College</h3><p>Canisius University<br>University at Buffalo<br>University of Mary Washington</p></div>
      <div><h3>Private Clients</h3><p>Athletes from the NHL, NBA, MLB, MLS and AVP</p></div>
      <div><h3>Credentials</h3><p>MS, Exercise Science<br>CSCS, NSCA</p></div>
    </div>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <div class="section-head"><p class="eyebrow">What We Stand For</p><h2>Mission values</h2></div>
    <div class="grid two">
      <div class="card"><div class="pad"><h3>Holistic Development</h3><p>Growing athletes physically, mentally, emotionally and socially, not just on the field.</p></div></div>
      <div class="card"><div class="pad"><h3>Effort / Attitude</h3><p>The way athletes carry themselves matters. Show up ready to work every session, bring energy, compete with yourself and your teammates. These small habits build a greater potential for greatness.</p></div></div>
      <div class="card"><div class="pad"><h3>Coachability</h3><p>The athlete-coach relationship is critical to success. The athletes who improve fastest are the ones most open to coaching. Listen, ask questions and apply feedback.</p></div></div>
      <div class="card"><div class="pad"><h3>Ownership</h3><p>Athletes who take accountability of their own process are far more likely to succeed in sports and in life.</p></div></div></div>
    </div>
  </div>
</section>
{cta()}"""
    page("about.html", "About",
         "Jack Anderson, MS, CSCS: founder and head coach of Mission Performance SB, with experience across the NHL, NFL and college strength and conditioning.",
         body)


def build_athletes():
    cards = "".join(
        f'<div class="athlete"><div class="school">{esc(s)}</div><div class="sport">{esc(sp)}</div><div class="name">{esc(n)}</div></div>'
        for n, s, sp in ATHLETES
    )
    body = f"""
<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Results</p>
    <h1>Where our athletes go</h1>
    <p class="lede">Mission athletes now competing in college, across every level and a range of sports.</p>
  </div>
</section>
<section class="block">
  <div class="wrap">
    <div class="athletes">{cards}</div>
  </div>
</section>
{cta()}"""
    page("athletes.html", "Where Our Athletes Go",
         "Mission Performance SB athletes now competing in college, from Michigan and USC to Pepperdine, Cal Poly and Westmont.",
         body)


def signup_box(up=""):
    return f"""
<div class="signup">
  <h3>Get the newsletter</h3>
  <p class="dim" style="margin:8px 0 0">Training, nutrition, sleep and recruiting advice for athletes and parents, sent to your inbox.</p>
  <form data-web3 data-ok="You're on the list. Thanks for subscribing!">
    <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
    <input type="hidden" name="subject" value="New newsletter signup">
    <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
    <input type="email" name="email" placeholder="Email address" aria-label="Email address" required>
    <button class="btn" type="submit">Subscribe</button>
    <div class="form-status" role="status" style="flex-basis:100%"></div>
  </form>
</div>"""


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%B %-d, %Y")


def build_newsletter():
    articles = json.load(open(os.path.join(ROOT, "newsletter", "articles.json"), encoding="utf-8"))
    items = "".join(
        f'<li><a href="{a["slug"]}.html"><div class="t">{esc(a["title"])}</div><div class="d">{fmt_date(a["date"])}</div></a></li>'
        for a in articles
    )
    body = f"""
<section class="page-hero">
  <div class="wrap narrow">
    <p class="eyebrow">Newsletter</p>
    <h1>The Mission Newsletter</h1>
    <p class="lede">Practical advice on training, nutrition, sleep, recovery and recruiting for youth athletes and their parents.</p>
  </div>
</section>
<section class="block">
  <div class="wrap narrow">
    {signup_box("../")}
    <ul class="articles" style="margin-top:40px">{items}</ul>
  </div>
</section>"""
    page("newsletter/index.html", "Newsletter",
         "Training, nutrition, sleep, recovery and recruiting advice for youth athletes and parents from Mission Performance SB.",
         body, depth=1)

    for a in articles:
        body = f"""
<article class="article">
  <div class="wrap narrow">
    <a class="back" href="./">← All articles</a>
    <h1>{esc(a["title"])}</h1>
    <p class="meta">Jack Anderson, MS, CSCS · {fmt_date(a["date"])}</p>
    <div class="body">{a["body"]}</div>
    <div style="margin-top:48px">{signup_box("../")}</div>
  </div>
</article>"""
        text = " ".join(html.unescape(__import__("re").sub(r"<[^>]+>", " ", a["body"])).split())
        page(f"newsletter/{a['slug']}.html", a["title"], text[:155].rsplit(" ", 1)[0] + "…", body, depth=1)


def build_consult():
    def field(name, label, type_="text", required=True, full=False, autocomplete=None):
        req = " required" if required else ""
        ac = f' autocomplete="{autocomplete}"' if autocomplete else ""
        cls = ' class="full"' if full else ""
        return f'<div{cls}><label for="{name}">{label}{"" if required else " <span class=dim>(optional)</span>"}</label><input id="{name}" name="{name}" type="{type_}"{req}{ac}></div>'

    grades = "".join(f"<option>{g}</option>" for g in
                     ["6th", "7th", "8th", "9th", "10th", "11th", "12th", "College", "Other"])
    body = f"""
<section class="page-hero">
  <div class="wrap narrow">
    <p class="eyebrow">Get Started</p>
    <h1>Request a consult</h1>
    <p class="lede">Every athlete starts with a consultation, athlete and parent together. Tell us a little about your athlete and Jack will reach out personally to find a time.</p>
  </div>
</section>
<section class="block">
  <div class="wrap narrow">
    <form data-web3 data-ok="Thanks! Your request is in. Jack will reach out soon to set up a consultation.">
      <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
      <input type="hidden" name="subject" value="New consult request from the website">
      <input type="hidden" name="from_name" value="Mission Performance website">
      <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
      <fieldset>
        <legend>Parent / Guardian</legend>
        <div class="fields">
          {field("parent_name", "Name", full=True, autocomplete="name")}
          {field("parent_phone", "Phone", "tel", autocomplete="tel")}
          {field("parent_email", "Email", "email", autocomplete="email")}
        </div>
      </fieldset>
      <fieldset>
        <legend>Athlete</legend>
        <div class="fields">
          {field("athlete_name", "Name", full=True)}
          {field("athlete_phone", "Phone", "tel")}
          {field("athlete_email", "Email", "email")}
          <div><label for="grade">Grade</label><select id="grade" name="grade" required><option value="">Select…</option>{grades}</select></div>
          {field("school", "School")}
          {field("sports", "Sport(s)", full=True)}
          <div class="full"><label for="goal">What is the athlete's goal?</label><textarea id="goal" name="goal" required placeholder="e.g. make varsity, play in college, stay healthy through the season"></textarea></div>
          {field("heard_about", "How did you hear about us?", full=True)}
        </div>
      </fieldset>
      <button class="btn" type="submit">Send Request</button>
      <div class="form-status" role="status"></div>
      <p class="form-note">Prefer email? Reach Jack directly at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    </form>
  </div>
</section>"""
    page("consult.html", "Request a Consult",
         "Request a consultation with Mission Performance SB. Athlete and parent meet with Jack to talk goals, history and how the program works.",
         body)


def build_robots():
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /\n" if TESTING else "User-agent: *\nAllow: /\n")


if __name__ == "__main__":
    build_home()
    build_how()
    build_about()
    build_athletes()
    build_newsletter()
    build_consult()
    build_robots()
    print("Built.")
