# Congressional Race Hub

A static landing page for GitHub Pages: links out to your dashboards, plus a
self-updating "news well" of election headlines.

## Files

- `index.html` — the page itself. No build step; GitHub Pages serves it as-is.
- `news.json` — the headline data the page reads. Starts as a placeholder;
  gets rewritten automatically (see below).
- `scripts/fetch_news.py` — pulls headlines from Google News RSS (no API key
  needed) and writes `news.json`.
- `.github/workflows/update-news.yml` — a GitHub Action that runs the script
  on a schedule and commits the updated `news.json`.

## One-time setup

1. Create a new GitHub repo (or use an existing one) and add all these files,
   preserving the folder structure — `.github/workflows/update-news.yml` must
   stay in that exact path.
2. In the repo's **Settings → Pages**, set the source to your default branch
   (root folder). Your page will be live at
   `https://<username>.github.io/<repo-name>/`.
3. In **Settings → Actions → General → Workflow permissions**, make sure
   "Read and write permissions" is selected. This lets the Action commit the
   updated `news.json` back to the repo.
4. That's it — the Action will run every 6 hours automatically. To run it
   immediately instead of waiting: go to the **Actions** tab → "Update News
   Well" → **Run workflow**.

## Editing what the news well tracks

Open `scripts/fetch_news.py` and edit the `QUERIES` list near the top:

```python
QUERIES = [
    "2026 congressional election",
    "2026 midterm elections House",
    "2026 Senate race",
]
```

Add, remove, or narrow these (e.g. `"AZ-01 congressional race"`) to change
what shows up. Commit the change, and the next scheduled (or manual) run will
use the new queries.

## Adding more dashboard links

Open `index.html` and find the `Dashboards & Tools` section. Copy an existing
`<a class="card">` block, then edit the `href`, eyebrow label, title, and
description. There's a dashed placeholder card at the end showing where to
add the next one.

## Changing update frequency

Open `.github/workflows/update-news.yml` and edit the cron line:

```yaml
- cron: "0 */6 * * *"   # every 6 hours
```

Cron schedules are in UTC. For example, `"0 */3 * * *"` runs every 3 hours,
`"0 12 * * *"` runs once daily at noon UTC.

## Testing locally (optional)

```bash
python scripts/fetch_news.py
```

This overwrites `news.json` in place using your current queries — useful for
previewing before you commit.
