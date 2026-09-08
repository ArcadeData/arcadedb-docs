# Native Drivers Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document ArcadeDB's four native drivers (`arcadedb-driver`, `arcadedb-driver-grpc`, `@arcadedb/driver`, `@arcadedb/driver-grpc`) as five new pages under Languages & Drivers, with every code sample executed against a real server before it ships.

**Architecture:** Five AsciiDoc pages in `src/main/asciidoc/how-to/connectivity/drivers/`. One overview page carries the material common to all four drivers (HTTP vs gRPC, the `truncated` trap, the compatibility table); four per-package pages carry that language's idioms. Routing happens in the `languages-drivers.adoc` card grid — no existing page moves, no URL changes. `scripts/generate-nav.py` is the single wiring point: it feeds both the Antora sidebar and the PDF.

**Tech Stack:** AsciiDoc (Asciidoctor + Antora 3.2), Python 3.10+ (`docs-validator.py`, `scripts/*.py`), Node 20+ (Antora, Pagefind), Docker (`arcadedata/arcadedb:26.9.1`) for sample execution, Maven for the PDF build.

**Spec:** `docs/superpowers/specs/2026-09-07-native-drivers-docs-design.md`

## Global Constraints

- **Branch.** Work on a branch off `main` named `feat/native-drivers-docs`. Do NOT build on
  `feat/445-ha-tls-mtls-raft-grpc`, which is unrelated work that happened to be checked out when
  the spec was committed.
- **Edit only `src/main/asciidoc/`.** `docs/modules/ROOT/` is generated and gitignored;
  `scripts/migrate.sh` wipes and rebuilds it. Never hand-edit a file under `docs/modules/ROOT/`.
- **Filenames and anchors are lowercase-with-hyphens.** Enforced by `docs-validator.py` in CI.
- **Headings start at `====`** on every new page, matching siblings in
  `how-to/connectivity/`. `scripts/promote-headings.py` shifts each page to start at level 1
  during migration.
- **House style:** American English spelling, uppercase SQL keywords, sparing em-dashes. Setting
  wildcards in prose are written `+foo.*+` so Asciidoctor does not eat them.
- **Versions appear in exactly one place:** the compatibility table on `native-drivers.adoc`.
  Install commands are unpinned everywhere (`pip install arcadedb-driver`, never `==0.1.0`). No
  shields.io badges.
- **Every code sample must be executed** against a running ArcadeDB server before the page
  containing it is committed (spec decision 6). A sample that was not run does not ship.
- **Exact versions for the compatibility table:** all four packages are `0.1.0`; all four were
  generated against ArcadeDB server `26.9.1`.
- **Docker image for all sample execution:** `arcadedata/arcadedb:26.9.1`.
- **Root password must be at least 8 characters.** Use `playwithdata` (12). A shorter password
  kills the server at startup with `ServerSecurityException: User password too short (<8
  characters)`, whose only visible symptom is a closed port.
- **Scratch work goes in the scratchpad**, not the repo. This is a documentation repository; no
  sample harness, `package.json`, or virtualenv is ever committed.

---

## File Structure

**Created (all under `src/main/asciidoc/how-to/connectivity/drivers/`):**

| File | Responsibility |
| --- | --- |
| `native-drivers.adoc` | Overview. The only page carrying cross-cutting material: what contract-generated means, HTTP vs gRPC (including why there is no browser gRPC), the result envelope and `truncated`, the compatibility table, links to the four driver pages. |
| `python-http.adoc` | `arcadedb-driver` only. Sync and async facades, context managers, the timeout trap, transactions, the two error models. |
| `python-grpc.adoc` | `arcadedb-driver-grpc` only. `host:port` targets, `raw` vs the three wrappers, channel-level auth, the insecure-channel guard, `stream_query`. |
| `js-http.adoc` | `@arcadedb/driver` only. ESM/Node constraints, `createClient`, `QueryEnvelope`, the transaction callback contract, `ArcadeDBError` vs `raw`. |
| `js-grpc.adoc` | `@arcadedb/driver-grpc` only. Runtime targets, no browser build, `createClient` + `passwordAuth` guard, `streamQuery` and `retrievalMode`. |

**Modified:**

| File | Change |
| --- | --- |
| `src/main/asciidoc/languages-drivers.adoc` | Python and JS/TS cards re-point at the overview page and rename their sub-text. |
| `scripts/generate-nav.py` | Five new nav entries under `Languages & Drivers`; two existing entries retitled. |

**Not modified, and deliberately so:** `content.adoc`, `how-to/chapter.adoc`, and every
`chapter.adoc` under `how-to/`. `how-to/connectivity/` has no chapter aggregator and is absent
from the legacy single-page build; the PDF is generated from the nav files by
`scripts/generate-pdf-manual.py`. Adding entries to `generate-nav.py` is the whole of the wiring.

---

### Task 1: A verified sample-execution environment

No repository files change in this task. Its deliverable is a working environment plus four
smoke-tested package installs, and it gates every page task that follows: no sample may be
written into a page before it has run here.

**Files:**
- Create: `$SCRATCH/drivers-samples/` (scratchpad only, never committed)
- Modify: none
- Test: the smoke scripts in steps 5-8

Throughout this plan, `$SCRATCH` means the session scratchpad directory named in the environment
preamble. Nothing under it is added to git.

