# Native Drivers Documentation — Design

Date: 2026-09-07
Status: approved (design); implementation plan not yet written
Scope: `arcadedb-docs` — document the four native clients published from
`ArcadeData/arcadedb-drivers` under Languages & Drivers.

## Background

`arcadedb-drivers` publishes four packages, generated from ArcadeDB's OpenAPI and
Protobuf contracts and kept in sync with them by a CI drift gate. All four are live
at version `0.1.0`, verified against the registries on 2026-09-07:

| Package | Registry | API | Notes |
| --- | --- | --- | --- |
| `arcadedb-driver` | PyPI | HTTP | sync + async facade, Python >= 3.10 |
| `arcadedb-driver-grpc` | PyPI | gRPC | sync + async facade, Python >= 3.10 |
| `@arcadedb/driver` | npm | HTTP | ESM only, Node >= 20 |
| `@arcadedb/driver-grpc` | npm | gRPC | Node/Bun/Deno, no browser build |

Both packages in each language were generated against contract `26.9.1`.

`docs.arcadedb.com/arcadedb/languages-drivers` currently routes Python and
JavaScript/TypeScript readers straight to `tutorials/python-quickstart.adoc` and
`tutorials/javascript-quickstart.adoc`, both of which teach the PostgreSQL wire
protocol (`psycopg` / `pg`) with a short HTTP section. Neither mentions a native
driver. Both carry a "per-protocol examples coming soon" TIP.

### Known-stale upstream statement

`typescript/packages/driver-grpc/README.md` in `arcadedb-drivers` still states the
package "is not yet published to npm". The npm registry contradicts this:
`@arcadedb/driver-grpc@0.1.0` is live. These docs will describe the package as
published. Fixing that README is a separate PR against a separate repository and is
not part of this work.

## Decisions

Six decisions were settled during brainstorming. Each is recorded with the reasoning
so a later reader can tell an intentional choice from an accident.

1. **Routing model: a chooser, not a demotion.** The docs do not declare the native
   driver the one true path and demote the wire protocols. A reader building a new
   application wants the native driver; a reader who already runs a PostgreSQL or
   Neo4j stack wants the wire protocol. Both are first-class; the docs route between
   them rather than ranking them.

2. **Granularity: four driver pages plus one shared overview.** One page per
   published package, so each maps 1:1 to a registry entry and a README. The material
   that is cross-cutting and near-verbatim identical across all four READMEs — the
   `truncated` envelope trap, the contract-generation explanation, the HTTP-vs-gRPC
   choice, the compatibility table — lives once on the overview page instead of four
   times.

3. **Depth: docs cover the path, README covers the API.** The docs carry the full
   narrative needed to build something: install, connect, query, transactions, error
   handling, the failure modes that bite. They defer to each package's README for the
   exhaustive API surface and for deep internals (the four-async-interceptors
   explanation in the Python gRPC driver; the exact enumerated limitations of the
   insecure-channel guard).

4. **Versions: one table, no pins in prose.** Install snippets are unpinned
   (`pip install arcadedb-driver`, not `==0.1.0`). Exactly one compatibility table
   exists, on the overview page. No shields.io badges: the PDF build renders a badge
   as a static image, which is worse than a table cell. The failure mode of stating
   nothing — a reader on ArcadeDB 25.x cannot tell whether the driver works for them —
   is worse than the failure mode of one stale row.

5. **Routing happens in the card grid.** `languages-drivers.adoc` is already a pure
   routing page; making its Python and JS/TS cards route to four destinations per
   language rather than one is what that page is for. This costs no URL moves, no
   `url-migration-map.tsv` entries, and no rewrite of two working tutorials. The
   quickstarts' misleading nav labels are fixed in place instead (see below).

6. **All code samples are executed before they ship.** Every snippet on all five
   pages is run against a real ArcadeDB server — HTTP on 2480 and gRPC with the plugin
   enabled — before the page is committed. These are the flagship examples for four
   brand-new packages; a broken quick start on day one is expensive, and porting
   unexecuted recipes is a mistake this repository has made before.

## Information architecture

One new directory, `src/main/asciidoc/how-to/connectivity/drivers/`, holding five
pages:

| File | Anchor | Purpose |
| --- | --- | --- |
| `native-drivers.adoc` | `native-drivers` | Overview: HTTP vs gRPC, contract generation, the `truncated` trap, compatibility table |
| `python-http.adoc` | `driver-python-http` | `arcadedb-driver` |
| `python-grpc.adoc` | `driver-python-grpc` | `arcadedb-driver-grpc` |
| `js-http.adoc` | `driver-js-http` | `@arcadedb/driver` |
| `js-grpc.adoc` | `driver-js-grpc` | `@arcadedb/driver-grpc` |

