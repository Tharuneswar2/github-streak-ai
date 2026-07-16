# Troubleshooting

## Common Issues

### `NVIDIA_API_KEY is not set`

**Problem:** AI features are disabled because no API key is configured.

**Solution:**
1. Copy the env template: `cp .env.example .env`
2. Get a key from [build.nvidia.com](https://build.nvidia.com/)
3. Add it to `.env`: `NVIDIA_API_KEY=nvapi-xxxx...`

---

### `Authentication failed (HTTP 401)`

**Problem:** The API key is invalid or expired.

**Solution:**
- Verify your key at [build.nvidia.com](https://build.nvidia.com/)
- Regenerate if expired
- Ensure no extra whitespace in `.env`

---

### `Model or endpoint not found (HTTP 404)`

**Problem:** The configured model doesn't exist.

**Solution:**
- Check available models at [build.nvidia.com/explore/discover](https://build.nvidia.com/explore/discover)
- Update `MODEL` in `.env` to a valid model identifier

---

### `No git repository found`

**Problem:** Git statistics require an initialized repository.

**Solution:**
```bash
git init
git add .
git commit -m "Initial commit"
```

---

### `ModuleNotFoundError: No module named 'config'`

**Problem:** Python can't find the project modules.

**Solution:**
- Ensure you're running from the project root directory
- Install in editable mode: `pip install -e .`
- Or add the project root to `PYTHONPATH`

---

### `Template not found`

**Problem:** Jinja2 templates are missing from the `templates/` directory.

**Solution:**
- Verify the `templates/` directory exists and contains `.j2` files
- The system will fall back to built-in templates if Jinja2 templates are missing

---

### `Request timed out`

**Problem:** The NVIDIA API is slow or unreachable.

**Solution:**
- Check your internet connection
- The client retries 3 times automatically
- Try again in a few minutes
- Check [NVIDIA API status](https://status.nvidia.com/)

---

### `Permission denied` on log files

**Problem:** File system permissions prevent writing.

**Solution:**
```bash
chmod -R u+rw logs/ reports/
```

---

### Tests fail with `LogNotFoundError`

**Problem:** Tests require populated log fixtures.

**Solution:**
- Tests use temporary directories — ensure pytest fixtures are loaded
- Run tests from the project root: `pytest tests/ -v`

---

## GitHub Actions Issues

### Workflow doesn't trigger

**Check:**
- Workflow files are in `.github/workflows/`
- Branch name matches (default: `main`)
- YAML syntax is valid

### Reports not auto-committing

**Check:**
- The workflow has `contents: write` permission
- `NVIDIA_API_KEY` is set in GitHub Secrets
- There are actual content changes (empty commits are skipped by design)

### Reminder issues not created

**Check:**
- The workflow has `issues: write` permission
- The cron schedule is correct (default: 22:00 UTC daily)

---

## Getting Help

1. Check the [FAQ](FAQ.md)
2. Search [existing issues](https://github.com/yourusername/github-streak-ai/issues)
3. Open a [new issue](https://github.com/yourusername/github-streak-ai/issues/new)
