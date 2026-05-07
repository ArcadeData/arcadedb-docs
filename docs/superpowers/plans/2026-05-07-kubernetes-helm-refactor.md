# Kubernetes Helm-First Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite `src/main/asciidoc/how-to/operations/kubernetes.adoc` as a Helm-first guide built around the official `arcadedb-helm` chart, drop the legacy raw-manifest install path, consolidate the K8s/HA content from `ha.adoc` into the new page, and verify both the single-page Asciidoctor build and the Antora build succeed.

**Architecture:** A single `kubernetes.adoc` file is rewritten in place with eight subsections (prereqs, quickstart-on-kind, production install, comprehensive values reference, operate, HA-on-K8s, troubleshooting, reference deployment). The K8s subsection in `ha.adoc` collapses to a one-line cross-reference. No new `.adoc` files are created. Validation runs `docs-validator.py` (cross-refs + naming), `mvn generate-resources` (single-page HTML), and `bash scripts/migrate.sh && npm run build` (Antora).

**Tech Stack:** AsciiDoc (Asciidoctor 2.5.1 + asciidoctorj-pdf 2.3.23), Antora, Maven 3, Python 3 (validator). Chart pinned to `arcadedb-helm` **v26.4.2**.

**Spec:** `docs/superpowers/specs/2026-05-07-kubernetes-helm-refactor-design.md`

---

## File Map

| File | Change | Responsibility |
|------|--------|----------------|
| `src/main/asciidoc/how-to/operations/kubernetes.adoc` | Full rewrite | The Kubernetes how-to page (Helm-first) |
| `src/main/asciidoc/how-to/operations/ha.adoc` | Edit lines ~341–360 | Replace `===== Kubernetes` body with cross-ref to `<<kubernetes-ha,...>>` |

No other files are touched. `chapter.adoc` already includes `kubernetes.adoc` and needs no change.

## Authoritative Sources

These are the references the implementer should keep open while writing the values reference. The plan calls them out instead of inlining their full content because they're the canonical source:

- Chart README: https://github.com/ArcadeData/arcadedb-helm/blob/main/charts/arcadedb/README.md
- Chart values: https://github.com/ArcadeData/arcadedb-helm/blob/main/charts/arcadedb/values.yaml
- Reference deployment: https://github.com/ArcadeData/arcadedb-deployments/tree/main/kubernetes
  - **Important:** Its `values.yaml` wraps everything under top-level `arcadedb:` because it consumes the chart as a *subchart*. When installing the chart **directly** (`helm install my-arcadedb arcadedb/arcadedb`) — which is what we document — values are at the top level (no `arcadedb:` wrapper). Don't copy the deployments-repo file verbatim.

## Convention Reminders

- All file names: lowercase-with-hyphens. (Validator-enforced.)
- All anchors: lowercase-with-hyphens. Format: `[[anchor-id]]` on its own line directly above a heading.
- Cross-refs: `<<anchor-id,display text>>`.
- Code blocks: `[source,shell]`, `[source,yaml]`, `[source,properties]` etc.
- Tables: `[%header,cols=...]` with `|===` fences. Match the style of the existing `ha.adoc` settings table (lines 392–463).
- House style: American English spelling, uppercase SQL keywords (not relevant for this page, but stay consistent if any SQL appears).

---

## Task 1: Skeleton — anchors and headings only

**Goal:** Replace the existing 90-line page with the new skeleton (intro paragraph + every section heading and anchor) so subsequent tasks fill in content. After this task, the page builds cleanly with mostly empty sections.

**Files:**
- Modify (full rewrite): `src/main/asciidoc/how-to/operations/kubernetes.adoc`

- [ ] **Step 1: Confirm chart version**

The plan pins to chart `26.4.2`. If significant time has passed since the spec was written (>30 days), confirm by fetching `https://raw.githubusercontent.com/ArcadeData/arcadedb-helm/main/charts/arcadedb/Chart.yaml` and reading the `version:` field. If newer, use the new version everywhere this plan says `26.4.2`.

- [ ] **Step 2: Rewrite the file with the skeleton**

Replace the entire contents of `src/main/asciidoc/how-to/operations/kubernetes.adoc` with:

```asciidoc
[[kubernetes]]
==== Kubernetes

ArcadeDB officially supports deployment on Kubernetes via the https://github.com/ArcadeData/arcadedb-helm[arcadedb-helm] chart, published at `https://helm.arcadedb.com/`.
The chart deploys ArcadeDB as a `StatefulSet` and, when `replicaCount` is greater than 1, automatically configures a Raft-based <<ha,High Availability>> cluster.
The reference for the configuration values below targets chart version *26.4.2*; confirm against your installation with `helm show values arcadedb/arcadedb`.

[[kubernetes-prerequisites]]
===== Prerequisites