**Why `how-to/connectivity/` rather than `tutorials/` or `reference/`.** These pages
belong to the existing "how do I connect from X" family that already holds
`postgres.adoc`, `bolt.adoc`, `jdbc.adoc`, `rust.adoc`. `reference/` in this
repository is contract-shaped material (HTTP endpoint tables, the Java API); driver
pages are task-shaped. The `drivers/` subdirectory keeps five new files from swamping
a directory that already holds twelve.

**Heading levels.** Pages are authored at `====` to match their siblings;
`scripts/promote-headings.py` shifts each page so it starts at level 1 in Antora.

### Build and publication path

`scripts/migrate.sh` copies `how-to/` with `cp -R`, so the new subdirectory is picked
up with no script change. The PDF is **not** built from `content.adoc`'s include tree:
`scripts/generate-pdf-manual.py` generates `docs/pdf/manual.adoc` from the nav files.
`how-to/connectivity/` has no `chapter.adoc` and is not included in the legacy
single-page build at all, so these pages follow that same pattern.

Consequence: **adding the pages to `scripts/generate-nav.py` is what puts them in both
the sidebar and the PDF.** No `chapter.adoc` edits are needed anywhere.

### Navigation

In `scripts/generate-nav.py`, under the existing `Languages & Drivers` group:

- The native-drivers overview becomes a parent entry with the four driver pages
  nested beneath it, placed above the per-language wire-protocol entries.
- Two existing entries are retitled so the nav stops promising more than the page
  delivers:
  - `tutorials/python-quickstart.adoc`: `Python` -> `Python — PostgreSQL Protocol`
  - `tutorials/javascript-quickstart.adoc`: `JavaScript / TypeScript` ->
    `JavaScript — PostgreSQL Protocol`

## Page contents

### `native-drivers.adoc` (overview)

- **What these are.** Four packages generated from ArcadeDB's OpenAPI and Protobuf
  contracts, with a CI drift gate. Stated in terms of what it buys the reader: the
  client cannot silently disagree with the server about the wire format.
- **HTTP or gRPC?** A decision table. HTTP for general use, browsers, serverless, and
  minimal dependencies; gRPC for throughput-sensitive server-to-server work — large
  result sets, bulk inserts, streaming. Plus the hard constraint: **there is no
  browser gRPC client and cannot be one**, because ArcadeDB's `GrpcServerPlugin` is
  plain grpc-java over HTTP/2 with no gRPC-Web handler and no Connect protocol in
  front of it. This is a server capability question, not a packaging one.
- **The result envelope and `truncated`.** `query` and `command` return the whole
  envelope, not bare rows. `truncated` is true when the server's serializer hit its
  row cap with rows still to write, and a truncated result is indistinguishable by
  shape from a complete one. Check `truncated` before treating `result` as the whole
  answer. Raising `limit` past `arcadedb.server.httpQueryMaxResultRows` is refused
  with 413 rather than returning more rows, so past that ceiling a narrower filter is
  the only fix.
- **Compatibility table.** The single place in these docs where a version number
  appears:

  | Package | Version | ArcadeDB server |
  | --- | --- | --- |
  | `arcadedb-driver`, `arcadedb-driver-grpc` | 0.1.0 | 26.9.1 |
  | `@arcadedb/driver`, `@arcadedb/driver-grpc` | 0.1.0 | 26.9.1 |

- Links to the four driver pages, and back to the wire-protocol pages for readers who
  took the other branch.

### `python-http.adoc` — `arcadedb-driver`

Install (`pip` and `uv`). `ArcadeDBServer` + `basic_auth` quick start; `bearer_auth`
shown as the token variant. The async twin `AsyncArcadeDBServer`, shown once so the
reader sees the facades mirror each other method-for-method. Context managers and why
they matter (each server owns an `httpx` client with its own connection pool that must
be released). The timeout trap: **omitting `timeout` disables timeouts entirely** — it
is not "use httpx's 5-second default", because in httpx an explicit `timeout=None`
means no timeout at all. `transaction()`. The error model. Defers to the README for
the exhaustive method list.

### `python-grpc.adoc` — `arcadedb-driver-grpc`