**Interfaces:**
- Consumes: nothing.
- Produces: two running containers and their addresses — `$ARCADE_HTTP` (an HTTP base URL such
  as `http://localhost:2480`) and `$ARCADE_GRPC` (a gRPC target such as `localhost:50051`) — plus
  a database named `mydb` holding the `Person` / `Movie` / `Acted` schema, a Python virtualenv
  with both PyPI packages, and a Node project with both npm packages. Tasks 3-6 run their samples
  against exactly this environment.

- [ ] **Step 1: Create the branch**

```bash
git fetch origin
git switch -c feat/native-drivers-docs origin/main
```

- [ ] **Step 2: Start an ArcadeDB container with both HTTP and gRPC**

One container serves both tasks here; the drivers repository uses two only to keep a gRPC plugin
failure from reddening its HTTP test suite, which is not a concern for running documentation
samples by hand.

```bash
docker run -d --name arcadedb-docs-samples \
  -p 2480:2480 -p 50051:50051 \
  -e JAVA_OPTS="-Darcadedb.server.rootPassword=playwithdata -Darcadedb.server.plugins=GRPC:com.arcadedb.server.grpc.GrpcServerPlugin" \
  arcadedata/arcadedb:26.9.1
```

The gRPC plugin is **not** enabled by default; without that
`-Darcadedb.server.plugins=` value nothing listens on 50051 at all.

- [ ] **Step 3: Verify both ports are live**

```bash
curl -s -u root:playwithdata http://localhost:2480/api/v1/ready -o /dev/null -w '%{http_code}\n'
docker logs arcadedb-docs-samples 2>&1 | grep 'gRPC server started on 0.0.0.0:50051'
```

Expected: `204` (or `200`) from the first command, and one matching log line from the second. The
log line — not an open TCP port — is the signal that the plugin finished starting. If it is
absent, check the logs for `ServerSecurityException: User password too short`.

- [ ] **Step 4: Create the sample database and schema**

```bash
curl -s -u root:playwithdata -X POST http://localhost:2480/api/v1/server \
  -H 'Content-Type: application/json' \
  -d '{"command":"create database mydb"}'

curl -s -u root:playwithdata -X POST http://localhost:2480/api/v1/command/mydb \
  -H 'Content-Type: application/json' \
  -d '{"language":"sql","command":"CREATE VERTEX TYPE Person IF NOT EXISTS"}'
curl -s -u root:playwithdata -X POST http://localhost:2480/api/v1/command/mydb \
  -H 'Content-Type: application/json' \
  -d '{"language":"sql","command":"CREATE VERTEX TYPE Movie IF NOT EXISTS"}'
curl -s -u root:playwithdata -X POST http://localhost:2480/api/v1/command/mydb \
  -H 'Content-Type: application/json' \
  -d '{"language":"sql","command":"CREATE EDGE TYPE Acted IF NOT EXISTS"}'
curl -s -u root:playwithdata -X POST http://localhost:2480/api/v1/command/mydb \
  -H 'Content-Type: application/json' \
  -d '{"language":"sql","command":"CREATE VERTEX TYPE Account IF NOT EXISTS"}'

curl -s -u root:playwithdata -X POST http://localhost:2480/api/v1/command/mydb \
  -H 'Content-Type: application/json' \
  -d '{"language":"sql","command":"INSERT INTO Person SET name = '\''Alice'\'', age = 30"}'
curl -s -u root:playwithdata -X POST http://localhost:2480/api/v1/command/mydb \
  -H 'Content-Type: application/json' \
  -d '{"language":"sql","command":"INSERT INTO Person SET name = '\''Bob'\'', age = 25"}'
```

Expected: each returns a JSON body with no `"error"` key.

- [ ] **Step 5: Install the two Python packages**

```bash
mkdir -p "$SCRATCH/drivers-samples/python" && cd "$SCRATCH/drivers-samples/python"
python3 -m venv .venv && . .venv/bin/activate
pip install arcadedb-driver arcadedb-driver-grpc
pip show arcadedb-driver arcadedb-driver-grpc | grep -E '^(Name|Version):'
```

Expected: both report `Version: 0.1.0`. If either reports something else, stop and report it —
the compatibility table in Task 2 states 0.1.0 and must not be written from memory.

- [ ] **Step 6: Smoke-test the Python packages**

```python
# $SCRATCH/drivers-samples/python/smoke.py
from arcadedb_driver import ArcadeDBServer, basic_auth
from arcadedb_driver_grpc import create_client, messages

with ArcadeDBServer(base_url="http://localhost:2480", auth=basic_auth("root", "playwithdata")) as srv:
    print("http:", srv.db("mydb").query(language="sql", command="SELECT FROM Person").result)

with create_client("localhost:50051", insecure=True) as client:
    response = client.raw.ExecuteQuery(
        messages.ExecuteQueryRequest(database="mydb", query="SELECT FROM Person", language="sql")
    )
    print("grpc:", [dict(r.properties) for result in response.results for r in result.records])
```

Run: `python smoke.py`
Expected: both lines print Alice and Bob. A `grpc.RpcError` with `UNAUTHENTICATED` means the
container's gRPC plugin wants credentials — add
`auth=password_auth("root", "playwithdata", "mydb")` alongside `insecure=True` and note that the
driver pages must show the authenticated form.

- [ ] **Step 7: Install the two npm packages**

```bash
mkdir -p "$SCRATCH/drivers-samples/js" && cd "$SCRATCH/drivers-samples/js"
npm init -y
npm pkg set type=module
npm install @arcadedb/driver @arcadedb/driver-grpc
npm ls --depth=0
```