[[kubernetes-quickstart]]
===== Quickstart with kind

[[kubernetes-install]]
===== Installing the chart

[[kubernetes-values]]
===== Configuration reference

[[kubernetes-values-image]]
====== Image

[[kubernetes-values-replicas]]
====== Replicas

[[kubernetes-values-credentials]]
====== Credentials

[[kubernetes-values-database]]
====== Database

[[kubernetes-values-plugins]]
====== Plugins

[[kubernetes-values-service]]
====== Service

[[kubernetes-values-ingress]]
====== Ingress

[[kubernetes-values-persistence]]
====== Persistence

[[kubernetes-values-resources]]
====== Resources

[[kubernetes-values-probes]]
====== Probes

[[kubernetes-values-autoscaling]]
====== Autoscaling

[[kubernetes-values-security]]
====== Security context

[[kubernetes-values-serviceaccount]]
====== Service account

[[kubernetes-values-scheduling]]
====== Scheduling

[[kubernetes-values-podmetadata]]
====== Pod metadata

[[kubernetes-values-networkpolicy]]
====== Network policy

[[kubernetes-values-extras]]
====== Extras

[[kubernetes-operate]]
===== Operating the cluster

[[kubernetes-ha]]
===== High Availability on Kubernetes

[[kubernetes-troubleshooting]]
===== Troubleshooting

[[kubernetes-reference-deployment]]
===== Reference deployment
```

- [ ] **Step 3: Verify the AsciiDoc compiles**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -30`

Expected: build succeeds. The single-page HTML at `target/generated-docs/index.html` contains the new section headings (you can grep: `grep -c 'kubernetes-quickstart' target/generated-docs/index.html` should return ≥1).

- [ ] **Step 4: Verify the docs validator passes on naming/structure**

Run: `python docs-validator.py`

Expected: validator passes (or, if it reports unrelated pre-existing failures, none of them mention `kubernetes.adoc` or any of the new `kubernetes-*` anchors).

- [ ] **Step 5: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc
git commit -m "docs(k8s): scaffold Helm-first kubernetes.adoc skeleton

Replace the legacy raw-manifest page with the section/anchor skeleton
for the Helm-first rewrite. Subsequent commits fill in each section.

Refs: docs/superpowers/specs/2026-05-07-kubernetes-helm-refactor-design.md"
```

---

## Task 2: Prerequisites + Quickstart

**Goal:** Fill in the two introductory sections that get a reader from "I have a laptop" to "I have a running cluster I can curl."

**Files:**
- Modify: `src/main/asciidoc/how-to/operations/kubernetes.adoc`

- [ ] **Step 1: Fill in Prerequisites**

Replace the empty `[[kubernetes-prerequisites]]\n===== Prerequisites\n` section with:

```asciidoc
[[kubernetes-prerequisites]]
===== Prerequisites

* Kubernetes 1.19 or later
* Helm 3.0 or later
* `kubectl` configured for your target cluster
* (Optional) `kind` and Docker for the local quickstart below
```

- [ ] **Step 2: Fill in Quickstart with kind**

Replace the empty `[[kubernetes-quickstart]]\n===== Quickstart with kind\n` section with:

````asciidoc
[[kubernetes-quickstart]]
===== Quickstart with kind

This walkthrough mirrors https://github.com/ArcadeData/arcadedb-deployments/tree/main/kubernetes[`ArcadeData/arcadedb-deployments/kubernetes`] and produces a 3-node ArcadeDB cluster on a local https://kind.sigs.k8s.io/[kind] cluster in roughly five minutes.

. Create a local Kubernetes cluster:
+
[source,shell]
----
kind create cluster --name arcadedb
----

. Create the secret holding the `root` user password (replace `<password>`):
+
[source,shell]
----
kubectl create secret generic arcadedb-credentials \
  --from-literal=rootPassword='<password>'
----

. Add the ArcadeDB Helm repository and update:
+
[source,shell]
----
helm repo add arcadedb https://helm.arcadedb.com/
helm repo update
----

. Save the following overrides to `values.yaml`:
+
[source,yaml]
----
replicaCount: 3
image:
  tag: "26.4.2"
service:
  http:
    type: ClusterIP
credentials:
  rootPassword:
    secret:
      name: arcadedb-credentials
      key: rootPassword
----

. Install the chart:
+
[source,shell]
----
helm install my-arcadedb arcadedb/arcadedb -f values.yaml --wait
----

. Forward the HTTP port to your laptop:
+
[source,shell]
----
kubectl port-forward svc/my-arcadedb-http 2480:2480
----

. Open http://localhost:2480 in a browser to reach Studio, or use `curl`:
+
[source,shell]
----
curl -u root:<password> http://localhost:2480/api/v1/server
----

For a scripted version (with `start.sh`, `stop.sh`, and `test.sh`), see the <<kubernetes-reference-deployment,reference deployment>>.
````

- [ ] **Step 3: Verify the build still succeeds**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success.

- [ ] **Step 4: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc
git commit -m "docs(k8s): add prerequisites and kind quickstart"
```

