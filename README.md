# App Builder Repo (multi-language, auto-skip, HTML support, auto output/)

Builds a Windows .exe and/or Android .apk automatically from whatever
project you drop into source/ -- Python, .NET/C#, C/C++ (CMake), Android
Studio (Gradle), or plain HTML/CSS/JS.

## What's new in this update

1. Auto-skip instead of fail: if source/ only has an Android project, the
   Windows job detects "unknown", skips its build steps, and finishes
   green (no red X) -- it simply produces no .exe. Same in reverse.
2. HTML/web project support: if source/ has an index.html and nothing else
   recognized, it gets wrapped with Electron (portable .exe) for Windows and
   Capacitor (WebView app) for Android, producing a real .apk via Gradle.
3. Auto-copy to output/: after a successful build, the release job now
   copies the finished .exe/.apk directly into the repo's output/ folder
   and commits it back to main automatically -- so besides the Releases
   tab, you can also just browse to output/ in the repo and download the
   latest build directly, no separate step needed.

## Files to upload to GitHub for this update

Only ONE file changed: .github/workflows/build.yml
Replace that file in your existing repo (edit in place or Add file ->
Upload files with the same name) -- nothing else needs to change.

## The source/ folder -- supported project types

- Python: main.py + requirements.txt (+ optional buildozer.spec)
- .NET/C#: any *.csproj
- C/C++: CMakeLists.txt
- Android Studio: gradlew + settings.gradle (must include Gradle wrapper)
- HTML/web: index.html (wrapped automatically, no changes needed)

## Running a build

Actions tab -> "Build PC EXE and Android APK" -> Run workflow -> set
app_name / entry_file -> Run workflow. Results appear in:
  - Releases tab (tag build-<run_number>), AND
  - output/ folder in the repo itself (auto-committed after each build)