Expected: both resolve at `0.1.0`. `type=module` is required — both packages are ESM only with no
`require()` entry point.

- [ ] **Step 8: Smoke-test the npm packages**

```js
// $SCRATCH/drivers-samples/js/smoke.mjs
import { createClient, basicAuth } from "@arcadedb/driver";
import { createClient as createGrpcClient } from "@arcadedb/driver-grpc";

const server = createClient({
  baseUrl: "http://localhost:2480",
  auth: basicAuth("root", "playwithdata"),
});
const { result } = await server.db("mydb").query({ language: "sql", command: "SELECT FROM Person" });
console.log("http:", result);

const grpc = createGrpcClient({ baseUrl: "http://localhost:50051" });
const response = await grpc.raw.executeQuery({ database: "mydb", query: "SELECT FROM Person", language: "sql" });
console.log("grpc:", response.results.flatMap((r) => r.records.map((rec) => rec.properties)));
```

Run: `node smoke.mjs`
Expected: both lines print Alice and Bob.

- [ ] **Step 9: Record the environment facts**

Write `$SCRATCH/drivers-samples/ENV.md` capturing: the four installed versions as reported by
`pip show` and `npm ls`, whether the gRPC calls needed authentication, and the exact HTTP and gRPC
addresses. Tasks 3-6 read this file rather than re-deriving any of it.

No commit — this task changes no tracked file.

---

### Task 2: The overview page, wired end to end

Delivers `native-drivers.adoc` plus both wiring changes (nav and card grid), so the site builds
with a reachable new page before any driver page exists.

**Files:**
- Create: `src/main/asciidoc/how-to/connectivity/drivers/native-drivers.adoc`
- Modify: `src/main/asciidoc/languages-drivers.adoc` (Python and JavaScript cards)
- Modify: `scripts/generate-nav.py` (the `Languages & Drivers` group)
- Test: `python docs-validator.py`, `bash scripts/migrate.sh && npm run build`

**Interfaces:**
- Consumes: the verified versions from `$SCRATCH/drivers-samples/ENV.md` (Task 1, Step 9).
- Produces: the anchor `native-drivers`, which all four driver pages link back to, and the four
  forward xrefs that keep those pages out of the orphan report. Tasks 3-6 each replace one
  "coming in this release" list item on this page with a live xref.

- [ ] **Step 1: Write the overview page**

Create `src/main/asciidoc/how-to/connectivity/drivers/native-drivers.adoc`:

```asciidoc
[[native-drivers]]
==== Native Drivers

[TIP]
====
*Which page do I want?*

* Building a new application in Python or JavaScript/TypeScript -- start here.
* Already running a PostgreSQL stack -- xref:how-to/connectivity/postgres.adoc[PostgreSQL wire protocol].
* Already running a Neo4j stack -- xref:how-to/connectivity/bolt.adoc[Neo4j BOLT].
* Any other language -- xref:reference/http-api/http.adoc[HTTP/JSON API], no driver required.
====

ArcadeDB publishes four native drivers, two per language, from the
https://github.com/ArcadeData/arcadedb-drivers[arcadedb-drivers] repository. Every one of them is
generated from a shared contract -- an OpenAPI specification for the HTTP drivers, a Protobuf
`.proto` for the gRPC drivers -- and each driver's build regenerates from that contract and fails
if the checked-in code and a fresh regeneration disagree.

That matters to you, not just to the people who build the drivers: a generated client cannot
silently disagree with the server about the wire format. When ArcadeDB adds a field, the driver
gets it from the contract rather than from someone remembering to hand-write it.

===== HTTP or gRPC?

[cols="1,3", options="header"]
|===
| Choose | When

| HTTP
| General application traffic, browsers, serverless functions, and anywhere you want the smallest
dependency footprint. This is the right default.

| gRPC
| Throughput-sensitive server-to-server work: large result sets you want to stream rather than
page, and bulk inserts.
|===

There is no browser gRPC driver, and there cannot be one until the server changes. ArcadeDB's
`GrpcServerPlugin` is plain grpc-java over HTTP/2, with no gRPC-Web handler and no Connect
protocol in front of it. A browser cannot speak raw HTTP/2 gRPC framing at all, so no client
library in any language can reach this server from a browser. Use an HTTP driver there.

===== The result envelope, and why `truncated` matters

The HTTP drivers' `query` and `command` do not return bare rows. They return the whole response
envelope: `result`, `limit`, `returned`, and `truncated`.

`truncated` is true when the server's serializer hit its row cap while the query still had rows
left to write. `result` is then a partial answer, not a short-but-complete one -- and the two are
indistinguishable by shape. A caller that reads `result` and ignores `truncated` will silently
work off half an answer.

Always check `truncated` before treating `result` as the whole result set. When it is true,
re-query with a narrower filter or a higher `limit`. Raising `limit` is not always the fix: a
result whose true size exceeds the server's hard ceiling
(`+arcadedb.server.httpQueryMaxResultRows+`) is refused outright with HTTP 413 rather than
truncated, so past that ceiling a narrower filter is the only way forward.

===== Versions and server compatibility

[cols="2,1,1", options="header"]
|===
| Package | Version | ArcadeDB server

| `arcadedb-driver`, `arcadedb-driver-grpc` (PyPI)
| 0.1.0
| 26.9.1

| `@arcadedb/driver`, `@arcadedb/driver-grpc` (npm)
| 0.1.0
| 26.9.1
|===

Each driver is generated against one server release's contract, shown above. Install commands in
these pages are deliberately unpinned; the registries carry the current version.

===== The four drivers

* Python, HTTP -- `arcadedb-driver` (page coming in this release)
* Python, gRPC -- `arcadedb-driver-grpc` (page coming in this release)
* JavaScript / TypeScript, HTTP -- `@arcadedb/driver` (page coming in this release)
* JavaScript / TypeScript, gRPC -- `@arcadedb/driver-grpc` (page coming in this release)
```