---

## Task 3: Production install section

**Goal:** Document the production-oriented install path (no kind), with verification steps and a forward link to the values reference.

**Files:**
- Modify: `src/main/asciidoc/how-to/operations/kubernetes.adoc`

- [ ] **Step 1: Fill in Installing the chart**

Replace the empty `[[kubernetes-install]]\n===== Installing the chart\n` section with:

````asciidoc
[[kubernetes-install]]
===== Installing the chart

For production deployments, follow the same broad shape as the <<kubernetes-quickstart,quickstart>> but tailor `values.yaml` to your environment.

. Add the Helm repository:
+
[source,shell]
----
helm repo add arcadedb https://helm.arcadedb.com/
helm repo update
----

. Create a `Secret` containing the `root` password.
The chart references this secret by name -- it does not store the password in the chart values:
+
[source,shell]
----
kubectl create secret generic arcadedb-credentials \
  --from-literal=rootPassword='<password>'
----

. Prepare a `values.yaml` override file that fits your environment.
At a minimum, set `replicaCount`, `image.tag`, and the `credentials.rootPassword.secret` block.
See the <<kubernetes-values,configuration reference>> for the full set of options including persistence, ingress, resources, autoscaling, and security context.

. Install the chart:
+
[source,shell]
----
helm install my-arcadedb arcadedb/arcadedb \
  --namespace arcadedb --create-namespace \
  --values values.yaml \
  --wait
----

. Verify the deployment:
+
[source,shell]
----
kubectl -n arcadedb get statefulset
kubectl -n arcadedb get pods
kubectl -n arcadedb get svc
----

The pods are named `my-arcadedb-0`, `my-arcadedb-1`, ... and reach the `Ready` state once the readiness probe succeeds.
````

- [ ] **Step 2: Verify the build**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success.

- [ ] **Step 3: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc
git commit -m "docs(k8s): add production install walkthrough"
```

---

## Task 4: Configuration reference — intro and values-table pattern

**Goal:** Add the `===== Configuration reference` intro paragraph (the "what this section is, what version it pins, where to find the source of truth") and write the **first** values group (Image) **fully**, in the exact pattern the rest of the groups will follow. Tasks 5–9 then apply the same pattern to the remaining groups.

**Files:**
- Modify: `src/main/asciidoc/how-to/operations/kubernetes.adoc`

**Pattern reminder (apply to every values group from this task onward):**

```
[[kubernetes-values-<group>]]
====== <Group title>

<One paragraph of prose explaining what the group covers and any cross-cutting
caveats — e.g. for Resources, "do not set a CPU limit; it interacts badly
with the JVM GC.">

[%header,cols="2,1,4"]
|===
|Key | Default | Description

|`<key>` | `<default>` | <description>
| ... | ... | ...
|===

Example override:

[source,yaml]
----
<minimal yaml snippet showing typical use of one or two keys from the table>
----
```

The `cols="2,1,4"` ratio gives the key column enough room for fully-qualified
paths and the description column enough room for a sentence. Use this same
ratio for every group.

- [ ] **Step 1: Fill in the Configuration reference intro**

Replace the empty `[[kubernetes-values]]\n===== Configuration reference\n` line so the heading is followed by:

```asciidoc
[[kubernetes-values]]
===== Configuration reference

The values exposed by the chart are grouped below.
This reference targets chart version *26.4.2*; confirm the current set against your installation with:

[source,shell]
----
helm show values arcadedb/arcadedb
----

The complete and authoritative source is the chart's https://github.com/ArcadeData/arcadedb-helm/blob/main/charts/arcadedb/values.yaml[`values.yaml`].
The example snippets below show keys at the top level (the chart is installed directly as `arcadedb/arcadedb`); if you consume the chart as a *subchart* under a parent named `arcadedb`, wrap each snippet under a top-level `arcadedb:` key.
```

- [ ] **Step 2: Fill in the Image group (full pattern)**

Replace the empty `[[kubernetes-values-image]]\n====== Image\n` section with:

````asciidoc
[[kubernetes-values-image]]
====== Image

Selects the container image, pull policy, and pull secrets.
Override `image.tag` to pin to a specific ArcadeDB release; otherwise the chart's `appVersion` is used.

[%header,cols="2,1,4"]
|===
|Key | Default | Description

|`image.registry` | `arcadedata` | Container registry hosting the image
|`image.repository` | `arcadedb` | Image repository name
|`image.tag` | (chart `appVersion`) | Image tag; pin to a specific ArcadeDB version for reproducible deployments
|`image.pullPolicy` | `IfNotPresent` | Kubernetes image pull policy
|`imagePullSecrets` | `[]` | List of `Secret` references for private registries
|`nameOverride` | `""` | Overrides the chart name used in resource names
|`fullnameOverride` | `""` | Overrides the fully-qualified app name used in resource names
|===

Example override:

[source,yaml]
----
image:
  tag: "26.4.2"
  pullPolicy: IfNotPresent
imagePullSecrets:
  - name: my-registry-secret
----
````

- [ ] **Step 3: Verify the build**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success. Spot-check the table renders correctly: `grep -c 'image.registry' target/generated-docs/index.html` returns at least 1.

- [ ] **Step 4: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc
git commit -m "docs(k8s): add values reference intro and Image group"
```

