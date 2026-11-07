"""Builds the project's working files from a LinkedIn data export.

Run from the project root:
    python3 scripts/build.py                        # uses the newest archive in raw/
    python3 scripts/build.py raw/<archive-folder>   # uses a specific archive

Creates or overwrites: profile/, content/posts/, content/comments/, content/articles/, activity/.
The source archive in raw/ is never modified. Files missing from a new export are not deleted.
"""
import csv, re, html, glob, os, sys, io, unicodedata
from datetime import datetime
from collections import defaultdict

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) > 1:
    R = os.path.abspath(sys.argv[1])
else:
    found = sorted(glob.glob(os.path.join(root, "raw", "*LinkedInDataExport*")), key=os.path.getmtime)
    if not found:
        sys.exit("No LinkedIn archive (*LinkedInDataExport*) found in raw/")
    R = found[-1]
print("Archive:", os.path.relpath(R, root))
if not os.path.isfile(os.path.join(R, "Profile.csv")):
    sys.exit("Profile.csv not found in the archive folder. The CSV files are probably one level deeper - "
             "move the inner archive folder directly into raw/ (see SETUP.md, step 4).")
if not os.path.isfile(os.path.join(R, "Shares.csv")):
    sys.exit("Shares.csv not found - this is the Basic archive, without posts and comments. "
             "Wait for the second email from LinkedIn and download the Complete archive (see SETUP.md, step 3).")

def rows(name):
    with open(os.path.join(R, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))

def clean(s):
    s = html.unescape(s or "")
    s = re.sub(r"<br\s*/?>|</p>|</li>", "\n", s)
    s = re.sub(r"<li[^>]*>", "\n• ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"•\s*\n\s*", "• ", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n\s*\n+", "\n\n", s)
    return s.strip()

