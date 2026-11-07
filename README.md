# LinkedIn Profile Workspace

Turn your LinkedIn data into a tidy folder you can work on with Claude: your profile, posts, articles, comments, conversations and activity, each in its own place.

No coding needed — Claude does the technical part for you.

## Quick start

### Step 1. Download this project

1. At the top of this page, click the green **Code** button → **Download ZIP**.
2. Open your **Downloads** folder and double-click the ZIP file to unpack it (on Windows: right-click → **Extract All**).
3. Move the unpacked folder somewhere convenient, for example to **Documents**, and rename it to `LinkedIn`.

More: [SETUP.md, step 1](SETUP.md#step-1-get-the-template).

### Step 2. Ask LinkedIn for your data

1. Open [this LinkedIn page](https://www.linkedin.com/mypreferences/d/download-my-data) and sign in.
2. Select the **first option**: *Download larger data archive…*
3. Click **Request archive**.
4. Wait for an email from LinkedIn. **You will get two emails — you need the second one**, which arrives within 24 hours. The first one (after ~10 minutes) does not contain your posts.

More: [SETUP.md, steps 2–3](SETUP.md#step-2-request-your-data-archive-from-linkedin) — the two archives and export limitations.

### Step 3. Put your data into the project

1. In the second email, click the link and download the archive. The file is called `Complete_LinkedInDataExport_….zip`.
2. Double-click it to unpack.
3. Open your `LinkedIn` project folder and create a new folder inside it named **`raw`**.
4. Drag the unpacked `Complete_LinkedInDataExport_…` folder into `raw`.

More: [SETUP.md, step 4](SETUP.md#step-4-put-the-archive-into-the-project) — what the folder should look like.

### Step 4. Open the project in Claude Code

1. Install Claude Code: [claude.com/claude-code](https://claude.com/claude-code) — the desktop app is the easiest option.
2. Open Claude Code and choose your `LinkedIn` folder as the project.

More: [SETUP.md, step 5](SETUP.md#step-5-open-the-project-in-claude-code).

### Step 5. Ask Claude to build the project

Type in the chat:

> Build the project from my LinkedIn archive.

Claude will run the build and tell you what it found. If it asks for permission to run a command, click **Allow**.

**Done.** Your data is now sorted into the `profile`, `content` and `activity` folders, and you can ask Claude anything about it.

More: [SETUP.md, step 6](SETUP.md#step-6-run-the-build) — running it yourself, and [Structure after the build](#structure-after-the-build) — what goes where.

### Later: updating with fresh data

> ⚠️ **The project is a snapshot of your current LinkedIn data.** Every update deletes `profile/`, `content/` and `activity/` completely and builds them again from scratch. **All changes you made in these folders, and any files you added there, will be lost.** Keep your own files (notes, drafts, plans) in a separate folder.

Repeat steps 2–3 to get a new archive, then ask Claude:

> Rebuild the project with the new archive.

More: [SETUP.md, Updating the data](SETUP.md#updating-the-data).

---

Something went wrong? See the Troubleshooting section in **[SETUP.md](SETUP.md#troubleshooting)**.

---

## Structure after the build

```
<project>/
├── CLAUDE.md          rules for Claude
├── README.md          this file
├── SETUP.md           detailed setup guide
├── scripts/
│   └── build.py       build script
├── raw/               source archive (not worked with directly)
├── profile/           information about the profile owner
│   └── linkedin_view/ what LinkedIn itself inferred about the owner
├── content/           what the owner wrote
│   ├── posts/
│   ├── articles/
│   └── comments/
└── activity/          people, actions, jobs
    ├── network/
    │   └── messages/
    ├── actions/
    └── jobs/
```

### profile/

Short tables are the CSV files from the export. Files with long texts are converted to markdown.

| File | Contents | Source in the archive |
|---|---|---|
| profile.md | name, headline, About, location, websites | Profile.csv |
| positions.md | experience | Positions.csv |
| projects.md | projects | Projects.csv |
| education.csv | education | Education.csv |
| certifications.csv | certifications | Certifications.csv |
| organizations.csv | organizations | Organizations.csv |
| skills.csv | skills | Skills.csv |
| endorsements_received.csv | skill endorsements received | Endorsement_Received_Info.csv |
| causes.csv | causes | Causes You Care About.csv |
| verifications.csv | verifications (email column removed) | Verifications/Verifications.csv |
| linkedin_view/inferences.csv | LinkedIn's inferences about the owner | Inferences_about_you.csv |
| linkedin_view/ad_targeting.csv | ad targeting attributes, one row per value (`Category,Value`); categories that repeat company follows and education are removed | Ad_Targeting.csv |

### content/

| Folder | Contents | Source |
|---|---|---|
| posts/ | Posts — each in its own file `YYYY-MM-DD_beginning-of-post.md`, with a link to LinkedIn. Index in `posts/README.md` | Shares.csv |
| articles/ | Articles in markdown. Index in `articles/README.md` | Articles/ |
| comments/ | Comments — one file per month `YYYY-MM.md`. Index in `comments/README.md` | Comments.csv |

### activity/

| Folder | Contents | Source |
|---|---|---|
| network/ | connections, invitations, member_follows, company_follows | Connections, Invitations, Member_Follows, Company Follows |
| network/messages/ | Conversations — one file per conversation `YYYY-MM-DD_with-whom.md` (date of the first message). Index in `messages/README.md` | messages.csv |
| actions/ | reactions, reposts, votes, saved_items, search_queries, events, learning, endorsements_given | Reactions, InstantReposts, Votes, Saved_Items, SearchQueries, Events, Learning, Endorsement_Given_Info |
| jobs/ | applications, saved_jobs, screening_answers | Jobs/, Job Applicant Saved Screening Question Responses |

## What the script does not copy

These archive files stay in `raw/` only:

- **Personal data:** Private_identity_asset, PhoneNumbers, Email Addresses, Whatsapp Phone Numbers, Registration, Receipts_v2, Logins, Security Challenges.
- **Empty or technical:** Notes, SavedJobAlerts, Profile Summary, Job Seeker Preferences, Job Applicant Saved Answers, LAN Ads Engagement, Ads Clicked, learning/coach/guide messages.
- **Rich_Media.csv** — a log of uploaded media; post texts are taken from Shares.csv.

## Privacy

The `raw/`, `profile/`, `content/` and `activity/` folders contain personal data and are excluded from git via `.gitignore`. Do not remove these lines from `.gitignore` if you plan to publish your copy of the project.