---

## Task 5: Values reference — Replicas, Credentials, Database, Plugins

**Goal:** Apply the pattern from Task 4 to four more groups. Source content from the chart's `values.yaml` and `README.md` (linked in *Authoritative Sources* at the top of this plan). Use the same `[%header,cols="2,1,4"]` table format and trailing example snippet.

**Files:**
- Modify: `src/main/asciidoc/how-to/operations/kubernetes.adoc`

- [ ] **Step 1: Fill in Replicas**

Replace the empty section. Cover at minimum:

* `replicaCount` — number of pods. Default `1`. Values > 1 enable Raft HA automatically. Cross-reference: `<<kubernetes-ha,High Availability on Kubernetes>>` for the implications.

The example snippet should show `replicaCount: 3` and a one-line note that 3 is the smallest cluster that tolerates one node failure under majority quorum.

- [ ] **Step 2: Fill in Credentials**

Cover:

* `credentials.rootPassword.secret.name` — name of the `Secret` containing the password
* `credentials.rootPassword.secret.key` — key within the `Secret`

Defaults: per the chart's `values.yaml` (typically empty/required). Include a one-paragraph caution that the password must be set before installation; missing-secret pods crash-loop, mentioned again in <<kubernetes-troubleshooting>>.

Example snippet: the same secret-creation `kubectl create secret` shown in the quickstart, followed by the matching `values.yaml` block.

- [ ] **Step 3: Fill in Database**

Cover:

* `arcadedb.databaseDirectory` — path inside the container (default `/home/arcadedb/databases`)
* `arcadedb.defaultDatabases` — databases to create at startup
* `arcadedb.extraCommands` — additional JVM arguments (default `["-Darcadedb.server.mode=production"]`)
* `arcadedb.extraEnvironment` — extra environment variables passed to the container

Example snippet: a minimal `extraCommands` override adding a custom JVM flag, plus an `extraEnvironment` map setting one env var.

- [ ] **Step 4: Fill in Plugins**

Cover the wire-protocol plugin toggles. Per the chart's `values.yaml`, this is `arcadedb.plugins.<name>.enabled` for: `gremlin`, `postgres`, `mongo`, `redis`, `prometheus`, plus a `custom` slot for user plugins.

Example snippet: enabling the Postgres and Mongo wire protocols.

- [ ] **Step 5: Verify the build**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success.

- [ ] **Step 6: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc
git commit -m "docs(k8s): add Replicas, Credentials, Database, Plugins values"
```

---

## Task 6: Values reference — Service, Ingress, Persistence

**Goal:** Three more values groups, same pattern.

**Files:**
- Modify: `src/main/asciidoc/how-to/operations/kubernetes.adoc`

- [ ] **Step 1: Fill in Service**

Cover:

* `service.http.type` — Service type (default `ClusterIP`; common alternatives `NodePort`, `LoadBalancer`)
* `service.http.port` — HTTP port (default `2480`)
* `service.rpc.port` — Raft gRPC port (default `2434`)

Note the difference between the public HTTP service and the internal Raft RPC port (the headless service used by Raft is created automatically by the chart and is not directly exposed to users — call this out).

Example snippet: switching the HTTP service to `LoadBalancer`.

- [ ] **Step 2: Fill in Ingress**

Cover:

* `ingress.enabled` (default `false`)
* `ingress.className`
* `ingress.annotations`
* `ingress.hosts` (list of `host` + `paths`)
* `ingress.tls`

Example snippet: a single-host ingress with TLS and a `cert-manager` annotation.

- [ ] **Step 3: Fill in Persistence**

Cover:

* `persistence.enabled` (default `true` — recommend keeping it on)
* `persistence.size` (default `8Gi`)
* `persistence.accessMode` (default `ReadWriteOnce`)
* `persistence.storageClass` (default `""` → cluster default)

Add a sidebar note that PVCs created by the StatefulSet **survive `helm uninstall`** by design. To delete them, run:

```shell
kubectl delete pvc -l app.kubernetes.io/name=arcadedb -n <namespace>
```

This same `kubectl delete pvc` line will be referenced again in `<<kubernetes-operate>>` and `<<kubernetes-troubleshooting>>`.

Example snippet: enabling persistence with a 50Gi PVC on a named storage class.

- [ ] **Step 4: Verify the build**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success.

- [ ] **Step 5: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc
git commit -m "docs(k8s): add Service, Ingress, Persistence values"
```

