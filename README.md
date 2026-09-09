# App Builder Repo (PC .exe + Android .apk)

Automatically builds a Windows `.exe` and an Android `.apk` from Python
source you place in the `source/` folder — either as **loose files** or as
a **single zip**. No admin panel required to use it.

## The `source/` folder — two supported ways to add your project

**Way 1 — loose files (recommended for the web UI):**
Go to `source/` on GitHub → **Add file → Upload files** → drag your whole
project folder in (GitHub preserves the folder structure). Put `main.py`,
`requirements.txt`, assets, and optionally `buildozer.spec` directly inside
`source/`.

**Way 2 — a single zip:**
Drop one `.zip` containing your project (with `main.py` at its root) into
`source/`. The workflow auto-detects a lone zip and extracts it before
building — you don't have to do anything else.

The workflow checks `source/` for exactly one `.zip` file first; if it finds
one, it extracts it. Otherwise it copies everything in `source/` as-is. If
neither produces the entry file you specified, **the build fails immediately
with a clear error** instead of wasting 20+ minutes on a broken build.

## How to run a build

1. Add your project to `source/` (either way above) and commit.
2. Go to the **Actions** tab → **Build PC EXE and Android APK** → **Run
   workflow** → set `app_name` and `entry_file` (default `main.py`) → **Run
   workflow**.
3. Wait for the three jobs (`build-windows`, `build-android`, `release`) to
   finish — Android takes 15-25 minutes on a fresh runner, Windows is much
   faster.
4. Download the finished `.exe` and `.apk` from the **Releases** tab, tagged
   `build-<run_number>`.

## Optional: admin panel (upload zip from a web form instead of GitHub's UI)

If you'd rather use a small web form to upload a zip and auto-trigger the
build (instead of using GitHub's own upload UI + Run workflow button), use
`admin_panel/`:

1. Create a GitHub Personal Access Token with `repo` + `workflow` scopes.
2. Copy `admin_panel/.env.example` to `admin_panel/.env` and fill in your
   token, `REPO_OWNER`, `REPO_NAME`.
3. `cd admin_panel && pip install -r requirements.txt && python app.py`
4. Open `http://localhost:5000`, upload a zip, and track `/status`.

This is entirely optional — Way 1 and Way 2 above work without running any
extra server.

## What your project needs

- `main.py` (or any entry file name you specify in the workflow input)
- `requirements.txt` — Python dependencies (e.g. `kivy` for cross-platform)
- Optional `buildozer.spec` — if missing, `buildozer.spec.default` is used
  automatically and renamed to your chosen app name
- Any assets (images, `.kv` files, fonts) your app references

## Notes on reliability ("kono fail sara")

- The workflow validates that your entry file actually exists in `source/`
  before spending any build time — if it's missing, the run fails in
  seconds with a clear message instead of a mysterious 20-minute failure.
- After building, it also verifies the `.exe`/`.apk` was actually produced
  before uploading artifacts, catching silent build failures early.
- This setup assumes a **Python (Kivy) project**, since that's the one
  codebase Buildozer (Android) and PyInstaller (Windows) can both package
  from. If your PC and Android apps are two separate codebases (e.g.
  Electron + native Kotlin), tell me and I'll split this into two independent
  `source/` folders and two workflows.
- Android builds are slower because Buildozer downloads the Android SDK/NDK
  fresh on every run — this is expected GitHub Actions behavior, not a bug.