Install. `create_client("localhost:50051", insecure=True)`, and that the target is
gRPC's native `host:port` form, not a URL — there is no scheme to parse, so TLS is
`credentials=grpc.ssl_channel_credentials()` and plaintext is an explicit
`insecure=True`. `raw` (the generated stub, through which every RPC in the contract is
reachable) versus the three wrappers `create_client` adds: `stream_query`,
`insert_stream`, `transaction`. Authentication attached as a **channel** interceptor
rather than per-call metadata, and why: the wrappers cover only some RPCs, so per-call
auth would leave `raw` calls silently anonymous. The insecure-channel guard, with its
honest limitation — it recognizes only the exact `Interceptor` value `password_auth`
returned, so composing it with another interceptor silently skips the check while the
plaintext password still goes out. The four-async-interceptors internals stay in the
README.

### `js-http.adoc` — `@arcadedb/driver`

Install. **ESM only, Node >= 20, no `require()` entry point** — stated up front,
because it is the first thing that bites. `createClient` with `basicAuth` and
`bearerAuth`. The `QueryEnvelope<T>` interface. `db.transaction()` and its callback
semantics: every call goes through the `tx` handle passed to the callback, not the
outer `db`; it commits when the callback resolves, rolls back and re-throws when it
throws; the caller always sees the callback's own error, with a failed rollback
attached as `err.cause` rather than replacing it. **Two error models**: facade methods
throw `ArcadeDBError` on any non-2xx; `server.raw` (the underlying openapi-fetch
client) does not throw at all — it returns `{ data, error }`.

### `js-grpc.adoc` — `@arcadedb/driver-grpc`

Install. Runtime targets: Node, Bun, and Deno, with Node the only one this
repository's CI exercises — Bun and Deno are described as intended targets that are
likely to work, not as verified. No browser build, with the server-side reason given
once here and once on the overview. `createClient` with `passwordAuth` and
`bearerAuth`, and the same insecure-URL refusal with the same honest limitation as the
Python driver. `streamQuery`, which flattens the server's stream of row batches into
one row at a time and does nothing else. `retrievalMode` as a deliberate caller
choice, with all three modes and their tradeoffs: `CURSOR` (default; bounded memory),
`MATERIALIZE_ALL` (server materializes first, then batches), `PAGED` (re-issues with
`LIMIT`/`SKIP` per batch).

### `languages-drivers.adoc` changes

The Python and JavaScript/TypeScript cards change `href` to
`how-to/connectivity/drivers/native-drivers.html`, and their sub-text names the native
driver first with the wire options after — for example, Python's becomes
"`arcadedb-driver` (HTTP & gRPC), psycopg, neo4j, httpx." The Node.js, Java, and all
other cards are untouched.

## Voice

These pages are ported from READMEs written in a strong, specific voice that names
what will bite the reader. That voice is preserved rather than flattened into feature
listing. House style still applies: American spelling, uppercase SQL keywords, sparing
em-dashes.

## Verification

1. `python docs-validator.py` — filename and anchor conventions, cross-reference
   validity, orphan detection. Every new page must be reachable: the four driver pages
   from the overview, the overview from `languages-drivers.adoc` and the nav.
2. `bash scripts/migrate.sh && npm run build` — confirms the pages land in
   `build/site/how-to/connectivity/drivers/`, the nav renders the new group, and the
   PDF aggregator picks them up.
3. `mvn -Pgenerate-pdf generate-resources` — confirms the PDF builds and contains the
   new pages with no stray passthrough text.
4. Every code sample executed against a running ArcadeDB server (decision 6), with the
   gRPC plugin enabled for the two gRPC pages.
5. Before attributing any CI failure to this branch, diff the "Validate Documentation"
   job against `main` — it is chronically red there for unrelated reasons, and the
   failing step moves over time.

## Risks

- **Drift.** Nothing mechanically ties these pages to `arcadedb-drivers`. The
  compatibility table and every code sample will silently rot at the next contract
  bump. Decision 4 minimizes the surface to one table and unpinned install commands,
  but that is mitigation, not a fix. A real fix — a CI check comparing the documented
  version against the registries — is out of scope and worth filing separately.
- **Upstream README staleness.** These docs will contradict
  `typescript/packages/driver-grpc/README.md` until that file is corrected. Flagged,
  not fixed here.

## Out of scope

- Any change to the Java tutorial or the Java API reference pages.
- Any rewrite of the psycopg / `pg` quickstarts beyond their nav labels.
- Native driver pages for languages other than Python and JavaScript/TypeScript;
  `go/` and others do not exist in `arcadedb-drivers` yet.
- CI wiring between `arcadedb-docs` and `arcadedb-drivers`.
- The `arcadedb-drivers` README fix.