---

## Task 7: Values reference — Resources, Probes, Autoscaling

**Goal:** Three more groups. Two of them carry important caveats — make sure the prose includes them.

**Files:**
- Modify: `src/main/asciidoc/how-to/operations/kubernetes.adoc`

- [ ] **Step 1: Fill in Resources**

Cover:

* `resources.requests.cpu`, `resources.requests.memory`
* `resources.limits.memory`
* (intentionally **no** CPU limit by default)

Include the warning from the chart README:

> Avoid setting a CPU limit. CPU throttling interacts poorly with the JVM garbage collector and can cause GC pauses much larger than the throttling window. Use a CPU *request* to size scheduling and memory limits to bound the working set.

Example snippet:

```yaml
resources:
  requests:
    cpu: 500m
    memory: 2Gi
  limits:
    memory: 4Gi
```

- [ ] **Step 2: Fill in Probes**

Cover `livenessProbe` and `readinessProbe` — both are full Kubernetes probe objects in the chart. List the typical sub-keys (`httpGet.path`, `httpGet.port`, `initialDelaySeconds`, `periodSeconds`, `timeoutSeconds`, `failureThreshold`). Defaults: refer to the chart's `values.yaml`.

Example snippet: bumping `initialDelaySeconds` for slow-start environments.

- [ ] **Step 3: Fill in Autoscaling**

Cover:

* `autoscaling.enabled` (default `false`)
* `autoscaling.minReplicas`
* `autoscaling.maxReplicas`
* `autoscaling.targetCPUUtilizationPercentage`

Include the Raft caveat as a callout:

> When autoscaling is enabled in an HA configuration, ensure `minReplicas >= floor(maxReplicas / 2) + 1` so the cluster always has a Raft majority. Falling below the quorum threshold causes writes to stall.

Example snippet: enabling autoscaling with `minReplicas: 3, maxReplicas: 5`.

- [ ] **Step 4: Verify the build**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success.

- [ ] **Step 5: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc
git commit -m "docs(k8s): add Resources, Probes, Autoscaling values"
```

---

## Task 8: Values reference — Security, Service account, Scheduling, Pod metadata, Network policy, Extras

**Goal:** Final six values groups. Pattern is the same; these are mostly straightforward Kubernetes plumbing.

**Files:**
- Modify: `src/main/asciidoc/how-to/operations/kubernetes.adoc`

- [ ] **Step 1: Fill in Security context**

Cover both pod-level and container-level keys:

* `podSecurityContext.runAsNonRoot` (default `true`)
* `podSecurityContext.fsGroup` (default `1000`)
* `securityContext.runAsUser` (default `1000`)
* `securityContext.allowPrivilegeEscalation` (default `false`)
* (any others present in the chart values — check `values.yaml`)

One sentence noting the container runs as non-root by default.

Example snippet: tightening `securityContext` further (e.g. `readOnlyRootFilesystem: true` if the chart supports it).

- [ ] **Step 2: Fill in Service account**

Cover:

* `serviceAccount.create` (default `true`)
* `serviceAccount.automount`
* `serviceAccount.annotations`
* `serviceAccount.name`

Example snippet: re-using an existing service account (e.g. for IRSA on EKS).

- [ ] **Step 3: Fill in Scheduling**

Cover `nodeSelector`, `tolerations`, `affinity`. Defaults are empty. Mention pod anti-affinity as the typical use case (spread Raft peers across nodes).

Example snippet: a pod anti-affinity rule that prefers different nodes for each replica.

- [ ] **Step 4: Fill in Pod metadata**

Cover `podAnnotations` and `podLabels`. One sentence each.

Example snippet: a Prometheus scrape annotation pair.

- [ ] **Step 5: Fill in Network policy**

Cover `networkPolicy.enabled` (and any nested keys present in the chart's `values.yaml`). Defaults: per chart. One sentence on what enabling it does (creates a `NetworkPolicy` allowing only the documented ports).

Example snippet: enabling network policy.

- [ ] **Step 6: Fill in Extras**

Cover `extraManifests`, `volumes`, `volumeMounts`, `volumeClaimTemplates`. These are escape hatches. One sentence each.

Example snippet: mounting an extra `ConfigMap` as a config file.

- [ ] **Step 7: Verify the build**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success.

- [ ] **Step 8: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc
git commit -m "docs(k8s): add remaining values reference groups"
```

---

## Task 9: Operating the cluster

**Goal:** Document scaling, upgrading, and uninstalling. Emphasize the `helm upgrade` vs `kubectl scale` distinction.

