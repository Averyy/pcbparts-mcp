# Running it online (stats.pcbparts.dev)

The dashboard runs on the same VPS as `pcbparts-mcp`, as its own small container behind the existing Caddy, with a password.

## How it ships

- CI (`.github/workflows/docker-build.yml`) builds `ghcr.io/averyy/pcbparts-mcp-dashboard` from `dashboard/` next to the server's image, and `.github/workflows/tests.yml` runs its tests.
- `docker-compose.yml` has a `pcbparts-dashboard` service: no published port (Caddy reaches `pcbparts-dashboard:8050` on the `web` network), a named volume `pcbparts-dashboard-data` for the SQLite store, 256 MB.
- The deploy updates `pcbparts-mcp` first and the dashboard after it, separately: a failed pull or start of the dashboard never holds up the server.
- The container refuses to start without `DASHBOARD_PASSWORD` (HTTP Basic auth, user `admin` unless `DASHBOARD_USER` is set).
- It reads `https://pcbparts.dev/mcp/stats` and `/health` like any caller: one request an hour, far under the per-address limit, and `/mcp/stats` requests aren't tool calls. (Polling `http://pcbparts-mcp:8080` directly would need `pcbparts-mcp` added to the server's `MCP_ALLOWED_HOSTS`: fastmcp's host guard answers 421 to any other `Host` on every route.)

## One-time setup on the VPS

1. DNS: an A (and AAAA, if the site has one) record for `stats.pcbparts.dev` pointing at the VPS.
2. In `/root/pcbparts-mcp/.env` (already holds `STATS_TOKEN`), add:
   ```
   DASHBOARD_PASSWORD=<a long random password>
   ```
   Optional: `DASHBOARD_PROBLEMS_SINCE=<ISO time>` and `DASHBOARD_PROBLEMS_VERSION=<version>` to fix where problems start counting. Without them a new store counts problems from its first check, and the dashboard moves that point itself whenever `/health` reports a new version.
3. Caddy: add a site block and reload Caddy.
   ```
   stats.pcbparts.dev {
       reverse_proxy pcbparts-dashboard:8050
   }
   ```
   Caddy gets the certificate on its own. Caddy's own `basic_auth` can be added in front as a second lock.
4. After the first deploy with the dashboard, check the image is pullable: GitHub may create the new `pcbparts-mcp-dashboard` package as private. If the deploy log says "Usage dashboard image not pulled", make the package public (GitHub, Packages, package settings) or `docker login ghcr.io` on the VPS, then run `docker compose pull pcbparts-dashboard && docker compose up -d pcbparts-dashboard` in `/root/pcbparts-mcp`.

## Keeping the history collected so far (optional)

A new store fetches the last 365 server days on its first poll; only the dashboard's own hourly snapshots would be missing. To keep them, copy a local store over once:

```
# locally: a consistent copy of the store
sqlite3 data/dashboard.db ".backup /tmp/dashboard.db"
scp /tmp/dashboard.db <vps>:/tmp/dashboard.db

# on the VPS, in /root/pcbparts-mcp
chmod 644 /tmp/dashboard.db
docker compose stop pcbparts-dashboard
docker compose run --rm --no-deps -v /tmp/dashboard.db:/import.db:ro --entrypoint sh pcbparts-dashboard \
  -c 'cp /import.db /app/data/dashboard.db && chmod 600 /app/data/dashboard.db'
docker compose up -d pcbparts-dashboard
rm /tmp/dashboard.db
```

Then stop the local copy (`pcbparts-dashboard serve`), so only one poller runs.

## Load

One Python process (about 30-40 MB), a SQLite file growing a few MB a year, and no work between polls except serving the page.

## Backups

The store keeps days the server has already dropped (the server keeps 365 days, and clears `tool_apps`, `latency` and `popular_terms` after 30). Back up the `pcbparts-dashboard-data` volume like `pcbparts-cache`.
