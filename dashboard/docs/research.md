# What an MCP usage dashboard should show (research, 2026-11-21)

Condensed from four research passes. Sources were read directly unless marked.

## Anthropic

- No server-side dashboard guidance or targets. What they measure themselves: Claude Code's `tool_result` event records `tool_name`, `success`, `duration_ms`, `error_type`, input and result size; spans add `result_tokens`. Unit: calls, success rate, duration, result size, per tool. https://code.claude.com/docs/en/monitoring-usage
- "Writing effective tools for agents": track runtime per call, number of calls, tokens, tool errors. Many invalid-parameter errors mean the descriptions need work; many redundant calls mean pagination or limits need resizing. https://www.anthropic.com/research/writing-tools-for-agents
- MCP spec: protocol errors (unknown tool, malformed) vs `isError` tool results; `clientInfo` for telemetry only, never authorization; log cancellation reasons. https://modelcontextprotocol.io/specification/2025-11-25/server/tools
- Client limits: claude.ai tool timeout 240 s, results about 150,000 characters; Claude Code warns over 10,000 tokens, default cap 25,000 tokens. https://claude.com/docs/connectors/building, https://code.claude.com/docs/en/mcp
- Directory policy: collect no extraneous conversation data, even for logging; be frugal with tokens. https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy

## OpenAI

- No developer dashboard for published ChatGPT apps; developers build their own. https://community.openai.com/t/is-there-an-analytics-dashboard-for-published-chatgpt-apps/1387666
- The endpoint must "produce logs and metrics for failed initialization and tool calls" and meet latency and availability needs. https://developers.openai.com/plugins/build/mcp-server.md
- Review tool-call analytics weekly; "wrong tool" spikes mean metadata drift. https://developers.openai.com/plugins/guides/optimize-metadata.md
- Alert on anomalous traffic and repeated errors or failed auth. https://developers.openai.com/plugins/guides/security-privacy.md
- Plugins can be removed if "inactive, unstable, or non-compliant"; contract drift is re-checked. https://developers.openai.com/plugins/deploy/app-review.md
- Codex defaults: tool timeout 60 s, startup 10 s. https://developers.openai.com/codex/mcp.md
- Privacy: no tracking of timestamps, IPs or query patterns unless disclosed and narrowly scoped (guideline 4.3). https://developers.openai.com/plugins/plugin-guidelines.md

## MCP analytics products (PostHog MCP Analytics, mcpspan, TrackMCP, AgentCat, MCP Tower, Shinzo, Grafana #25252, Glean, Datadog)

- Consensus: calls per tool over time, error rate overall and per tool, p50/p95/p99 per tool, client breakdown, error classes beyond yes/no, a time-range filter.
- Worth copying: split bad arguments from tool failures (PostHog's leaderboard: 82.6% of failures were bad arguments); which argument failed, never its value (mcpspan); tools advertised but never called (PostHog, TrackMCP, mcpspan); release markers on charts and per-release comparison (mcpspan); "silent failures" that are HTTP 200 with `isError` (TrackMCP); an "Other" client bucket as a signal the labelling needs work; estimates kept apart from counts (MCP Tower).

## Dashboard design

- Lead with symptoms (RED: rate, errors, duration), then saturation (quotas, limiter). https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/, https://sre.google/sre-book/monitoring-distributed-systems/
- Latency as a distribution, never only a mean. Same SRE chapter.
- Every number needs a comparison, as a direct percent change (pitfalls 2 and 4); round (pitfall 3); no gauges or pies. https://www.perceptualedge.com/articles/Whitepapers/Common_Pitfalls.pdf
- Bullet graph for quota against limit and pace. https://www.perceptualedge.com/articles/misc/Bullet_Graph_Design_Spec.pdf
- Hour-of-day heatmap, always with counts nearby. https://www.honeycomb.io/blog/heatmaps-make-ops-better
- Small counts: show "3 of 9", not "33%".
- Table first, click for detail; upstream services as a table (Vercel External APIs). https://vercel.com/docs/observability
- An events strip (restarts, version changes, quota trouble) like Stripe Workbench's health history. https://docs.stripe.com/workbench/health
- Colour sparingly: neutral unless something needs action; never colour alone.

## What this data can't show

Session ids, tool sequences, retries after failure, reply sizes and tokens, model names and per-person counts: the server keeps none of them (by design: no IPs, no caller ids). `callers` counts distinct IPs per day, and hosted apps call from shared IPs.
