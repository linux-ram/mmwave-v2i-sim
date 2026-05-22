# One-time GitHub publish steps

Automated script: `bash scripts/publish_v0.1.sh`

## 1. Authenticate

```bash
brew install gh   # if needed
gh auth login
```

Choose GitHub.com, HTTPS or SSH, and grant access to the **linux-ram** organization.

## 2. Run publish script

```bash
cd /path/to/mmwave-v2i-sim
bash scripts/publish_v0.1.sh
```

This will:

- Create or push to `linux-ram/mmwave-v2i-sim`
- Tag and release **v0.1.0**
- Open three post-v0.1 tracking issues (m5, m6, m9) if they do not already exist

## 3. Manual fallback (no `gh`)

1. Create https://github.com/linux-ram/mmwave-v2i-sim (public, empty).
2. `git remote add origin git@github.com:linux-ram/mmwave-v2i-sim.git`
3. `git push -u origin main && git push origin v0.1.0`
4. Create release v0.1.0 from `docs/RELEASE_NOTES_v0.1.md`

## 4. Verify

- CI green: [Actions](https://github.com/linux-ram/mmwave-v2i-sim/actions) (README badge may cache ~5 minutes after a failed run)
- Fresh clone: `git clone ... && pip install -r requirements-lock.txt && pip install -e ".[dev,gui]" && pytest`
