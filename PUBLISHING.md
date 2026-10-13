# Publishing to `ivanpark/team-unicorn`

**Prepared, not yet uploaded.** The currently connected GitHub integration supports commits to an existing repository but **does not expose a create-repository operation**. At packaging time `ivanpark/team-unicorn` returned GitHub `404`. Nothing was pushed to `ivanpark/hmbr`.

## Option 1: Create the new repository in GitHub, then push

1. Log in to `ivanpark` and visit https://github.com/new . Set the repository name to `team-unicorn`, choose **Private** or **Public** deliberately, and **do not initialise** with README, licence or .gitignore (they are already here).
2. Unzip the release archive locally, open Terminal at the `Team_Unicorn_v0.7_Repo_Ready` directory and run:

```bash
git init -b main
git add .
git commit -m "Initial Team Unicorn research release v0.7"
git remote add origin https://github.com/ivanpark/team-unicorn.git
git push -u origin main
```

If GitHub authentication is required, use an approved SSH/credential-manager configuration, never commit secrets or use an account password.

## Option 2: GitHub CLI (single repository creation + push workflow)

If `gh` is installed and authenticated on your computer:

```bash
git init -b main
git add .
git commit -m "Initial Team Unicorn research release v0.7"
gh repo create ivanpark/team-unicorn --private --source . --remote origin --push
```

Change `--private` to `--public` only if you intend to make the research/code available to everyone. Note that the experimental archives are public under that choice; no licence is provided by default.

## Publish checks

```bash
python3 scripts/verify_release.py
git status --short
```

The package intentionally excludes the private local Canon DB and nonproject personal materials. Contents of historical simulation files are retained as authored.