The four "coming in this release" placeholders exist only between tasks; Tasks 3-6 each replace
one with a real xref, and Task 7 verifies none remain.

- [ ] **Step 2: Add the nav entries**

In `scripts/generate-nav.py`, inside the `Languages & Drivers` group, immediately after the Java
sub-tree and before `tutorials/python-quickstart.adoc`, insert:

```python
                (("how-to/connectivity/drivers/native-drivers.adoc", "Native Drivers"), [
                ]),
```

If `generate-nav.py` rejects a group whose children list is empty, make this a plain page
entry for now — `("how-to/connectivity/drivers/native-drivers.adoc", "Native Drivers"),` — and
Task 3 converts it to a parent when it adds the first child.

In the same group, retitle the two existing quickstart entries:

```python
                ("tutorials/python-quickstart.adoc", "Python — PostgreSQL Protocol"),
                ("tutorials/javascript-quickstart.adoc", "JavaScript — PostgreSQL Protocol"),
```

- [ ] **Step 3: Re-point the two cards**

In `src/main/asciidoc/languages-drivers.adoc`, change the Python card's `href` from
`tutorials/python-quickstart.html` to `how-to/connectivity/drivers/native-drivers.html`, and its
`<p>` from `psycopg, neo4j, requests / httpx.` to
`arcadedb-driver (HTTP &amp; gRPC), psycopg, neo4j, httpx.`

Change the JavaScript / TypeScript card's `href` from `tutorials/javascript-quickstart.html` to
`how-to/connectivity/drivers/native-drivers.html`, and its `<p>` from
`pg, neo4j-driver, fetch.` to `@arcadedb/driver (HTTP &amp; gRPC), pg, neo4j-driver, fetch.`

Leave every other card untouched, including Node.js.

- [ ] **Step 4: Run the validator**

Run: `python docs-validator.py`
Expected: no naming violations and no broken cross-references. The new page may appear in the
orphaned-pages WARNING list; that is a warning, not a failure, and Task 7 confirms it clears.

- [ ] **Step 5: Build the site**

Run: `bash scripts/migrate.sh && npm run build`
Expected: the migration prints no `WARN: nav references missing page`, and
`build/site/how-to/connectivity/drivers/native-drivers.html` exists with the compatibility table
rendered as a table (not literal text).

- [ ] **Step 6: Commit**

```bash
git add src/main/asciidoc/how-to/connectivity/drivers/native-drivers.adoc \
        src/main/asciidoc/languages-drivers.adoc scripts/generate-nav.py
git commit -m "docs: add native drivers overview and route the language cards to it"
```

---

### Task 3: `arcadedb-driver` (Python, HTTP)

**Files:**
- Create: `src/main/asciidoc/how-to/connectivity/drivers/python-http.adoc`
- Modify: `src/main/asciidoc/how-to/connectivity/drivers/native-drivers.adoc` (one list item)
- Modify: `scripts/generate-nav.py` (one nav entry)
- Test: the executed sample from Step 1, then `python docs-validator.py`

**Interfaces:**
- Consumes: the environment from Task 1; the `native-drivers` anchor from Task 2.
- Produces: the anchor `driver-python-http`.

- [ ] **Step 1: Write and run the sample script**

Create `$SCRATCH/drivers-samples/python/http_page.py` containing every snippet this page will
carry, in order, as one runnable script:

```python
import httpx
from arcadedb_driver import ArcadeDBError, ArcadeDBServer, basic_auth

with ArcadeDBServer(
    base_url="http://localhost:2480",
    auth=basic_auth("root", "playwithdata"),
    timeout=httpx.Timeout(5.0),
) as srv:
    db = srv.db("mydb")

    envelope = db.query(language="sql", command="SELECT FROM Person WHERE age > ?", params={"1": 21})
    print(envelope.result, envelope.returned, envelope.truncated)

    with db.transaction() as tx:
        tx.command(language="sql", command="INSERT INTO Account SET balance = 100")
        total = tx.query(language="sql", command="SELECT sum(balance) AS total FROM Account").result[0]["total"]
    print("total:", total)

    try:
        db.query(language="sql", command="SELECT FROM NoSuchType")
    except ArcadeDBError as err:
        print(err.status, err.error, err.detail, err.request_id)
```

Run: `python http_page.py`
Expected: the query prints Alice's row with `truncated` false; the transaction prints a numeric
total; the error branch prints a non-2xx status. Adjust the page's prose to whatever actually
happens — if `err.detail` comes back empty, the page must not claim it is populated.

- [ ] **Step 2: Write and run the async variant**

```python
import asyncio
from arcadedb_driver import AsyncArcadeDBServer, basic_auth


async def main() -> None:
    async with AsyncArcadeDBServer(
        base_url="http://localhost:2480", auth=basic_auth("root", "playwithdata")
    ) as srv:
        envelope = await srv.db("mydb").query(language="sql", command="SELECT FROM Person")
        print(envelope.result)


asyncio.run(main())
```

Run: `python http_page_async.py`
Expected: prints both people.

- [ ] **Step 3: Write the page**