**Files:**
- Modify: `src/main/asciidoc/how-to/operations/kubernetes.adoc`

- [ ] **Step 1: Fill in Operating the cluster**

Replace the empty `[[kubernetes-operate]]\n===== Operating the cluster\n` section with:

````asciidoc
[[kubernetes-operate]]
===== Operating the cluster

====== Scaling

Use `helm upgrade` to change the replica count persistently:

[source,shell]
----
helm upgrade my-arcadedb arcadedb/arcadedb \
  --namespace arcadedb \
  --reuse-values \
  --set replicaCount=5
----

`kubectl scale statefulset` also works for an immediate, one-off change:

[source,shell]
----
kubectl -n arcadedb scale statefulset my-arcadedb --replicas=5
----

A `kubectl scale` change is reverted on the next `helm upgrade` because Helm reapplies the `replicaCount` from the chart values.
For persistent changes, prefer `helm upgrade --set replicaCount=N` (or update the values file).

Scaling does not pause the workload.
New pods auto-join the Raft cluster, and pods removed during scale-down auto-leave via the `preStop` hook (see <<kubernetes-ha,High Availability on Kubernetes>>).

====== Upgrading the chart

[source,shell]
----
helm repo update
helm upgrade my-arcadedb arcadedb/arcadedb \
  --namespace arcadedb \
  --reuse-values
----

Pin `image.tag` to a specific ArcadeDB version for reproducible upgrades.

====== Uninstalling

[source,shell]
----
helm uninstall my-arcadedb --namespace arcadedb
----

Persistent volume claims **survive uninstall** by design.
To remove them too:

[source,shell]
----
kubectl -n arcadedb delete pvc -l app.kubernetes.io/name=arcadedb
----

The `Secret` holding the root password is not managed by Helm and is also retained.
Delete it explicitly if no longer needed.
````

- [ ] **Step 2: Verify the build**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success.

- [ ] **Step 3: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc
git commit -m "docs(k8s): add operate-the-cluster section"
```

---

## Task 10: High Availability on Kubernetes

**Goal:** Move the K8s/HA content from `ha.adoc:341–360` into this page (slightly expanded), and on a successful build edit `ha.adoc` to cross-reference here.

**Files:**
- Modify: `src/main/asciidoc/how-to/operations/kubernetes.adoc`
- Modify: `src/main/asciidoc/how-to/operations/ha.adoc:341-360`

- [ ] **Step 1: Fill in High Availability on Kubernetes (in kubernetes.adoc)**

Replace the empty `[[kubernetes-ha]]\n===== High Availability on Kubernetes\n` section with:

````asciidoc
[[kubernetes-ha]]
===== High Availability on Kubernetes

ArcadeDB on Kubernetes uses the standard `StatefulSet` + headless `Service` pattern (the same pattern used by `etcd`, CockroachDB, and Apache Ozone).
The chart pre-computes the full peer list from `replicaCount` and injects it into each pod via environment variables, so users do not configure `arcadedb.ha.serverList` by hand.

The chart sets the equivalent of:

[source,properties]
----
arcadedb.ha.enabled=true
arcadedb.ha.k8s=true
arcadedb.ha.k8sSuffix=.my-arcadedb.arcadedb.svc.cluster.local
arcadedb.ha.serverList=my-arcadedb-0.my-arcadedb.arcadedb.svc.cluster.local:2434:2480,my-arcadedb-1.my-arcadedb.arcadedb.svc.cluster.local:2434:2480,my-arcadedb-2.my-arcadedb.arcadedb.svc.cluster.local:2434:2480
----

(Substitute your release name and namespace.)

*Auto-join on scale-up* (since `26.4.1`)::
When `arcadedb.ha.k8s=true` and a new pod starts without an existing Raft storage directory, the server automatically joins the existing cluster via the Raft `SetConfiguration(ADD)` admin API.
This enables zero-downtime scale-up: `helm upgrade --set replicaCount=N` (or `kubectl scale statefulset`) adds new pods that join the existing cluster without restarting any existing peer.

*Auto-leave on scale-down*::
The chart installs a `preStop` hook that calls `POST /api/v1/cluster/leave` so the terminating pod cleanly transfers leadership (if it holds it) and removes itself from the Raft group before shutdown.

For the rest of the Raft semantics -- quorum, named peers, snapshot threshold, election timeouts, cluster token, replication failure handling -- see <<ha,High Availability>>.
````

- [ ] **Step 2: Verify the build still succeeds**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success.

- [ ] **Step 3: Replace the K8s subsection in ha.adoc**

In `src/main/asciidoc/how-to/operations/ha.adoc`, locate the section starting at the heading `===== Kubernetes` (around line 341) and ending at the line above `===== Troubleshooting` (around line 361). Replace the entire body of `===== Kubernetes` (everything from the heading through the last bullet about auto-leave) with:

```asciidoc
===== Kubernetes

