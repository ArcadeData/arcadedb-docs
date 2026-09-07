# Issue #445 — Document `arcadedb.ha.tls.*` (mTLS on the Raft gRPC transport)

Issue: https://github.com/ArcadeData/arcadedb-docs/issues/445
Engine PR: https://github.com/ArcadeData/arcadedb/pull/6918 (issue ArcadeData/arcadedb#3890)
Branch: `feat/445-ha-tls-mtls-raft-grpc`

## Goal

Document the five server-scoped `arcadedb.ha.tls.*` settings that add optional mTLS to the Raft
gRPC transport, plus the deployment story around them, and correct one paragraph in
`ha.adoc` that is now out of date.

## Verification against the engine (not the issue text)

Per house rule, every default and behavioral claim was read out of the engine source, not the
issue body.

`engine/src/main/java/com/arcadedb/GlobalConfiguration.java:2118-2168` — all five settings confirmed:

| Setting | Type | Default |
|---|---|---|
| `arcadedb.ha.tls.enabled` | Boolean | `false` |
| `arcadedb.ha.tls.certChainFile` | String | `""` |
| `arcadedb.ha.tls.privateKeyFile` | String | `""` |
| `arcadedb.ha.tls.trustCertCollectionFile` | String | `""` |
| `arcadedb.ha.tls.mutualAuth` | Boolean | `true` |

`ha-raft/src/main/java/com/arcadedb/server/ha/raft/RaftPropertiesBuilder.java` — behavior confirmed:

- `buildTlsConfig` returns `null` (plaintext) when `enabled=false`; otherwise `requireReadableFile`
  validates all three paths.
- Startup failure messages: `"<key> must be set when arcadedb.ha.tls.enabled is true"` and
  `"<key> (<path>) is not a readable file: Raft gRPC TLS cannot be initialized"`, thrown as
  `ConfigurationException`.
- `warnIfPrivateKeyIsReadableByOthers` logs a `WARNING` when the key has `GROUP_READ` or
  `OTHERS_READ`; it is a warning, never a refusal, and a no-op on non-POSIX filesystems.
- `mutualAuth=false` also logs a `WARNING` at startup.
- `applyTls` sets a single `GrpcConfigKeys.TLS` entry, which Ratis 3.3.0 uses as the default for
  the admin, client and server-to-server endpoints — so one setting covers AppendEntries,
  RequestVote and InstallSnapshot.

`ha-raft/src/main/java/com/arcadedb/server/ha/raft/KubernetesAutoJoin.java:58,126` — the auto-join
probe client is handed the same Ratis `Parameters` as the local server, so it speaks TLS exactly
when the cluster does. No extra configuration for auto-join on Kubernetes.

Release: `git tag --contains 0fa1cc08f3` → **26.9.1**. The issue's "from v26.9.1" is correct.

## Changes

1. `src/main/asciidoc/how-to/operations/ha.adoc`
   - New `[[ha-grpc-mtls]] mTLS for the Raft gRPC transport (from v26.9.1)` section.
   - Corrected the *Peer allowlist* bullet, which claimed mTLS was not available.
   - Cross-reference from the `[[ha-ssl]]` (HTTP side channels) section.
   - Five new rows in the *HA Settings* table.
2. `src/main/asciidoc/reference/settings.adoc` — five new rows, alphabetically placed.
3. `src/main/asciidoc/how-to/operations/kubernetes.adoc` — cert-manager issuance and Secret mount
   recipe in the `[[kubernetes-ha]]` section.

## Verification plan

This is a documentation repository: the executable checks are `docs-validator.py` (naming
conventions, cross-reference resolution, orphan pages) and the two build pipelines
(`scripts/migrate.sh` + `npm run build` for Antora, `mvn generate-resources` for the single-page
HTML). Results recorded below.

## Verification results

