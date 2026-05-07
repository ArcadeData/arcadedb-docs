# Kubernetes documentation refactor — Helm-first

**Date:** 2026-05-07
**Author:** robfrank (with Claude Code)
**Status:** Approved (pending implementation)
**Affected page:** `src/main/asciidoc/how-to/operations/kubernetes.adoc`

## Goal

Rewrite the Kubernetes how-to page so that the official Helm chart from
[`ArcadeData/arcadedb-helm`](https://github.com/ArcadeData/arcadedb-helm)
(published to `https://helm.arcadedb.com/`) is the single, canonical install
path. Replace the legacy `kubectl apply -f arcadedb-statefulset.yaml` flow
entirely. Add a comprehensive `values.yaml` reference, a kind-based quickstart
that mirrors `ArcadeData/arcadedb-deployments`, and consolidate the
Kubernetes-specific HA content currently in `ha.adoc` into this page.

## Background

`kubernetes.adoc` today (90 lines) leads with raw-manifest installation
(`kubectl apply -f config/arcadedb-statefulset.yaml`) and treats Helm as a
short footnote that points to a local chart path (`./arcadedb`). This is out
of date in three ways:

1. The chart now lives in its own repository (`ArcadeData/arcadedb-helm`) and
   is published to a public Helm repo (`https://helm.arcadedb.com/`); users
   should install via `helm repo add` rather than from a checkout.
2. `ArcadeData/arcadedb-deployments` provides a working, scripted reference
   deployment (kind cluster + values overrides + start/stop/test scripts)
   that readers should be able to discover from the manual.
3. `ha.adoc` already covers `arcadedb.ha.k8s`, `arcadedb.ha.k8sSuffix`,
   auto-join, and the preStop auto-leave hook in a small `===== Kubernetes`
   subsection (lines 341–360). With the page being rewritten, this content
   belongs on the Kubernetes page where readers will look for it; `ha.adoc`
   should cross-reference instead of duplicating.

## Scope

### In scope

- **Full rewrite** of `src/main/asciidoc/how-to/operations/kubernetes.adoc`
- **Edit** to `src/main/asciidoc/how-to/operations/ha.adoc`: replace the
  `===== Kubernetes` subsection (lines ~341–360) with a one-line cross-
  reference pointing to the new Kubernetes page section.
- New sub-anchors on the Kubernetes page so other pages (and ha.adoc) can
  deep-link.

### Out of scope

- Changes to `arcadedb-helm` (the chart itself).
- Changes to `arcadedb-deployments`.
- Other AsciiDoc pages that mention Kubernetes incidentally
  (`concepts/high-availability.adoc:130`, `tutorials/run.adoc`,
  `concepts/databases.adoc`, etc.) — single-line mentions that remain
  accurate; leave alone.
- Modifying `chapter.adoc` — it already includes `kubernetes.adoc`.
- Documentation of the Docker Compose HA scenario in `arcadedb-deployments`
  (covered by the existing Docker page).

## Page outline

The new `kubernetes.adoc` is organized linearly, simple → advanced, so
newcomers can stop after the quickstart and reference readers can jump to
the relevant section. All anchors are lowercase-with-hyphens per
`docs-validator.py`.

```
[[kubernetes]]
==== Kubernetes

  [Intro: 2–3 sentences. Recommends the official Helm chart from
   helm.arcadedb.com. Notes that ArcadeDB on Kubernetes runs as a
   StatefulSet and supports Raft HA when replicaCount > 1.]

[[kubernetes-prerequisites]]
===== Prerequisites
  - Kubernetes 1.19+
  - Helm 3+
  - kubectl configured for the target cluster

[[kubernetes-quickstart]]
===== Quickstart with kind
  Five-minute path mirroring arcadedb-deployments/kubernetes/start.sh:
  1. kind create cluster
  2. kubectl create secret generic arcadedb-credentials
       --from-literal=rootPassword='...'
  3. helm repo add arcadedb https://helm.arcadedb.com/
     helm repo update
  4. helm install my-arcadedb arcadedb/arcadedb
       --set replicaCount=3
       --set service.http.type=ClusterIP
       --wait
     (or with a values.yaml file — show both)
  5. kubectl port-forward svc/my-arcadedb-http 2480:2480
  6. Open http://localhost:2480 (Studio) or curl with root credentials
  Closing line: "see arcadedb-deployments/kubernetes for the scripted
  version with start/stop/test."

[[kubernetes-install]]
===== Installing the chart
  Production-oriented walkthrough (no kind):
  - Add the Helm repo and update
  - Create the rootPassword secret
  - Prepare a values.yaml override file (link forward to the reference)
  - helm install with --values
  - Verify: kubectl get statefulset, get pods, get svc
  - First connection (root + chosen password)

[[kubernetes-values]]
===== Configuration reference
  Brief intro: "These are the values exposed by the official chart. For the
  complete and current list, see the chart's values.yaml. The reference
  below targets chart version v<X.Y> — confirm against your installed
  version with `helm show values arcadedb/arcadedb`."

  Grouped reference (each group: short prose + table key/default/description
  + a small values.yaml snippet showing typical use):

  - Image: registry, repository, tag, pullPolicy, imagePullSecrets,
    nameOverride, fullnameOverride
  - Replicas: replicaCount (with the Raft HA implication, link to
    kubernetes-ha)
  - Credentials: arcadedb.credentials.rootPassword.secret.{name,key}
  - Database: arcadedb.databaseDirectory, defaultDatabases, extraCommands,
    extraEnvironment
  - Plugins: arcadedb.plugins.{gremlin, postgres, mongo, redis, prometheus,
    custom}
  - Service: service.http.{type,port}, service.rpc.port
  - Ingress: enabled, className, annotations, hosts, tls
  - Persistence: enabled, size, accessMode, storageClass + a note about
    PVCs surviving helm uninstall
  - Resources: requests + limits, with the "no CPU limit to avoid GC
    throttling" note from the chart README
  - Probes: liveness, readiness
  - Autoscaling: enabled, minReplicas, maxReplicas,
    targetCPUUtilizationPercentage, with the Raft quorum caveat
    (minReplicas >= floor(maxReplicas/2)+1)
  - Security context: pod-level (runAsNonRoot, fsGroup) and container-level
    (runAsUser, allowPrivilegeEscalation)
  - Service account: create, automount, annotations, name
  - Scheduling: nodeSelector, tolerations, affinity
  - Pod metadata: podAnnotations, podLabels
  - Network policy: networkPolicy.enabled
  - Extras: extraManifests, volumes, volumeMounts, volumeClaimTemplates

[[kubernetes-operate]]
===== Operating the cluster
  - Scaling:
    Recommended (persistent): helm upgrade --set replicaCount=N
    One-off (reverted on next helm upgrade): kubectl scale statefulset
    Note that scaling does not pause workload (existing point in
    today's page — preserve).
  - Upgrading the chart: helm repo update, helm upgrade.
  - Uninstalling: helm uninstall my-arcadedb. Mention that PVCs persist
    by default — show kubectl delete pvc when a clean slate is wanted.

[[kubernetes-ha]]
===== High Availability on Kubernetes
  Content adapted from ha.adoc:341-360:
  - StatefulSet + Headless Service pattern (peer of etcd, CockroachDB,
    Apache Ozone)
  - The chart pre-computes the full serverList from replicaCount and
    injects via env vars — users typically do not configure
    arcadedb.ha.serverList by hand.
  - Minimal effective configuration (the four properties: ha.enabled,
    ha.k8s, ha.k8sSuffix, ha.serverList) — show as the chart-rendered
    result, not as something users edit.
  - Auto-join on scale-up (v26.4.1+).
  - Auto-leave on scale-down (preStop hook → POST /api/v1/cluster/leave).
  - Cross-reference to <<ha,High Availability>> for the rest of Raft
    semantics (quorum, named peers, snapshot threshold, election
    timeouts, etc.).

[[kubernetes-troubleshooting]]
===== Troubleshooting
  - Root password not set / pod CrashLoopBackOff: the most common cause
    (preserved from today's page).
  - kubectl describe pod arcadedb-0 — read events.
  - kubectl logs arcadedb-0 — read server log.
  - Tearing down a stuck cluster: helm uninstall + optional kubectl
    delete pvc -l app.kubernetes.io/name=arcadedb.

[[kubernetes-reference-deployment]]
===== Reference deployment
  Link: ArcadeData/arcadedb-deployments — kubernetes/ directory has a
  scripted kind-based example (start.sh / stop.sh / test.sh, plus a
  values.yaml override) that pairs well with the quickstart above and
  serves as a starting point for your own setup.
```

## Cross-references and external links

### Internal anchors

- `[[kubernetes]]` — preserved (outbound links from `ha.adoc:16`,
  `chapter.adoc:45 include`, etc., are unchanged)
- New: `[[kubernetes-prerequisites]]`, `[[kubernetes-quickstart]]`,
  `[[kubernetes-install]]`, `[[kubernetes-values]]`,
  `[[kubernetes-operate]]`, `[[kubernetes-ha]]`,
  `[[kubernetes-troubleshooting]]`, `[[kubernetes-reference-deployment]]`
- All anchors lowercase-with-hyphens (CLAUDE.md naming convention,
  enforced by `docs-validator.py`).

### Edit to ha.adoc

Replace lines ~341–360 (`===== Kubernetes` ... auto-leave bullet) with:

```asciidoc
===== Kubernetes

For Kubernetes deployments using the official Helm chart, including
auto-join on scale-up and the preStop auto-leave hook, see
<<kubernetes-ha,High Availability on Kubernetes>>.
```

### External links (verified during exploration)

- `https://helm.arcadedb.com/` — Helm repository
- `https://github.com/ArcadeData/arcadedb-helm` — chart source
- `https://github.com/ArcadeData/arcadedb-deployments` — reference
  deployments (kubernetes/ directory)
- `https://github.com/ArcadeData/arcadedb-helm/blob/main/charts/arcadedb/README.md`
  — chart README (linked from the values reference intro)
- `https://github.com/ArcadeData/arcadedb-helm/blob/main/charts/arcadedb/values.yaml`
  — values source-of-truth (linked from the values reference intro)

The legacy link to
`https://github.com/ArcadeData/arcadedb/blob/main/package/src/main/config/arcadedb-statefulset.yaml`
is removed — the raw-manifest path is dropped entirely.

The legacy link to
`https://github.com/ArcadeData/arcadedb/blob/main/k8s/helm/README.md`
is removed — superseded by the chart's own repo README.

## Maintenance plan

A comprehensive inline values reference can drift from the chart. We accept
the trade-off (the user explicitly chose comprehensive over brief), and we
limit drift cost with three measures:

1. **Chart version pin in the page.** The intro to the values reference
   names the chart version it was written against. Readers can resolve any
   discrepancy with `helm show values arcadedb/arcadedb`.
2. **Single source-of-truth pointer.** The same intro links to the chart's
   `values.yaml` so a reader who needs the absolute current state can find
   it in one click.
3. **Sync expectation.** When `arcadedb-helm` cuts a new minor release that
   adds, removes, or renames values, this page should be reviewed. The
   design itself documents this expectation; we are not adding tooling for
   it now.

## Validation

Before merging:

1. `python docs-validator.py` — naming + cross-ref validation passes (no
   broken `<<...>>` references; all new anchors and files follow
   lowercase-with-hyphens convention).
2. `mvn generate-resources` — single-page HTML build succeeds without
   Asciidoctor errors.
3. `bash scripts/migrate.sh && npm run build` — Antora build succeeds and
   the page renders at `build/site/.../kubernetes.html`.
4. Manual read-through of both rendered outputs to confirm formatting,
   table layout, code-block syntax highlighting, and that all
   cross-references resolve.
5. Confirm anchor uniqueness — no collision with anchors elsewhere in the
   manual (grep for each new anchor name).
6. `mvn -Pgenerate-pdf generate-resources` — PDF builds without errors and
   the new page reads cleanly in PDF.

## Risks and mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Values reference drifts from chart | Medium | Chart version pin + source-of-truth link in the page |
| Existing `<<kubernetes,...>>` links break | Low | Top-level `[[kubernetes]]` anchor preserved |
| ha.adoc edit breaks an inbound link | Low | grep for `kubernetes-ha` (does not exist today) and `<<kubernetes,` (existing — preserved); the only content moved is the body of `===== Kubernetes`, no anchor was attached to it |
| Inline kind quickstart drifts from arcadedb-deployments scripts | Low | Quickstart is intentionally minimal; the deployments link is the canonical scripted version |
| Reader confusion about kubectl scale vs helm upgrade | Medium | Operate section calls out the difference explicitly |

## Open questions

None — all decisions resolved during brainstorming:

- Raw-manifest path: drop entirely
- Values reference depth: comprehensive inline
- arcadedb-deployments treatment: inline kind quickstart + see-also link
- ha.adoc overlap: consolidate K8s/HA content into kubernetes.adoc
- Page structure: linear tutorial-first (Approach A)