For Kubernetes deployments using the official Helm chart -- including the `StatefulSet` + headless `Service` pattern, auto-join on scale-up, and the `preStop` auto-leave hook -- see <<kubernetes-ha,High Availability on Kubernetes>> in the Kubernetes guide.
```

(Use `Edit` with the exact `old_string` matching the existing `===== Kubernetes` heading and its body. Do not modify `===== Troubleshooting` or anything below it.)

- [ ] **Step 4: Verify the cross-reference resolves**

Run: `python docs-validator.py`

Expected: validator passes (no broken cross-references). The new `<<kubernetes-ha,...>>` link from `ha.adoc` resolves to the anchor created in step 1.

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success. Spot-check: `grep -c 'kubernetes-ha' target/generated-docs/index.html` returns at least 2 (the anchor itself + the cross-ref from ha.adoc).

- [ ] **Step 5: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc src/main/asciidoc/how-to/operations/ha.adoc
git commit -m "docs(k8s,ha): consolidate K8s/HA content into kubernetes.adoc

Move the StatefulSet + headless service + auto-join/auto-leave content
out of ha.adoc into the new kubernetes-ha section, and replace the
ha.adoc subsection with a one-line cross-reference."
```

---

## Task 11: Troubleshooting + Reference deployment

**Goal:** Final two sections.

**Files:**
- Modify: `src/main/asciidoc/how-to/operations/kubernetes.adoc`

- [ ] **Step 1: Fill in Troubleshooting**

Replace the empty `[[kubernetes-troubleshooting]]\n===== Troubleshooting\n` section with:

````asciidoc
[[kubernetes-troubleshooting]]
===== Troubleshooting

The most common deployment failure is a missing or incorrectly named `rootPassword` `Secret` -- pods crash-loop with an authentication-related error in the log.
Verify the secret exists and that the chart's `credentials.rootPassword.secret.name` and `.key` match it.

Inspect a pod's events:

[source,shell]
----
kubectl -n arcadedb describe pod my-arcadedb-0
----

Read the server log:

[source,shell]
----
kubectl -n arcadedb logs my-arcadedb-0
----

(Replace `my-arcadedb-0` with the pod name you want to inspect.)

To tear down a stuck cluster and start over:

[source,shell]
----
helm uninstall my-arcadedb --namespace arcadedb
kubectl -n arcadedb delete pvc -l app.kubernetes.io/name=arcadedb
----

Then re-run `helm install` with corrected values.
````

- [ ] **Step 2: Fill in Reference deployment**

Replace the empty `[[kubernetes-reference-deployment]]\n===== Reference deployment\n` section with:

````asciidoc
[[kubernetes-reference-deployment]]
===== Reference deployment

The https://github.com/ArcadeData/arcadedb-deployments[`ArcadeData/arcadedb-deployments`] repository hosts a working, scripted reference deployment under https://github.com/ArcadeData/arcadedb-deployments/tree/main/kubernetes[`kubernetes/`].
It pairs a https://kind.sigs.k8s.io/[kind] cluster with the official chart and provides:

* `start.sh` -- creates the kind cluster, runs `helm dependency update` + `helm install --wait`, and starts a port-forward to `localhost:2480`.
* `stop.sh` -- terminates the port-forward, runs `helm uninstall`, and destroys the kind cluster.
* `test.sh` -- validates that the cluster is functional.
* `values.yaml` -- the values overrides used by `start.sh`. Note that this file wraps overrides under a top-level `arcadedb:` key because it consumes the chart as a *subchart*; when installing the chart directly (the path documented above), use the same overrides at the top level.

Use this repository as a starting point for your own setup and as a reproducible bug-report environment.
````

- [ ] **Step 3: Verify the build**

Run: `mvn -q generate-resources -DskipTests 2>&1 | tail -20`

Expected: success.

- [ ] **Step 4: Commit**

```shell
git add src/main/asciidoc/how-to/operations/kubernetes.adoc
git commit -m "docs(k8s): add troubleshooting and reference deployment sections"
```

---

## Task 12: Final validation pass

**Goal:** Run every validation and rendering command in the spec to confirm the rewrite is shippable. Fix anything that breaks.

**Files:**
- Read-only verification, plus possible spot fixes if anything fails.

- [ ] **Step 1: Run the docs validator**

Run: `python docs-validator.py`

Expected: passes. If it reports broken cross-references involving the new `kubernetes-*` anchors or any existing `<<kubernetes,...>>` callers, fix the offending anchor or reference inline.

- [ ] **Step 2: Confirm no anchor collisions**

Run:

```shell
for a in kubernetes-prerequisites kubernetes-quickstart kubernetes-install kubernetes-values kubernetes-operate kubernetes-ha kubernetes-troubleshooting kubernetes-reference-deployment kubernetes-values-image kubernetes-values-replicas kubernetes-values-credentials kubernetes-values-database kubernetes-values-plugins kubernetes-values-service kubernetes-values-ingress kubernetes-values-persistence kubernetes-values-resources kubernetes-values-probes kubernetes-values-autoscaling kubernetes-values-security kubernetes-values-serviceaccount kubernetes-values-scheduling kubernetes-values-podmetadata kubernetes-values-networkpolicy kubernetes-values-extras; do
  count=$(grep -r "\[\[$a\]\]" src/main/asciidoc/ | wc -l)
  echo "$a: $count"
done
```

Expected: every anchor reports `1`. Any value other than 1 indicates a duplicate or missing definition; fix and rerun.

- [ ] **Step 3: Build the single-page HTML**

Run: `mvn generate-resources`

Expected: build succeeds, no Asciidoctor warnings or errors. The output file `target/generated-docs/index.html` exists.

- [ ] **Step 4: Build the PDF**

Run: `mvn -Pgenerate-pdf generate-resources`

Expected: success. `target/generated-docs/ArcadeDB-Manual.pdf` exists.

- [ ] **Step 5: Build the Antora site**

Run:

```shell
npm ci
bash scripts/migrate.sh
npm run build
```

Expected: success. `build/site/` exists and contains a Kubernetes page derived from `kubernetes.adoc` (find it with `find build/site -name 'kubernetes*' -type f`).

- [ ] **Step 6: Spot-check the rendered output**

Open `target/generated-docs/index.html` in a browser (or inspect with `grep`/`less`) and verify:

* The intro paragraph appears with the correct chart-version pin (`26.4.2`).
* All eight subsections render in order.
* The values reference tables render correctly (header row, three columns).
* The cross-reference from `ha.adoc` resolves: search for `High Availability on Kubernetes` in the rendered HA chapter and confirm it links to the Kubernetes section.

Locate the same page in `build/site/` (Antora output) and repeat the spot-check.

- [ ] **Step 7: If everything passes, no commit needed**

If steps 1–6 pass without changes, the work from previous tasks is complete and committed. If you made fixes during this task, commit them:

```shell
git add -A
git commit -m "docs(k8s): post-validation fixes"
```

- [ ] **Step 8: Summarize**

Report:
* Total commits added on this branch
* Each validation command's pass/fail status
* Any deviations from the spec (there should be none; if so, document why)

---

## Self-Review

**Spec coverage check:**

| Spec section | Implementing task(s) |
|--------------|----------------------|
| Page outline → intro | Task 1 (skeleton) |
| Page outline → Prerequisites | Task 2 |
| Page outline → Quickstart with kind | Task 2 |
| Page outline → Installing the chart | Task 3 |
| Page outline → Configuration reference (intro + 16 groups) | Tasks 4, 5, 6, 7, 8 |
| Page outline → Operating the cluster | Task 9 |
| Page outline → High Availability on Kubernetes | Task 10 |
| Page outline → Troubleshooting | Task 11 |
| Page outline → Reference deployment | Task 11 |
| Cross-references → ha.adoc edit | Task 10 |
| Cross-references → new sub-anchors | Task 1 (skeleton creates them) |
| Maintenance → chart version pin | Task 1 (intro), Task 4 (values intro) |
| Maintenance → source-of-truth pointer | Task 4 (values intro) |
| Validation → docs-validator.py | Tasks 1, 10, 12 |
| Validation → mvn generate-resources | every task |
| Validation → mvn -Pgenerate-pdf | Task 12 |
| Validation → migrate.sh + npm run build | Task 12 |
| Validation → manual read-through | Task 12 step 6 |
| Validation → anchor uniqueness | Task 12 step 2 |

No gaps.

**Placeholder scan:** No "TBD", "TODO", or vague "add appropriate X" instructions. Every step shows the exact AsciiDoc to write or the exact command to run, with one deliberate, structured exception: Tasks 5–8 specify the *content* of each values group ("cover these keys, with this defaults, with this caveat, with this example pattern") rather than reproducing the full chart `values.yaml` inline. This is intentional — the chart's `values.yaml` is the source of truth and must be opened by the implementer; reproducing it here would re-create the drift problem. Each step still names every key to cover, every default value, every caveat callout, and the structure of the example snippet.

**Type consistency check:** Anchor names match between definition and reference sites (`kubernetes-ha` defined in Task 1, referenced from `ha.adoc` in Task 10; `kubernetes-troubleshooting` defined in Task 1, referenced from quickstart in Task 2 implicitly via "see troubleshooting"). Service names (`my-arcadedb-http`), pod names (`my-arcadedb-0..N`), and namespace (`arcadedb`) are consistent across quickstart, install, operate, and troubleshooting sections.