def li_text(s):
    # LinkedIn Shares/Comments: line breaks are stored as "\n" wrapped in stray quotes
    s = (s or "").replace('"\n""\n"', "\n\n").replace('"\n"', "\n").replace("\xa0", " ")
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def write(path, text):
    p = os.path.join(root, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")

def slugify(text, n=6):
    t = unicodedata.normalize("NFKC", text).lower()
    words = re.findall(r"[^\W_]+", t)
    return "-".join(words[:n]) or "post"

def preview(text, n=80):
    t = unicodedata.normalize("NFKC", text)
    line = next((l for l in t.split("\n") if len(re.findall(r"[^\W\d_]{3,}", l)) >= 3), t.split("\n")[0])
    return line.strip()[:n].replace("|", "/")

# ---------- copy helpers ----------
def copy_csv(src, dst, skip_preamble=False, drop_cols=()):
    with open(os.path.join(R, src), encoding="utf-8", newline="") as f:
        t = f.read()
    if skip_preamble:
        lines = t.splitlines(keepends=True)
        i = next(k for k, l in enumerate(lines) if l.startswith("First Name"))
        t = "".join(lines[i:])
    if drop_cols:
        rd = list(csv.reader(io.StringIO(t)))
        keep = [k for k, c in enumerate(rd[0]) if c not in drop_cols]
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\n").writerows([[r[k] for k in keep] for r in rd if r])
        t = buf.getvalue()
    write(dst, t)

# ---------- profile: information about me ----------
def about(s):
    s = clean(s)
    s = re.sub(r"\s*•\s*", "\n• ", s)
    s = re.sub(r"(?<=[a-z.,;:)])(?=[A-Z\U0001D5D4-\U0001D627])", "\n\n", s)
    return s.strip()

# short tables: original CSVs, file names unified to lowercase_snake_case
PROFILE_NAMES = {
    "Education.csv": "education.csv", "Certifications.csv": "certifications.csv",
    "Organizations.csv": "organizations.csv", "Skills.csv": "skills.csv",
    "Endorsement_Received_Info.csv": "endorsements_received.csv",
    "Causes You Care About.csv": "causes.csv",
}
for src in ["Education.csv", "Certifications.csv", "Organizations.csv", "Skills.csv",
            "Endorsement_Received_Info.csv", "Causes You Care About.csv"]:
    copy_csv(src, f"profile/{PROFILE_NAMES[src]}")

# what LinkedIn inferred about me
copy_csv("Inferences_about_you.csv", "profile/linkedin_view/inferences.csv")
copy_csv("Verifications/Verifications.csv", "profile/verifications.csv", drop_cols=("Email address",))

# long texts: markdown
p = rows("Profile.csv")[0]
out = ["# Profile", "", "_Source: Profile.csv_", "",
       "## Name", "", f"{p['First Name']} {p['Last Name']}", "",
       "## Headline", "", clean(p["Headline"]), "",
       "## Industry", "", p["Industry"] or "—", "",
       "## Location", "", p["Geo Location"] or "—", "",
       "## Websites", "", clean(p["Websites"]) or "—", "",
       "## About", "", about(p["Summary"])]
write("profile/profile.md", "\n".join(out))

out = ["# Positions", "", "_Source: Positions.csv_", ""]
for r in rows("Positions.csv"):
    out += [f"## {r['Title']} — {r['Company Name']}",
            f"_{r['Started On']} – {r['Finished On'] or 'present'} · {r['Location']}_", "",
            about(r["Description"]), ""]
write("profile/positions.md", "\n".join(out))

out = ["# Projects", "", "_Source: Projects.csv_", ""]
for r in rows("Projects.csv"):
    out += [f"## {r['Title']}",
            f"_{r['Started On'] or '—'} – {r['Finished On'] or '—'}_" + (f" · {r['Url']}" if r["Url"] else ""), "",
            clean(r["Description"]), ""]
write("profile/projects.md", "\n".join(out))

# Ad_Targeting: one wide row -> long table Category,Value (deduplicated);
# categories that repeat my own data (Company Follows, Education) are dropped
AD_SKIP = {"Company Follower of", "Member Schools", "Degrees", "Graduation Year"}
with open(os.path.join(R, "Ad_Targeting.csv"), encoding="utf-8") as f:
    hdr, val = list(csv.reader(f))[:2]
seen, long_rows = set(), []
for k, v in zip(hdr, val):
    if k in AD_SKIP:
        continue
    for item in (x.strip() for x in v.split(";")):
        if item and (k, item) not in seen:
            seen.add((k, item)); long_rows.append((k, item))
buf = io.StringIO()
csv.writer(buf, lineterminator="\n").writerows([("Category", "Value")] + long_rows)
write("profile/linkedin_view/ad_targeting.csv", buf.getvalue())

# ---------- posts: Shares.csv, one file each ----------
shares = sorted(rows("Shares.csv"), key=lambda r: r["Date"], reverse=True)
idx = ["# Posts", "",
       "_Source: Shares.csv. Newest first. The export contains no post statistics (reach, reactions)._", "",
       "| Date | Beginning of post | File |", "|---|---|---|"]
used, empty = set(), []
for r in shares:
    d = datetime.strptime(r["Date"], "%Y-%m-%d %H:%M:%S")
    text = li_text(r["ShareCommentary"])
    if not text:
        empty.append((d, r))
        continue
    base = f"{d:%Y-%m-%d}_{slugify(text)}"
    name, i = f"{base}.md", 2
    while name in used:
        name = f"{base}-{i}.md"; i += 1
    used.add(name)
    meta = [f"_Date: {d:%Y-%m-%d %H:%M}_  ", f"_Link: {r['ShareLink']}_  "]
    if r["SharedUrl"]: meta.append(f"_Shared URL: {r['SharedUrl']}_  ")
    if r["MediaUrl"]: meta.append(f"_Media: {r['MediaUrl']}_  ")
    meta.append(f"_Visibility: {r['Visibility']}_")
    write(f"content/posts/{name}", f"# Post {d:%Y-%m-%d}\n\n" + "\n".join(meta) + f"\n\n---\n\n{text}")
    idx.append(f"| {d:%Y-%m-%d} | {preview(text)} | [{name}]({name}) |")
if empty:
    idx += ["", "## Posts without text", ""]
    idx += [f"- {d:%Y-%m-%d %H:%M} · {r['ShareLink']}" for d, r in empty]
write("content/posts/README.md", "\n".join(idx))

# ---------- comments: one file per month ----------
by_month = defaultdict(list)
for r in rows("Comments.csv"):
    d = datetime.strptime(r["Date"], "%Y-%m-%d %H:%M:%S")
    by_month[f"{d:%Y-%m}"].append((d, r))
cidx = ["# Comments", "",
        "_Source: Comments.csv. One file per month, sorted by date inside. Each link points to the post the comment was left on._", "",
        "| Month | Count | File |", "|---|---|---|"]
for m in sorted(by_month, reverse=True):
    items = sorted(by_month[m], key=lambda x: x[0])
    body = [f"# Comments {m}", ""]
    for d, r in items:
        body += [f"## {d:%Y-%m-%d %H:%M}", "", f"_Post: {r['Link']}_", "", li_text(r["Message"]), "", "---", ""]
    write(f"content/comments/{m}.md", "\n".join(body))
    cidx.append(f"| {m} | {len(items)} | [{m}.md]({m}.md) |")
write("content/comments/README.md", "\n".join(cidx))

# ---------- articles ----------
arts = []
for f in glob.glob(os.path.join(R, "Articles/Articles/*.html")):
    t = open(f, encoding="utf-8").read()
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S)
    title = clean(re.search(r"<title>(.*?)</title>", t, re.S).group(1))
    pub = re.search(r"Published on (\d{4}-\d{2}-\d{2})", t)
    pub = pub.group(1) if pub else "unknown"
    body = re.search(r"<body.*?>(.*)</body>", t, re.S).group(1)
    body = re.sub(r"<h1.*?</h1>", "", body, flags=re.S)
    body = re.sub(r"<p class=\"(created|published)\">.*?</p>", "", body, flags=re.S)
    body = re.sub(r"<h([23])[^>]*>(.*?)</h\1>", lambda m: "\n\n" + "#" * int(m.group(1)) + " " + clean(m.group(2)) + "\n\n", body, flags=re.S)
    body = re.sub(r"<p[^>]*>", "\n\n", body)
    body = re.sub(r"<img[^>]*src=\"([^\"]+)\"[^>]*>", r"\n\n![](\1)\n\n", body)
    name = f"{pub}_{slugify(title, 8)}.md"
    write(f"content/articles/{name}", f"# {title}\n\n_Published: {pub}_\n\n{clean(body)}")
    arts.append(f"| {pub} | {title} | [{name}]({name}) |")