Create `src/main/asciidoc/how-to/connectivity/drivers/python-http.adoc` with anchor
`[[driver-python-http]]`, title `Python -- HTTP Driver`, and these sections, using only code that
ran in Steps 1-2:

1. **Install** — `pip install arcadedb-driver`, and the uv form `uv add arcadedb-driver`.
   Requires Python 3.10+.
2. **Connect and query** — the `ArcadeDBServer` / `basic_auth` snippet, plus one sentence that
   `bearer_auth("AU-...")` substitutes directly for a session token from `/api/v1/login`.
3. **Sync and async** — the async snippet, and that `AsyncArcadeDBServer` mirrors the sync facade
   method for method.
4. **Close your client** — both classes are context managers because each owns an `httpx` client
   with its own connection pool that must be released. Use `with` / `async with` where you can;
   call `close()` or `await aclose()` otherwise.
5. **Timeouts are off by default** — a NOTE admonition. Omitting `timeout` does not mean "use
   httpx's five-second default"; it means no timeout at all, because in httpx an explicit
   `timeout=None` means exactly that. Show `timeout=httpx.Timeout(5.0)`.
6. **Transactions** — `with db.transaction() as tx:`. State the contract in three clauses: the
   block exits cleanly and the transaction commits; the block raises and it rolls back with the
   block's own exception propagating (a failed rollback attaches as `__cause__` rather than
   replacing it); the commit itself fails and a best-effort rollback is issued first so the
   server-side session is not left for `+arcadedb.server.httpTxExpireTimeout+` to reap. Add the
   trap: calls made through the outer `db` handle while a transaction is open auto-commit outside
   it.
7. **Two error models** — facade methods raise `ArcadeDBError` with `status`, `error`, `detail`,
   `request_id`; `srv.raw` does not raise at all and hands back a response whose `status_code` and
   `parsed` the caller inspects.
8. **Next steps** — xrefs to `native-drivers` (envelope and `truncated`), `driver-python-grpc`,
   and a link to the package README for the full method list.

- [ ] **Step 4: Wire it up**

Add to `scripts/generate-nav.py`, inside the `Native Drivers` children list added in Task 2:

```python
                    ("how-to/connectivity/drivers/python-http.adoc", "Python — HTTP"),
```

In `native-drivers.adoc`, replace the first list item with:

```asciidoc
* Python, HTTP -- xref:how-to/connectivity/drivers/python-http.adoc[`arcadedb-driver`]
```

- [ ] **Step 5: Validate and build**

Run: `python docs-validator.py && bash scripts/migrate.sh && npm run build`
Expected: no broken xrefs, no `WARN: nav references missing page`, and
`build/site/how-to/connectivity/drivers/python-http.html` exists.

- [ ] **Step 6: Commit**

```bash
git add src/main/asciidoc/how-to/connectivity/drivers/ scripts/generate-nav.py
git commit -m "docs: document arcadedb-driver, the Python HTTP driver"
```

---

### Task 4: `arcadedb-driver-grpc` (Python, gRPC)

**Files:**
- Create: `src/main/asciidoc/how-to/connectivity/drivers/python-grpc.adoc`
- Modify: `src/main/asciidoc/how-to/connectivity/drivers/native-drivers.adoc` (one list item)
- Modify: `scripts/generate-nav.py` (one nav entry)
- Test: the executed sample from Step 1, then `python docs-validator.py`

**Interfaces:**
- Consumes: the environment from Task 1; the `native-drivers` anchor from Task 2.
- Produces: the anchor `driver-python-grpc`.

- [ ] **Step 1: Write and run the sample script**

Create `$SCRATCH/drivers-samples/python/grpc_page.py`:

```python
from arcadedb_driver_grpc import InsecureChannelError, create_client, messages, password_auth

with create_client("localhost:50051", insecure=True) as client:
    response = client.raw.ExecuteQuery(
        messages.ExecuteQueryRequest(database="mydb", query="SELECT FROM Person WHERE age > 21", language="sql")
    )
    for result in response.results:
        for record in result.records:
            print(record.rid, dict(record.properties))

    for record in client.stream_query(
        messages.StreamQueryRequest(
            database="mydb",
            query="SELECT FROM Person",
            language="sql",
            retrieval_mode=messages.StreamQueryRequest.RetrievalMode.CURSOR,
            batch_size=500,
        )
    ):
        print(record.rid, dict(record.properties))

try:
    create_client("localhost:50051", auth=password_auth("root", "playwithdata", "mydb"))
except InsecureChannelError as err:
    print("guard fired:", err)
```

Run: `python grpc_page.py`
Expected: the unary query prints matching rows; `stream_query` prints both people one at a time;
the guard branch prints a refusal. If the server requires authentication, add
`auth=password_auth("root", "playwithdata", "mydb"), insecure=True` to the first `create_client`
and carry that form into the page.

- [ ] **Step 2: Write the page**

Create `src/main/asciidoc/how-to/connectivity/drivers/python-grpc.adoc` with anchor
`[[driver-python-grpc]]`, title `Python -- gRPC Driver`, sections:

1. **Install** — `pip install arcadedb-driver-grpc` / `uv add arcadedb-driver-grpc`, Python 3.10+.
2. **Prerequisite: enable the plugin** — an IMPORTANT admonition. The gRPC server is a plugin that
   is not started by default; register it with
   `-Darcadedb.server.plugins=GRPC:com.arcadedb.server.grpc.GrpcServerPlugin` and it listens on
   50051. Cross-reference xref:reference/grpc-api.adoc[the gRPC API reference] for the full option
   list.