| Check | Baseline (before) | After |
|---|---|---|
| `docs-validator.py` — filenames | ✅ pass | ✅ pass |
| `docs-validator.py` — anchor naming | ✅ pass | ✅ pass |
| `docs-validator.py` — broken cross-references | 1 (`postgres.adoc:121`, pre-existing, unrelated) | 1 (same one) |
| `docs-validator.py` — orphaned pages | 41 | 41 |
| Anchors / references counted | 1179 / 707 | 1186 / 709 |
| `mvn generate-resources` (single-page HTML) | clean | clean, no new warnings |
| `scripts/migrate.sh` + `npm run build` (Antora) | clean | clean, no new warnings |

All seven new anchors resolve in both pipelines, and cross-page links render correctly in the
Antora output (`kubernetes.html` → `ha.html#ha-grpc-mtls`,
`reference/settings.html` → `../how-to/operations/ha.html#ha-grpc-mtls`).

### Markup bug caught by inspecting the rendered output

The first draft wrote the wildcards as `` `arcadedb.ha.tls.*` `` and `` `arcadedb.ssl.*` ``. Two of
those on the same line pair their asterisks into AsciiDoc bold, and the rendered HTML silently
dropped the `*` from both. Fixed by wrapping them in a passthrough: `` `+arcadedb.ha.tls.*+` ``.
Worth remembering for any future prose that names a setting family.

## Not verified

The openssl recipe in `[[ha-grpc-mtls-openssl]]` could not be executed in this session: the
sandbox blocks writing files matching a private-key filename pattern. The commands are standard
openssl usage and the certificate profile they produce (`extendedKeyUsage = serverAuth,clientAuth`
plus a SAN, PKCS#8 key) matches what the engine's own test PKI generates with `keytool`
(`ha-raft/src/test/java/com/arcadedb/server/ha/raft/RaftTestPki.java`: `-ext eku=serverAuth,clientAuth`,
and `writePrivateKeyPem` emitting PKCS#8), but the exact command lines were not run end to end.

## Style notes

- American English per house style: `dialing`, `armor`. The one `dialling` left in `ha.adoc` is
  inside a verbatim quote of the engine's own `WARNING` log line and must stay as the engine
  prints it.
- The `detect-private-key` pre-commit hook matches the literal PEM header strings anywhere in a
  staged file, delimiters or not. The first commit attempt was rejected because the prose quoted
  those headers verbatim to explain the PKCS#8 requirement. The docs now describe the armor by
  its label (`PRIVATE KEY` vs `RSA PRIVATE KEY`) instead, which reads the same and does not trip
  the hook.

## Pull request

https://github.com/ArcadeData/arcadedb-docs/pull/451 — branch `feat/445-ha-tls-mtls-raft-grpc`,
commit `b753a2ce`.

### Review cycles

None. This repository has no automated PR reviewer: `.github/workflows/` contains only
`antora-preview.yml`, `cloudflare-deploy.yml`, `docs-validation.yml` and `pdf.yml`, and recent PRs
(#440, #447, #449) drew comments from `mergify` and the maintainer only. The review-poll loop was
stopped rather than left to time out against a bot that does not exist.

Final state: **no reviewer configured** — the PR is ready for human review.

### CI

| Check | Result |
|---|---|
| `generate` (Generate Site) | ✅ pass |
| `Validate Documentation` | ❌ fail — **pre-existing, not caused by this PR** |
| Mergify Summary | ✅ pass |

`Validate Documentation` fails on the `Run documentation validator` step with the single broken
cross-reference `'Column type mapping' in how-to/connectivity/postgres.adoc:121`. The same check
has failed on the last five runs of `main` for the same reason. The source there writes
`<<Column type mapping,Column type mapping>>`, a reference to a section title rather than to a
lowercase-hyphen anchor; Asciidoctor resolves it (both builds are clean) but `docs-validator.py`
does not. Fixing it is a one-line change unrelated to #445, so it was deliberately left out of this
PR rather than mixed in — worth its own issue.

### Follow-up

`project_422_ha_channel_self_healing_docs` tracked "17 undocumented `ha.*` keys" for a later sweep.
Five of those (`ha.tls.*`) are now documented; the remainder still are.