write("content/articles/README.md", "\n".join(["# Articles", "", "| Date | Title | File |", "|---|---|---|"] + sorted(arts, reverse=True)))

# ---------- activity: network, actions, jobs ----------
for src, dst, *pre in [
    ("Connections.csv", "network/connections.csv", True),
    ("Invitations.csv", "network/invitations.csv"),
    ("Member_Follows.csv", "network/member_follows.csv"),
    ("Company Follows.csv", "network/company_follows.csv"),
    ("Reactions.csv", "actions/reactions.csv"),
    ("InstantReposts.csv", "actions/reposts.csv"),
    ("Votes.csv", "actions/votes.csv"),
    ("Saved_Items.csv", "actions/saved_items.csv"),
    ("SearchQueries.csv", "actions/search_queries.csv"),
    ("Events.csv", "actions/events.csv"),
    ("Learning.csv", "actions/learning.csv"),
    ("Endorsement_Given_Info.csv", "actions/endorsements_given.csv"),
    ("Jobs/Job Applications.csv", "jobs/applications.csv"),
    ("Jobs/Saved Jobs.csv", "jobs/saved_jobs.csv"),
    ("Job Applicant Saved Screening Question Responses.csv", "jobs/screening_answers.csv"),
]:
    copy_csv(src, f"activity/{dst}", bool(pre))

# ---------- messages: one markdown file per conversation ----------
_me = rows("Profile.csv")[0]
ME = f"{_me['First Name']} {_me['Last Name']}".strip()  # as LinkedIn shows the owner in messages
convs = defaultdict(list)
for r in rows("messages.csv"):
    convs[r["CONVERSATION ID"]].append(r)
midx = ["# Conversations", "", "_Source: messages.csv. One file per conversation, sorted by date inside. Most recent first._", "",
        "| Last message | With | Subject | Messages | File |", "|---|---|---|---|---|"]
entries, used_m = [], set()
for cid, msgs in convs.items():
    msgs.sort(key=lambda r: r["DATE"])
    people = []
    for r in msgs:
        for n in [r["FROM"]] + r["TO"].split(","):
            n = n.strip()
            if n and n != ME and n not in people:
                people.append(n)
    who = ", ".join(people) or ME
    title = next((r["CONVERSATION TITLE"] or r["SUBJECT"] for r in msgs if r["CONVERSATION TITLE"] or r["SUBJECT"]), "")
    first = msgs[0]["DATE"][:10]
    base = f"{first}_{slugify(who, 4)}"
    name, i = f"{base}.md", 2
    while name in used_m:
        name = f"{base}-{i}.md"; i += 1
    used_m.add(name)
    body = [f"# {who}", ""]
    if title: body += [f"_Subject: {title}_  "]
    body += [f"_Messages: {len(msgs)}, {first} – {msgs[-1]['DATE'][:10]}_", ""]
    for r in msgs:
        body += [f"## {r['DATE'][:16]} · {r['FROM'] or '—'}", ""]
        if r["SUBJECT"] and r["SUBJECT"] != title:
            body += [f"**{r['SUBJECT']}**", ""]
        body.append(clean(r["CONTENT"]) or "_(no text)_")
        if r["ATTACHMENTS"]:
            body += ["", f"_Attachments: {len(r['ATTACHMENTS'].split(','))}_"]
        body.append("")
    write(f"activity/network/messages/{name}", "\n".join(body))
    entries.append((msgs[-1]["DATE"], f"| {msgs[-1]['DATE'][:10]} | {who.replace('|', '/')} | {title.replace('|', '/')} | {len(msgs)} | [{name}]({name}) |"))
midx += [e for _, e in sorted(entries, reverse=True)]
write("activity/network/messages/README.md", "\n".join(midx))
print("conversations:", len(convs))
print("posts:", len(used), "empty:", len(empty), "comment months:", len(by_month), "articles:", len(arts))
