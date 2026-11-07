# Working rules

- Do only what the user has agreed to and confirmed.
- Before any action that changes the project (creating, moving, editing or deleting files), describe the plan first and wait for explicit confirmation.
- Answer only the question asked. Do not draw conclusions, give recommendations or suggest a strategy unless asked.
- Record any user requirements in this file (CLAUDE.md), not in Claude's memory.

# Project requirements

- The project structure is described in README.md.
- Never modify the source export in `raw/`. We do not work with `raw/` — it is the source the project is built from.
- Do not look into `raw/` or read files from it unless the user explicitly asks. All working information is in `profile/`, `content/`, `activity/`.
- There are three working folders built from the export: `profile/`, `content/`, `activity/`.
- `profile/` — all information about the profile owner (not only what is visible on the profile page). Short tables are kept as the original CSV files. Anything hard to read as CSV is converted to markdown or a more readable table (without keeping a duplicate of the original CSV).
- `profile/linkedin_view/` — what LinkedIn itself inferred about the profile owner (Inferences, Ad_Targeting).
- `content/` — what the profile owner wrote: posts, articles, comments.
- `activity/` — people (`network/`), actions (`actions/`), job search (`jobs/`).
- Do not duplicate information within the project: every file lives in one place.
- Store each post in a separate file in `content/posts/`.
- Store comments by month: one file per month in `content/comments/`.
- Store each conversation in a separate file in `activity/network/messages/`.
- File names in the working folders are lowercase, words separated by `_` (e.g. `endorsements_received.csv`).
- Do not put obvious information such as file counts into README — only structure and rules.
- The working folders are built by `scripts/build.py`. Make structural changes in the script, not by hand in the generated files.

# Building the project

The user may not be technical. When they ask to build or rebuild the project:

1. Check that `python3` (or `python` on Windows) is available and is version 3.8+. If not, explain in plain words how to install it from python.org.
2. Check that `raw/` contains an unpacked folder with `LinkedInDataExport` in its name. If not, explain where to put the archive (README.md, step 3).
3. Run `python3 scripts/build.py` from the project root. It uses the newest archive in `raw/`. For a rebuild (the working folders already exist), run it only after the user has confirmed, with `--yes` — the script cannot ask for confirmation when Claude runs it.
4. Report the result in plain words: which archive was used and what was built. If the script stops with an error, explain what it means and what the user should do (see the Troubleshooting table in SETUP.md).

Running the build is the agreed action in this case — no separate plan is needed. Before a **rebuild**, warn that the project is a snapshot of the current export: `profile/`, `content/` and `activity/` will be deleted completely and built again, so all changes and any files the user added there will be lost — their own files must be kept in a separate folder. Wait for confirmation.
