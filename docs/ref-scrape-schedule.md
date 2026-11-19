# Daily scrape schedule

The JLCPCB catalog scrape (`.github/workflows/scrape-components.yml`) must run every morning: since
0.10.2 `jlc_get_part` answers from the snapshot by default, so the snapshot's age is what users see.

GitHub's own schedule isn't reliable enough for that. In November 2026 its scheduled runs started 6
to 10 hours late and one day (2026-11-17) didn't run at all. So the scrape is started from outside:

- **Primary:** a cron job on the server starts the workflow through GitHub's `workflow_dispatch` API
  at a fixed time.
- **Backup:** the workflow's own `schedule` (12:21 UTC) still fires. Its `check` job skips the scrape
  when `data/manifest.json` on `main` already has that UTC day's `scraped_at`, so a late backup run
  never scrapes twice.

`/health` shows the snapshot's age (`snapshot.age_hours`) and `snapshot.stale: true` once it is over
30 hours old: check it if answers look out of date.

## Setting up the server's cron job

**If the server already has the GitHub CLI logged in** (`gh auth status` shows the `repo` scope), no
new token is needed. Use `gh`'s full path, since cron has a minimal `PATH` (`which gh`):

```cron
CRON_TZ=UTC
30 11 * * * /usr/bin/gh workflow run scrape-components.yml --repo OWNER/REPO --ref main >> /var/log/pcbparts-scrape-trigger.log 2>&1
```

That login can do much more than start a workflow. For a credential that can do only that, use a
dedicated token instead:

1. **Create a token** at GitHub → Settings → Developer settings → Fine-grained tokens:
   - Repository access: only this repository.
   - Permissions: **Actions: Read and write** (nothing else).
   - Expiry: your choice; put a reminder in your calendar, since an expired token stops the trigger
     (the backup schedule then takes over, late).
2. **Store it on the server**, readable by root only:

   ```bash
   umask 077 && printf '%s' 'github_pat_...' > /root/.pcbparts-scrape-token
   ```

3. **Add the cron entry** (`crontab -e` as root). `CRON_TZ=UTC` makes the time independent of the
   server's time zone; 11:30 UTC is 6:30 AM EST, and the scrape and deploy take about 35 minutes:

   ```cron
   CRON_TZ=UTC
   30 11 * * * curl -fsS -X POST -H "Authorization: Bearer $(cat /root/.pcbparts-scrape-token)" -H "Accept: application/vnd.github+json" https://api.github.com/repos/OWNER/REPO/actions/workflows/scrape-components.yml/dispatches -d '{"ref":"main"}' >> /var/log/pcbparts-scrape-trigger.log 2>&1 || echo "$(date -u +\%FT\%TZ) trigger failed" >> /var/log/pcbparts-scrape-trigger.log
   ```

   Replace `OWNER/REPO` with the repository. A successful trigger prints nothing (HTTP 204).
4. **Test it once by hand:** run the `curl` command from the entry, then look for a new
   "Scrape JLCPCB Components" run with the event `workflow_dispatch` under the repository's Actions.

The token can only start, cancel and read workflow runs in this one repository. It cannot push code
or read secrets.