3. **Connect and query** — the `create_client` snippet. State that the target is gRPC's native
   `host:port` form, not a URL: there is no scheme to parse and nothing to default, so TLS is
   `credentials=grpc.ssl_channel_credentials()` and plaintext is an explicit `insecure=True`.
4. **`raw` and the three wrappers** — every RPC in the contract is reachable through
   `client.raw`; `create_client` adds `stream_query`, `insert_stream`, and `transaction` on top
   for the RPCs the generated stub alone handles badly. Everything else is used through `raw`.
5. **Authentication is attached to the channel** — `bearer_auth` and `password_auth` become a
   channel interceptor, not per-call metadata, so `client.raw.ExecuteCommand(...)` carries the
   same headers `client.stream_query(...)` does. Explain why: the facade wraps only some RPCs, so
   per-call auth would leave every unwrapped call silently anonymous.
6. **The insecure-channel guard** — a WARNING admonition. `password_auth` sends the password in
   plaintext metadata, so `create_client` raises `InsecureChannelError` unless you pass
   `insecure=True` or supply channel credentials. State the limit honestly: the check keys on
   whether channel credentials were supplied, and a bearer token never trips it because it is not
   a password.
7. **Streaming queries** — the `stream_query` snippet. It flattens the server's stream of
   `QueryResult` batches into one `GrpcRecord` at a time and does nothing else: it picks no
   default for `retrieval_mode` or `batch_size`. List the three modes — `CURSOR` (proto default;
   runs once and streams as you iterate), `MATERIALIZE_ALL` (server loads the whole result set
   first, then batches it), `PAGED` (re-issues with `LIMIT`/`SKIP` per batch) — and say that
   leaving both unset sends protobuf's zero values, which is protobuf's default rather than a
   choice the wrapper made.
8. **Async** — `arcadedb_driver_grpc.aio.create_client` returns the async client; importing from
   `.aio` is the signal for which one you get.
9. **Next steps** — xrefs to `native-drivers`, `driver-python-http`, and the package README for
   the internals (including why the async facade needs four interceptor objects rather than one).

- [ ] **Step 3: Wire it up**

Nav entry, inside the `Native Drivers` children list:

```python
                    ("how-to/connectivity/drivers/python-grpc.adoc", "Python — gRPC"),
```

In `native-drivers.adoc`, replace the second list item with:

```asciidoc
* Python, gRPC -- xref:how-to/connectivity/drivers/python-grpc.adoc[`arcadedb-driver-grpc`]
```

- [ ] **Step 4: Validate and build**

Run: `python docs-validator.py && bash scripts/migrate.sh && npm run build`
Expected: no broken xrefs, no missing-page warnings,
`build/site/how-to/connectivity/drivers/python-grpc.html` exists.

- [ ] **Step 5: Commit**

```bash
git add src/main/asciidoc/how-to/connectivity/drivers/ scripts/generate-nav.py
git commit -m "docs: document arcadedb-driver-grpc, the Python gRPC driver"
```

---

### Task 5: `@arcadedb/driver` (JavaScript / TypeScript, HTTP)

**Files:**
- Create: `src/main/asciidoc/how-to/connectivity/drivers/js-http.adoc`
- Modify: `src/main/asciidoc/how-to/connectivity/drivers/native-drivers.adoc` (one list item)
- Modify: `scripts/generate-nav.py` (one nav entry)
- Test: the executed sample from Step 1, then `python docs-validator.py`

**Interfaces:**
- Consumes: the environment from Task 1; the `native-drivers` anchor from Task 2.
- Produces: the anchor `driver-js-http`.

- [ ] **Step 1: Write and run the sample script**

Create `$SCRATCH/drivers-samples/js/http_page.mjs`:

```js
import { ArcadeDBError, basicAuth, createClient } from "@arcadedb/driver";

const server = createClient({
  baseUrl: "http://localhost:2480",
  auth: basicAuth("root", "playwithdata"),
});

const db = server.db("mydb");

const envelope = await db.query({
  language: "sql",
  command: "SELECT FROM Person WHERE age > ?",
  params: { 1: 21 },
});
console.log(envelope.result, envelope.returned, envelope.truncated);

const total = await db.transaction(async (tx) => {
  await tx.command({ language: "sql", command: "INSERT INTO Account SET balance = 100" });
  const { result } = await tx.query({ language: "sql", command: "SELECT sum(balance) AS total FROM Account" });
  return result[0].total;
});
console.log("total:", total);

try {
  await db.query({ language: "sql", command: "SELECT FROM NoSuchType" });
} catch (err) {
  if (err instanceof ArcadeDBError) console.error(err.status, err.error, err.detail, err.requestId);
}
```

Run: `node http_page.mjs`
Expected: the query prints Alice's row with `truncated` false, the transaction returns a numeric
total, and the error branch prints a non-2xx status.

- [ ] **Step 2: Write the page**

Create `src/main/asciidoc/how-to/connectivity/drivers/js-http.adoc` with anchor
`[[driver-js-http]]`, title `JavaScript / TypeScript -- HTTP Driver`, sections:

1. **Install** — `npm install @arcadedb/driver`.
2. **Requirements** — a NOTE admonition, stated first because it is the first thing that bites:
   Node.js 20 or later, and the package is **ESM only**. There is no CommonJS build and no
   `require()` entry point; import it with `import`.
3. **Connect and query** — the `createClient` / `basicAuth` snippet, and that `bearerAuth("AU-...")`
   substitutes directly.
