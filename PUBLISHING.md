# Publishing status

The public repository was created by the owner, and the project metadata files `README.md`, `README.ko.md` and `CHANGELOG.md` have been committed to `main`.

**Important:** The PDFs, DOCX files, original blueprint, simulation HTML, Python source code, and result datasets are **not yet uploaded**. The README links to these paths as the planned final repository layout.

The complete prepared release bundle is `Team_Unicorn_v0.7_Repo_Ready_Complete.zip` (available from the ChatGPT conversation).

To publish all assets from a computer with Git credentials:

```bash
git clone https://github.com/ivanpark/team-unicorn.git
unzip -q ~/Downloads/Team_Unicorn_v0.7_Repo_Ready_Complete.zip -d /tmp/team-unicorn-release
cp -a /tmp/team-unicorn-release/Team_Unicorn_v0.7_Repo_Ready/. ./team-unicorn/
cd team-unicorn
python3 scripts/verify_release.py
git add .
git commit -m "Publish full Team Unicorn v0.7 research release"
git push origin main
```

Adjust ZIP location if different. The repository is public and has no software licence yet.
