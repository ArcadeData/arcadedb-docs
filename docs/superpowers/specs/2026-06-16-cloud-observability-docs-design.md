# Cloud Observability Documentation — Design Spec

**Date:** 2026-06-16
**Branch:** `docs/observability-4463`
**Tracks:** [arcadedb#4463](https://github.com/ArcadeData/arcadedb/issues/4463) (parent) and sub-issues
[#4464](https://github.com/ArcadeData/arcadedb/issues/4464) (health probes),
[#4465](https://github.com/ArcadeData/arcadedb/issues/4465) (metrics depth),
[#4466](https://github.com/ArcadeData/arcadedb/issues/4466) (structured logging),
[#4467](https://github.com/ArcadeData/arcadedb/issues/4467) (tracing).

## Goal

Document the Cloud Observability feature set (OpenTelemetry/OTLP, RED metrics depth,
structured JSON logging with correlation IDs, Kubernetes health probes) for
`docs.arcadedb.com` and the PDF manual, sourced from the canonical AsciiDoc tree in
`src/main/asciidoc/`.

All four pillars shipped and merged. This spec documents **what shipped**, verified
against the merged PRs (4473, 4532, 4604, 4639), not the original design spec — several
details drifted during implementation (see "Ground truth & spec drift" below).

## Source of truth (verified against merged code)

Documentation must reflect these verified facts, which differ in places from the
issue text.

### Pillar 4 — Health probes (PR 4473)

- **`GET /api/v1/health`** — new liveness endpoint. Handler `GetHealthHandler`.
  Unauthenticated, **no database I/O**. Returns **`204`** (empty body) whenever the
  HTTP layer is up. It **never returns 503** (a warming-up node must not be killed);
  the only failure mode is the HTTP layer being unreachable (connection refused).
  OpenAPI documents it under tag `Health`, responses 200/204.
- **`GET /api/v1/ready`** — unchanged by default. Server not `ONLINE` → `503`
  `"Server not started yet"`; `ONLINE` → `204`.
- **`arcadedb.server.readinessRequiresHA`** — `Boolean`, default `false`, scope SERVER.
  Description (verbatim): *"When true and HA is active, /api/v1/ready also requires the
  node to have joined the Raft group and be caught up. Default false preserves current
  readiness behavior."* When `true` **and** HA enabled: returns `503`
  `"Node has not yet joined the Raft group"` until the Raft election status is `DONE`
  (a leader is known), else `204`. **Accuracy note:** the check is election=`DONE`
  (leader known), **not** a true commit-index/replication catch-up guarantee — document
  it as "has joined the Raft group (a leader has been elected)", do not promise full
  catch-up.

### Pillar 1 — Metrics depth (PR 4532)

- **Prometheus scrape endpoint is `/prometheus`** (FQN plugin
  `com.arcadedb.metrics.prometheus.PrometheusMetricsPlugin`). The current docs wrongly
  say `/metrics` — **fix this**. Auth gated by raw key
  `arcadedb.serverMetrics.prometheus.requireAuthentication` (default `true`).
- **RED timers — only two shipped** (both `publishPercentileHistogram()`, no explicit
  SLO buckets). There is **no `arcadedb.tx.duration`** timer despite the spec:
  - `arcadedb.http.requests` — tags `method`, `path` (route template, never raw URI),
    `status`, `db`. Prometheus name `arcadedb_http_requests_seconds_*`.
  - `arcadedb.query.duration` — tags `protocol` (`http|bolt|postgres|mongo|grpc|redis|internal`,
    default `internal`), `db`, `language` (`sql|opencypher|gremlin|graphql|mongo`),
    `type` (`query|command`). Prometheus name `arcadedb_query_duration_seconds_*`.
    Query text is never a tag.
- **`EngineMetricsBinder`** (`com.arcadedb.server.monitor.EngineMetricsBinder`) — 14
  **engine-wide** gauges (NO per-database tag; **no sparse-vector gauge**), read from a
  1-second-memoized `Profiler` snapshot:
  `arcadedb.engine.page.cache.hits`, `.page.cache.misses`, `.pages.read`,
  `.pages.written`, `.wal.bytes.written`, `.wal.files`, `.mvcc.conflicts`,
  `.files.open`, `.tx.write`, `.tx.read`, `.tx.rollbacks`, `.queries`, `.commands`,
  `.databases`.
- **Optional OTLP metrics export** — plugin `com.arcadedb.metrics.otlp.OtlpMetricsPlugin`
  (SPI-registered, default off), registers an `OtlpMeterRegistry` alongside (not
  replacing) Prometheus. Keys are **plugin-level raw keys** (not GlobalConfiguration
  enums, so no canonical description string):
  - `arcadedb.serverMetrics.otlp.enabled` — default `false`.
  - `arcadedb.serverMetrics.otlp.endpoint` — default `http://localhost:4317`.
- Coverage caveats to note: Redis commands and unfiltered Mongo scans are not timed by
  `arcadedb.query.duration`.

### Pillar 3 — Structured logging (PR 4639)

- `arcadedb.server.logFormat` — `String`, default `text` (values `text|json`,
  case-insensitive). Description: *"Console log format: 'text' (default, human-readable)
  or 'json' (one JSON object per line with correlation fields)"*.
- `arcadedb.server.logIncludeTrace` — `Boolean`, default `false`. Description: *"In text
  log mode, append [traceId=...] to each line while a trace is active. Default false
  preserves current text output."*
- Formatter `com.arcadedb.log.JsonLogFormatter` (extends `LogFormatter`), built on
  in-tree `com.arcadedb.serializer.json.JSONObject` — **no new dependency**. One JSON
  object per line. Fields in order: `timestamp` (local time `yyyy-MM-dd'T'HH:mm:ss.SSS`,
  **no timezone/Z**), `level`, `logger`, `thread`, `message`, then optional `requestId`,
  `db`, `traceId`, `spanId`, `exception` (full stack trace string).
- Correlation: `requestId` from `X-Request-Id` request header (sanitized, capped 128
  chars) or a generated UUID; `X-Request-Id` is echoed on every response. `db` from the
  route's `{database}` path param (`none` for non-DB routes). `traceId`/`spanId` only
  when tracing active. **Works with tracing disabled** (requestId + db still populate).
- Text-mode tag (when `logIncludeTrace=true` and a trace is active): appends
  ` [traceId=<traceId>]` (traceId only, no spanId).
- Env-var forms follow the standard convention: `ARCADEDB_SERVER_LOGFORMAT`,
  `ARCADEDB_SERVER_LOGINCLUDETRACE`, plus `-Darcadedb.server.logFormat=json` etc.

### Pillar 2 — Distributed tracing (PR 4604)

- New optional Maven module `tracing` (artifact `arcadedb-tracing`), `provided` scope on
  the server, SPI-registered via `META-INF/services/com.arcadedb.server.ServerPlugin`
  → `com.arcadedb.tracing.TracingPlugin`. OTel SDK stays off the core/server classpath.
  Ships in the **`full`** distribution only (builder `SHADED_MODULES`).
- Config keys (GlobalConfiguration, scope SERVER):
  - `arcadedb.serverMetrics.tracing.enabled` — `Boolean`, default `false`. Description:
    *"Enable OpenTelemetry distributed tracing (requires the optional tracing plugin on
    the classpath). Note: query/command spans include the statement text as the
    db.statement span attribute, which may contain sensitive data, so secure the OTLP
    collector endpoint"*.
  - `arcadedb.serverMetrics.tracing.endpoint` — `String`, default `http://localhost:4317`.
    Description: *"OTLP trace export endpoint"*.
  - `arcadedb.serverMetrics.tracing.samplingRate` — `Float`, default `0.0`. Description:
    *"Parent-based trace sampling ratio in [0.0,1.0]"*. `>=1.0` always-on, `<=0.0`
    always-off, else ratio-based.
- Export: **OTLP over gRPC only** (`OtlpGrpcSpanExporter`, port 4317). Bad endpoint
  degrades gracefully (logs SEVERE, disables tracing, does not crash startup).
- Spans: `arcadedb.http.server.requests` (tags `method`, `path`, `db`, `status`) and
  `arcadedb.query` (tags `protocol`, `db`, `language`, `type`; high-cardinality span
  attribute `db.statement` = query/command text). Query spans nest under the HTTP span.
- Context propagation: **inbound HTTP W3C `traceparent` continuation only.**
- **Do NOT document as features** (not shipped): outbound Raft trace propagation,
  `service.name`/`service.instance.id` resource attributes, `OTEL_RESOURCE_ATTRIBUTES`.
  Mention as known limitations / possible follow-ups.

### Retro-compatibility (applies to all pillars)

Everything is **default-off / behavior-preserving**: with no new config, an upgraded
server behaves identically. `/prometheus`, `/api/v1/server`, `/api/v1/ready` shapes are
preserved; new series/endpoints are additive. No new mandatory dependencies (OTel lives
only in the optional `tracing` module). This is the framing for the whole guide.

## Deliverables

### 1. New page — `src/main/asciidoc/how-to/operations/observability.adoc`

Anchor `[[howto-observability]]`. Cohesive 4-pillar guide:

1. **Intro** — the "Observation spine" (instrument once → metric + span), the
   default-off retro-compat promise, and **the animated SVG pipeline diagram** (see §6).
2. **Metrics depth** — RED timers (the two real ones, their tags, `_seconds_*`
   Prometheus names), the 14 `EngineMetricsBinder` gauges (table), optional OTLP export
   with `serverMetrics.otlp.*` keys and a config snippet. Cross-link Prometheus/Grafana.
3. **Distributed tracing** — the optional `arcadedb-tracing` module (full distribution
   only), enable flags, gRPC OTLP endpoint, inbound `traceparent`, span names,
   `db.statement` **security note**, sampling, documented limitations.
4. **Structured logging** — `logFormat=json` → `JsonLogFormatter`, field list, example
   JSON line, `requestId`/`X-Request-Id` correlation (works without tracing),
   `logIncludeTrace` text tag, byte-identical default output.
5. **Health probes** — `/api/v1/health` (liveness, 204) vs `/api/v1/ready` (readiness)
   + `readinessRequiresHA`; canonical raw-Kubernetes `livenessProbe`/`readinessProbe`
   manifest. Cross-link kubernetes.adoc.

Register the page in the relevant nav include (`content.adoc` / how-to chapter include)
next to `monitoring.adoc`.

### 2. `reference/settings.adoc`

Add the **six** GlobalConfiguration keys to the correct tables with exact
descriptions/defaults: `server.readinessRequiresHA`, `server.logFormat`,
`server.logIncludeTrace`, `serverMetrics.tracing.enabled`,
`serverMetrics.tracing.endpoint`, `serverMetrics.tracing.samplingRate`. For the two
plugin-level raw OTLP keys (`serverMetrics.otlp.enabled`, `serverMetrics.otlp.endpoint`)
and `serverMetrics.prometheus.requireAuthentication`, document them where metrics config
is discussed (they are not GlobalConfiguration enums) — either a sub-note in the table
or in the observability page, cross-referenced.

### 3. `reference/http-api/http.adoc`

- New section `[[http-checkhealth]]` "Check server liveness (GET)" for `/api/v1/health`
  (204, unauth, no DB I/O), added to the endpoint summary table.
- Augment `[[http-checkready]]` to note the optional `readinessRequiresHA` HA-aware mode
  and the `503 "Node has not yet joined the Raft group"` response.

### 4. `how-to/operations/monitoring.adoc`

- **Fix `/metrics` → `/prometheus`** (both the prose endpoint and any scrape-config
  `targets`/path). Verify the plugin-activation guidance still matches reality
  (SPI auto-load vs `server.plugins`) while editing.
- Add a "Further Reading" link to the new observability page; optionally fold the
  generic "Available Metrics" list into a pointer to the precise tables on the new page.

### 5. `how-to/operations/kubernetes.adoc`

- Recommend **liveness → `/api/v1/health`**, readiness → `/api/v1/ready`; update the raw
  manifest example accordingly. Keep the Helm-chart value tables faithful to the chart
  (the chart currently polls `/api/v1/ready` for both) but add a note that liveness can
  target `/api/v1/health`.
- Document `readinessRequiresHA` for HA StatefulSets.

### 6. Animated SVG pipeline diagram (house style)

- Prefix `.obs-*` (grep to confirm free before use).
- `viewBox="0 0 1200 <h>"`, `role="img"`, `aria-label="..."`, inline in
  observability.adoc inside `++++` passthrough fences.
- Concept: a single **Observation** on a hot path (HTTP → query → tx) fans out to three
  sinks — a **metric timer** (→ `/prometheus` scrape + OTLP push), a **span** (→ OTel
  Collector via `traceparent`), and a **correlated JSON log line** (sharing
  `traceId`/`requestId`) — all converging on an **OTel Collector**. Reinforces the
  "instrument once, emit metric + span; correlation ID is the spine" narrative.
- SMIL dots-along-paths animation per the house template.
- **CSS mirrored into BOTH** `src/main/asciidoc/docinfo.html` **and**
  `docs/ui/supplemental/css/arcadedb.css` (live-site requirement). Hide under
  `@media (max-width: 700px)`.

## Scope guards (YAGNI)

- Document **only shipped** behavior. Exclude un-shipped spec items: `arcadedb.tx.duration`
  timer, per-database `EngineMetricsBinder` tags, sparse-vector gauges, outbound Raft
  trace propagation, `service.name`/`service.instance.id` resource attributes,
  `OTEL_RESOURCE_ATTRIBUTES` (note these as limitations/follow-ups only).
- Do not rewrite the Helm chart's documented behavior; add the `/api/v1/health`
  recommendation alongside it.
- Do not pin exact dependency version numbers in prose (they drift); say
  "OpenTelemetry-based" / "Micrometer-based".

## Validation

- Naming: new page lowercase-with-hyphens; anchors lowercase-with-hyphens.
- `python docs-validator.py` passes (cross-refs resolve, no orphan page —
  observability.adoc must be referenced from the nav include and from monitoring.adoc).
- `bash scripts/migrate.sh && npm run build`, then inspect `build/site/.../observability.html`
  to confirm the SVG renders and the CSS (from `arcadedb.css`) applied.
- Spot-check the PDF build path is unaffected (page included via the same source tree).
- House style: American English spelling, uppercase SQL keywords in any SQL snippets.