4. **The result envelope** — show the `QueryEnvelope<T>` interface (`result`, `limit`, `returned`,
   `truncated`) and link to xref:how-to/connectivity/drivers/native-drivers.adoc#native-drivers[the
   overview] for why `truncated` matters rather than repeating it.
5. **Transactions** — the `db.transaction(async (tx) => ...)` snippet, with the contract: every
   call goes through the `tx` handle, not the outer `db`; it commits when the callback resolves
   and returns that value; it rolls back and re-throws when the callback throws or rejects; the
   caller always sees the callback's own error, with a failed rollback attached as `err.cause`
   rather than replacing it; a failed commit issues a best-effort rollback first to release the
   server-side session.
6. **Two error models** — facade methods throw `ArcadeDBError` (`status`, `error`, `detail`,
   `requestId`) on any non-2xx. `server.raw`, the underlying openapi-fetch client, does **not**
   throw: it returns `{ data, error }` and leaves handling to the caller.
7. **Next steps** — xrefs to `native-drivers` and `driver-js-grpc`, plus the package README.

- [ ] **Step 3: Wire it up**

Nav entry, inside the `Native Drivers` children list:

```python
                    ("how-to/connectivity/drivers/js-http.adoc", "JavaScript / TypeScript — HTTP"),
```

In `native-drivers.adoc`, replace the third list item with:

```asciidoc
* JavaScript / TypeScript, HTTP -- xref:how-to/connectivity/drivers/js-http.adoc[`@arcadedb/driver`]
```

- [ ] **Step 4: Validate and build**

Run: `python docs-validator.py && bash scripts/migrate.sh && npm run build`
Expected: no broken xrefs, no missing-page warnings,
`build/site/how-to/connectivity/drivers/js-http.html` exists.

- [ ] **Step 5: Commit**

```bash
git add src/main/asciidoc/how-to/connectivity/drivers/ scripts/generate-nav.py
git commit -m "docs: document @arcadedb/driver, the JavaScript HTTP driver"
```

---

### Task 6: `@arcadedb/driver-grpc` (JavaScript / TypeScript, gRPC)

**Files:**
- Create: `src/main/asciidoc/how-to/connectivity/drivers/js-grpc.adoc`
- Modify: `src/main/asciidoc/how-to/connectivity/drivers/native-drivers.adoc` (one list item)
- Modify: `scripts/generate-nav.py` (one nav entry)
- Test: the executed sample from Step 1, then `python docs-validator.py`

**Interfaces:**
- Consumes: the environment from Task 1; the `native-drivers` anchor from Task 2.
- Produces: the anchor `driver-js-grpc`.

- [ ] **Step 1: Write and run the sample script**

Create `$SCRATCH/drivers-samples/js/grpc_page.mjs`:

```js
import { createClient, passwordAuth, StreamQueryRequest_RetrievalMode } from "@arcadedb/driver-grpc";

const grpc = createClient({ baseUrl: "http://localhost:50051" });

const response = await grpc.raw.executeQuery({
  database: "mydb",
  query: "SELECT FROM Person WHERE age > 21",
  language: "sql",
});
console.log(response.results.flatMap((r) => r.records.map((rec) => [rec.rid, rec.properties])));

for await (const row of grpc.streamQuery({
  database: "mydb",
  query: "SELECT FROM Person",
  language: "sql",
  retrievalMode: StreamQueryRequest_RetrievalMode.CURSOR,
})) {
  console.log(row.rid, row.properties);
}

try {
  createClient({ baseUrl: "http://localhost:50051", auth: passwordAuth("root", "playwithdata") });
} catch (err) {
  console.log("guard fired:", err.message);
}
```

Run: `node grpc_page.mjs`
Expected: the unary query prints matching rows, `streamQuery` prints both people one at a time,
and the guard branch prints the plaintext-password refusal.

- [ ] **Step 2: Write the page**

Create `src/main/asciidoc/how-to/connectivity/drivers/js-grpc.adoc` with anchor
`[[driver-js-grpc]]`, title `JavaScript / TypeScript -- gRPC Driver`, sections:

1. **Install** — `npm install @arcadedb/driver-grpc`.
2. **Prerequisite: enable the plugin** — the same IMPORTANT admonition as the Python gRPC page:
   the plugin is not started by default; register it with
   `-Darcadedb.server.plugins=GRPC:com.arcadedb.server.grpc.GrpcServerPlugin`; it listens on
   50051. Link xref:reference/grpc-api.adoc[the gRPC API reference].
3. **Runtime targets: Node, Bun, Deno -- not browsers** — Node 20+, Bun, or Deno. Say plainly that
   Node is what the drivers repository's CI exercises; Bun and Deno are intended targets without a
   CI job, so treat them as likely to work rather than verified. ESM only, no `require()`. Then
   the browser paragraph: no browser build, and the reason is the server (plain grpc-java over
   HTTP/2, no gRPC-Web handler), so use xref:how-to/connectivity/drivers/js-http.adoc[the HTTP
   driver] there.
4. **Connect and query** — the `createClient` snippet, and that `raw` is the generated Connect
   client for `ArcadeDbService` through which every contract RPC is callable; `createClient` adds
   `streamQuery`, `insertStream`, and `transaction` on top.
