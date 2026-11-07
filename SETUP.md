# Step-by-step setup guide

From an empty folder to a ready project. About 15 minutes of work plus up to a day of waiting for the LinkedIn archive.

---

## Step 1. Get the template

**Option A — without git (easier):**

1. Open the repository page on GitHub.
2. Click the green **Code** button → **Download ZIP**.
3. Unpack the archive:
   - **macOS:** double-click the `.zip` file;
   - **Windows:** right-click the file → **Extract All**.
4. Move the unpacked folder to where you want to work with it and rename it if you like, e.g. `LinkedIn`.

**Option B — with git:**

```bash
git clone <repository URL> LinkedIn
```

The folder should contain: `README.md`, `SETUP.md`, `CLAUDE.md`, `.gitignore` and the `scripts/` folder.

> `.gitignore` is a hidden file. In Finder you can show hidden files with `Cmd + Shift + .` (period).

---

## Step 2. Request your data archive from LinkedIn

Do this in a desktop browser (the mobile app has a different path that changes more often).

1. Open [linkedin.com](https://www.linkedin.com) and sign in.
2. In the top right, click your photo (**Me**) → **Settings & Privacy**.
3. On the left, select **Data privacy**.
4. In the **How LinkedIn uses your data** section, click **Get a copy of your data**.

   Direct link: [linkedin.com/mypreferences/d/download-my-data](https://www.linkedin.com/mypreferences/d/download-my-data)
5. Select the **top option** — the full archive:
   > **Download larger data archive, including connections, verifications, contacts, account history, and information we infer about you based on your profile and activity.**

   Do not pick individual categories (the second option) — that archive will not include posts and comments.
6. Click **Request archive**.
7. Enter your LinkedIn password if asked.

---

## Step 3. Wait for and download the archive

LinkedIn sends **two emails** to your account's email address:

| Email | Arrives | File | Suitable? |
|---|---|---|---|
| First | after about 10 minutes | `Basic_LinkedInDataExport_….zip` | ❌ no posts or comments |
| Second | within 24 hours | `Complete_LinkedInDataExport_….zip` | ✅ this is the one you need |

1. Wait for the **second** email.
2. Follow the link in the email, or open the **Get a copy of your data** page from step 2 again — a **Download archive** button will appear there.
3. Click it and enter your password if asked. The file `Complete_LinkedInDataExport_MM-DD-YYYY.zip` will be saved to your Downloads folder.

> The download link is valid for a limited time (usually about 72 hours). If you miss it, request the archive again.

**How to check the archive is complete:** after unpacking, it must contain `Shares.csv`. If it does not, this is the Basic archive — wait for the second email.

### LinkedIn export limitations

- The export contains no post statistics (reach, reactions, other people's comments).
- Reactions, reposts and saved items are links only, without text.
- Message attachments are only counted; the files themselves are not part of the export.
- The Basic archive has no posts or comments, and in `Rich_Media.csv` emoji and "bold" Unicode text are replaced with `?`. That is why you need the Complete archive.

---

## Step 4. Put the archive into the project

1. In the project root (next to `README.md`), create a folder named **`raw`**.
2. Unpack the downloaded archive:
   - **macOS:** double-click — a folder with the same name appears next to it;
   - **Windows:** right-click → **Extract All**.
3. Move the **unpacked folder** into `raw/`.

The result should look like this:

```
LinkedIn/
├── README.md
├── SETUP.md
├── CLAUDE.md
├── scripts/
│   └── build.py
└── raw/
    └── Complete_LinkedInDataExport_MM-DD-YYYY/
        ├── Profile.csv
        ├── Shares.csv
        ├── Comments.csv
        ├── messages.csv
        └── …
```

> Important: the CSV files must be **directly inside** the archive folder, not one level deeper. If you end up with `raw/Complete_…/Complete_…/Profile.csv`, move the inner folder one level up.

> On macOS the unpacked folder sometimes keeps `.zip` at the end of its name (e.g. `Complete_LinkedInDataExport_MM-DD-YYYY.zip`). That is fine — the script will find it.

---

## Step 5. Open the project in Claude Code

1. Install Claude Code following the instructions at [claude.com/claude-code](https://claude.com/claude-code). It is available as a desktop app (easiest), a VS Code / JetBrains extension and a terminal app.
2. Open the project folder:
   - **desktop app:** open Claude Code and choose your `LinkedIn` folder as the project;
   - **VS Code:** **File → Open Folder…** → select the project folder → open the Claude Code panel;
   - **terminal:** go to the project folder (see step 6, option B) and run `claude`.
3. Claude automatically reads `CLAUDE.md` and follows its rules: do only what is agreed, show a plan first, stay out of `raw/` unless asked.
4. Ask Claude to record your own project requirements in `CLAUDE.md` so they persist across sessions.

---

## Step 6. Run the build

### Option A — ask Claude (recommended)

Type in the Claude Code chat:

> Build the project from my LinkedIn archive.

Claude checks that Python is installed and the archive is in place, runs the build and tells you the result in plain words. If it asks for permission to run a command, click **Allow**.

### Option B — run it yourself in a terminal

**1. Check Python.** The script needs Python 3.8 or newer; no extra libraries are required.

1. Open a terminal:
   - **macOS:** `Cmd + Space` → type **Terminal** → `Enter`;
   - **Windows:** **Start** menu → type **cmd** or **PowerShell** → `Enter`.
2. Run:
   ```bash
   python3 --version
   ```
   On Windows, if the command is not found, try `python --version`.
3. If the output says `Python 3.8` or higher, you are all set.
   If the command is not found or the version is older, install Python from [python.org/downloads](https://www.python.org/downloads/). On Windows, check **Add Python to PATH** during installation.

**2. Run the script.**

1. Go to the project folder. The easiest way: type `cd ` (with a trailing space) and drag the project folder from Finder / Explorer into the terminal window — the path is filled in automatically. Press `Enter`.
   ```bash
   cd "/path/to/LinkedIn"
   ```
2. Run:
   ```bash
   python3 scripts/build.py
   ```
   (on Windows you may need `python scripts/build.py`)

   The script uses the newest archive in `raw/`. To use a specific one, pass its folder as an argument:
   ```bash
   python3 scripts/build.py raw/Complete_LinkedInDataExport_MM-DD-YYYY
   ```
3. At the end the script prints which archive it used and how many posts, comments, articles and conversations it built, for example:
   ```
   Archive: raw/Complete_LinkedInDataExport_MM-DD-YYYY
   conversations: 250
   posts: 40 empty: 0 comment months: 12 articles: 3
   ```

The project now has `profile/`, `content/` and `activity/` folders. See [README.md](README.md#structure-after-the-build) for what goes where.

---

## Updating the data

> ⚠️ **The project is a snapshot of your current LinkedIn data.** Every update deletes `profile/`, `content/` and `activity/` completely and builds them again from scratch. **All changes you made in these folders, and any files you added there, will be lost.** Keep your own files (notes, drafts, plans) in a separate folder.

When you want to refresh the project with new data:

1. Request and download a new Complete archive (steps 2–3).
2. Unpack it into `raw/` next to the old one (you can delete the old one).
3. Ask Claude: *Rebuild the project with the new archive.* — or run `python3 scripts/build.py` yourself. The script picks the newest archive.
4. Confirm the rebuild. The script lists the folders that will be deleted and rebuilt, and asks `Continue? [y/N]` — type `y` and press `Enter`. To skip the question, run `python3 scripts/build.py --yes`.

---

## Troubleshooting

| Message / situation | What to do |
|---|---|
| `No LinkedIn archive (*LinkedInDataExport*) found in raw/` | Check that the folder is named `raw`, sits in the project root, and contains an unpacked folder with `LinkedInDataExport` in its name |
| `Shares.csv not found - this is the Basic archive…` | Wait for the second email and download the Complete archive |
| `Profile.csv not found in the archive folder…` | The CSV files are one level deeper — see the note in step 4 |
| `python3: command not found` | Install Python (step 6, option B) or try the `python` command |
| `can't open file 'scripts/build.py'` | The terminal is not in the project folder — run the `cd` command from step 6, option B |
| The second email has not arrived within a day | Check your Spam folder, then the **Get a copy of your data** page — the download button appears there too |

---

## Privacy

See [README.md, Privacy](README.md#privacy).