5. **Authentication and the insecure guard** — `bearerAuth` sets `authorization: Bearer <token>`;
   `passwordAuth` sets the `x-arcade-user` / `x-arcade-password` / `x-arcade-database` metadata.
   A WARNING admonition: `createClient` refuses to pair `passwordAuth` with an `http://` base URL
   unless you pass `insecure: true`. State the limit honestly — the check recognizes only the
   exact interceptor value `passwordAuth` returned, so composing it with a logging or retry
   interceptor produces a new value without the marker and the refusal is silently skipped while
   the plaintext password still goes out.
6. **Streaming queries and `retrievalMode`** — the `streamQuery` snippet. It flattens the
   server's row batches into one row at a time and does nothing else; `retrievalMode` is
   deliberately the caller's choice. List `CURSOR` (default; bounded memory), `MATERIALIZE_ALL`
   (server materializes the whole result set, then emits batches), `PAGED` (re-issues with
   `LIMIT`/`SKIP` per batch).
7. **Next steps** — xrefs to `native-drivers` and `driver-js-http`, plus the package README.

- [ ] **Step 3: Wire it up**

Nav entry, inside the `Native Drivers` children list:

```python
                    ("how-to/connectivity/drivers/js-grpc.adoc", "JavaScript / TypeScript — gRPC"),
```

In `native-drivers.adoc`, replace the fourth list item with:

```asciidoc
* JavaScript / TypeScript, gRPC -- xref:how-to/connectivity/drivers/js-grpc.adoc[`@arcadedb/driver-grpc`]
```

- [ ] **Step 4: Validate and build**

Run: `python docs-validator.py && bash scripts/migrate.sh && npm run build`
Expected: no broken xrefs, no missing-page warnings,
`build/site/how-to/connectivity/drivers/js-grpc.html` exists.

- [ ] **Step 5: Commit**

```bash
git add src/main/asciidoc/how-to/connectivity/drivers/ scripts/generate-nav.py
git commit -m "docs: document @arcadedb/driver-grpc, the JavaScript gRPC driver"
```

---

### Task 7: Full-pipeline verification and PDF

The five pages exist and each built individually. This task proves the whole pipeline — site, PDF,
search index, and CI validator — is clean, and that no placeholder survived.

**Files:**
- Modify: only fixes surfaced by the checks below
- Test: every command in this task

**Interfaces:**
- Consumes: all five pages and both wiring changes from Tasks 2-6.
- Produces: a branch ready for a pull request.

- [ ] **Step 1: Confirm no placeholders remain**

```bash
grep -rn "coming in this release\|TBD\|TODO" src/main/asciidoc/how-to/connectivity/drivers/
```

Expected: no output. Any hit means a task left its list item unreplaced.

- [ ] **Step 2: Confirm every version claim**

```bash
grep -rn "0\.1\.0\|26\.9\.1" src/main/asciidoc/how-to/connectivity/drivers/
```

Expected: hits only inside the compatibility table in `native-drivers.adoc` — nowhere else, and
no version in any install command. Cross-check the numbers against
`$SCRATCH/drivers-samples/ENV.md`.

- [ ] **Step 3: Run the validator clean**

Run: `python docs-validator.py`
Expected: no naming violations, no broken cross-references, and none of the five new pages in the
orphaned-pages list.

- [ ] **Step 4: Full migrate and build**

Run: `bash scripts/migrate.sh && npm run build`
Expected: no `WARN: nav references missing page`, and none of the five pages listed under "pages
exist on disk but are not in any nav".

- [ ] **Step 5: Check the rendered nav and search index**

```bash
grep -c "Native Drivers" build/site/how-to/connectivity/drivers/native-drivers.html
ls build/site/pagefind/ >/dev/null && echo "index built"
```

Expected: the sidebar group renders, and the Pagefind index exists so the new pages are
searchable.

- [ ] **Step 6: Build the PDF**

Run: `mvn -Pgenerate-pdf generate-resources`
Expected: the build succeeds and `target/generated-docs/ArcadeDB-Manual.pdf` contains the five new
pages. Confirm the compatibility table rendered as a table and no `++++` passthrough content
leaked in as literal text.

- [ ] **Step 7: Tear down the sample environment**

```bash
docker rm -f arcadedb-docs-samples
```

- [ ] **Step 8: Open the pull request**

```bash
git push -u origin feat/native-drivers-docs
gh pr create --title "docs: document the four native ArcadeDB drivers" --body "..."
```

The body should name the spec, list the five new pages, and state that every code sample was
executed against `arcadedata/arcadedb:26.9.1`. Before attributing any red CI check to this branch,
diff the "Validate Documentation" job against `main` — that job is chronically red there for
unrelated reasons, and the failing step moves over time.

---

## Discovered during planning: an unresolved scope question

Reading the packages' public exports turned up driver surface the spec does not mention. Both HTTP
drivers expose three extra namespaces beyond `query` / `command` / `transaction`:

- Python: `db.ts` (time series), `db.grafana`, `db.promql` — `TimeSeriesNamespace`,
  `GrafanaNamespace`, `PromQLNamespace` in `arcadedb_driver/facade/`.
- TypeScript: the same three, exported as `TimeSeriesQueryOptions`, `GrafanaQueryOptions`,
  `PromQLQueryOptions` and friends from `@arcadedb/driver`.

The spec's page outlines cover none of them, and this plan follows the spec rather than quietly
widening it. Whether to add a section per HTTP page — or leave these to the package READMEs under
spec decision 3, "docs cover the path, README covers the API" — is a decision for the author
before Task 3 begins. Time-series support in particular is a documented ArcadeDB feature with its
own pages, so a native driver that speaks it and docs that never say so is a gap worth weighing.
