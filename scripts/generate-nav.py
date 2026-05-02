#!/usr/bin/env python3
"""
Generate docs/modules/ROOT/nav*.adoc from an explicit, user-task-shaped
section structure.

The old generator walked the include tree of src/main/asciidoc/content.adoc,
which produced one giant Documentation sidebar that mixed concepts with Java
code with operations. This generator instead emits three sibling nav files
that show up as tabs in the sidebar:

  nav.adoc        — Documentation        (narrative: get started / build /
                                            model / operate / tools / use-cases /
                                            API & Drivers including Java / HTTP /
                                            gRPC / MCP references)
  nav-query.adoc  — Query Languages      (SQL, Cypher, Gremlin, GraphQL,
                                            MongoDB QL, Redis, graph algorithms,
                                            vector functions)

Each tab has groups (collapsible parent items with no URL) and pages
(leaf items pointing at existing adoc files). Page URLs and anchors
are unchanged — only the sidebar grouping is rearranged.

Idempotent — overwrites the three nav files on every run.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAGES = REPO / "docs" / "modules" / "ROOT" / "pages"
NAV_DIR = REPO / "docs" / "modules" / "ROOT"

HEADING_RE = re.compile(r"^=+\s+(.+?)\s*$")


# Pages explicitly listed in the structure render with their first-heading
# title; pages can also be given an override label via a (path, label) tuple.
NAV_STRUCTURE: list[dict] = [
    {
        "file": "nav.adoc",
        "title": "Documentation",
        "intro": [("index.adoc", "Welcome")],
        "groups": [
            (("get-started.adoc", "Get Started"), [
                "tutorials/what-is-arcadedb.adoc",
                "tutorials/run.adoc",
                ("how-to/operations/docker.adoc", "Quick Start with Docker"),
            ]),
            ("Examples", [
                ("tutorials/vector-search-tutorial.adoc", "Vector Search Tutorial"),
                ("tutorials/time-series-tutorial.adoc", "Time Series Tutorial"),
                "use-cases/recommendation-engine.adoc",
                "use-cases/knowledge-graph.adoc",
                "use-cases/graph-rag.adoc",
                "use-cases/fraud-detection.adoc",
                "use-cases/realtime-analytics.adoc",
                "use-cases/social-network-analytics.adoc",
                "use-cases/supply-chain.adoc",
                ("use-cases/iam.adoc", "Identity & Access Management"),
                "use-cases/customer-360.adoc",
                "use-cases/semantic-search.adoc",
                "use-cases/geospatial-analytics.adoc",
                "use-cases/content-management.adoc",
                "use-cases/network-monitoring.adoc",
                "use-cases/data-lineage.adoc",
            ]),
            (("languages-drivers.adoc", "Languages & Drivers"), [
                (("tutorials/java-tutorial.adoc", "Java"), [
                    ("reference/java-api/java-ref-database.adoc", "Database API"),
                    ("reference/java-api/java-ref-database-async.adoc", "Async Database API"),
                    ("reference/java-api/java-schema.adoc", "Schema API"),
                    ("reference/java-api/java-select-api.adoc", "Native Select API"),
                    ("reference/java-api/java-embeddeddoc.adoc", "Embedded Documents"),
                    ("reference/java-api/java-events.adoc", "Events"),
                    ("reference/java-api/java-batch-importer.adoc", "Graph Batch Importer"),
                    ("reference/java-api/java-vectors.adoc", "Vector Embeddings"),
                    ("reference/java-api/java-api-remote.adoc", "Remote API"),
                    ("reference/java-api/java-api-grpc.adoc", "gRPC API"),
                ]),
                ("tutorials/python-quickstart.adoc", "Python"),
                ("tutorials/javascript-quickstart.adoc", "JavaScript / TypeScript"),
                ("how-to/connectivity/http-nodejs.adoc", "Node.js / JavaScript"),
                ("how-to/connectivity/http-csharp.adoc", "C#"),
                ("how-to/connectivity/c.adoc", "C"),
                ("how-to/connectivity/cpp.adoc", "C++"),
                ("how-to/connectivity/rust.adoc", "Rust"),
                ("how-to/connectivity/ruby.adoc", "Ruby"),
                ("how-to/connectivity/r.adoc", "R"),
                ("how-to/connectivity/http-elixir.adoc", "Elixir"),
            ]),
            (("api-integration.adoc", "API & Integration"), [
                ("reference/http-api/http.adoc", "HTTP API"),
                ("reference/grpc-api.adoc", "gRPC API"),
                ("how-to/connectivity/bolt.adoc", "Neo4j BOLT Protocol"),
                ("how-to/connectivity/postgres.adoc", "PostgreSQL Wire Protocol"),
                ("reference/mcp/mcp.adoc", "MCP Server"),
            ]),
            # Data Modeling reads as a learning path top-to-bottom:
            #   1. The big picture (multi-model)
            #   2. The core model (graph) and the other native models
            #   3. Storage primitives (records / databases)
            #   4. Schema layer (schema / inheritance / indexes / transactions)
            #   5. Value-level vocabulary (data types)
            #   6. Advanced modelling patterns
            #   7. Storage internals for the curious
            ("Data Modeling", [
                # 1. Big picture
                ("concepts/multi-model.adoc", "Multi-Model Architecture"),
                # 2. The seven data models
                ("concepts/graphs.adoc", "Graph Database"),
                ("concepts/timeseries.adoc", "Time Series"),
                ("concepts/vector-search.adoc", "Vector"),
                ("how-to/data-modeling/geospatial.adoc", "Geospatial"),
                ("how-to/data-modeling/full-text-index.adoc", "Full-Text Search"),
                ("concepts/key-value.adoc", "Key/Value"),
                # 3. Storage primitives
                ("concepts/basics.adoc", "Records, Documents, Vertices & Edges"),
                ("concepts/databases.adoc", "Databases"),
                # 4. Schema
                ("concepts/schema.adoc", "Schema"),
                ("concepts/inheritance.adoc", "Inheritance"),
                ("concepts/indexes.adoc", "Indexes"),
                ("concepts/transactions.adoc", "Transactions"),
                # 5. Data types
                ("reference/datatypes.adoc", "Data Types"),
                ("reference/binary-types.adoc", "Binary Types (BLOB)"),
                ("reference/managing-dates.adoc", "Managing Dates"),
                # 6. Advanced patterns (still feature-shaped, useful to most users)
                ("how-to/data-modeling/materialized-views.adoc", "Materialized Views"),
                ("how-to/data-modeling/vector-embeddings.adoc", "Vector Embeddings"),
            ]),
            ("Import & Migration", [
                ("how-to/migration/importer.adoc", "Generic Importer"),
                ("how-to/migration/graph-importer.adoc", "Graph Importer"),
                ("how-to/migration/json-importer.adoc", "JSON Importer"),
                ("how-to/migration/orientdb-importer.adoc", "OrientDB Importer"),
                ("how-to/migration/neo4j-importer.adoc", "Neo4j Importer"),
            ]),
            ("Self-Managed Deployment", [
                ("how-to/operations/binaries.adoc", "Install from Binaries"),
                ("how-to/operations/install-docker.adoc", "Install with Docker"),
                ("how-to/operations/kubernetes.adoc", "Kubernetes"),
                "tutorials/embed-server.adoc",
                ("how-to/operations/server.adoc", "Server Configuration"),
                ("how-to/operations/settings.adoc", "Changing Settings"),
                ("concepts/high-availability.adoc", "High Availability — Concepts"),
                ("how-to/operations/ha.adoc", "High Availability — Setup"),
                ("how-to/operations/backup.adoc", "Backup"),
                ("how-to/operations/auto-backup.adoc", "Automatic Backup"),
                ("how-to/operations/restore.adoc", "Restore"),
                "how-to/operations/monitoring.adoc",
                ("how-to/operations/upgrade.adoc", "Upgrade ArcadeDB"),
            ]),
            ("Security", [
                "how-to/operations/users.adoc",
                "how-to/operations/groups.adoc",
                ("how-to/operations/policy.adoc", "Security Policy"),
                ("how-to/operations/secrets.adoc", "Handling Secrets"),
                ("how-to/operations/gremlin-security.adoc", "Gremlin Security"),
            ]),
            ("Tools", [
                ("tools/studio/main.adoc", "Studio Overview"),
                ("tools/studio/database.adoc", "Studio: Database"),
                ("tools/studio/graph.adoc", "Studio: Graph"),
                ("tools/studio/table.adoc", "Studio: Table"),
                ("tools/studio/json.adoc", "Studio: JSON"),
                ("tools/studio/information.adoc", "Studio: Information"),
                ("tools/studio/server.adoc", "Studio: Server"),
                ("tools/studio/api.adoc", "Studio: API"),
                "tools/console.adoc",
                ("tools/swaggerui.adoc", "Swagger UI"),
                ("tools/tools.adoc", "Other Tools"),
            ]),
            (("how-to/integrations/chapter.adoc", "BI & Analytics"), [
                ("how-to/connectivity/jdbc.adoc", "JDBC Driver"),
                ("how-to/integrations/apache-superset.adoc", "Apache Superset"),
                ("how-to/integrations/grafana.adoc", "Grafana"),
                "how-to/integrations/metabase.adoc",
                ("how-to/integrations/power-bi.adoc", "Power BI"),
                "how-to/integrations/tableau.adoc",
            ]),
            # Advanced — engine internals and tuning that beginners can skip.
            # Pages stay at their original URLs; only the sidebar grouping
            # changes so the learning path stays clean for newcomers.
            ("Advanced", [
                ("how-to/operations/performance-tuning.adoc", "Performance Tuning"),
                ("reference/settings.adoc", "Settings Reference"),
                ("reference/sql-syntax.adoc", "SQL Syntax"),
                ("how-to/data-modeling/graph-olap.adoc", "Graph OLAP Engine"),
                ("reference/storage.adoc", "Storage Internals"),
                ("reference/lsm-tree.adoc", "LSM-Tree Algorithm"),
            ]),
            ("Help", [
                "appendix/community.adoc",
                ("appendix/issues.adoc", "Report an Issue"),
                "reference/requirements.adoc",
            ]),
        ],
    },
    {
        "file": "nav-query.adoc",
        "title": "Query Languages",
        "intro": [],
        "groups": [
            (("reference/sql/sql-introduction.adoc", "SQL"), [
                ("Manipulation", [
                    ("reference/sql/sql-select.adoc", "SELECT"),
                    ("reference/sql/sql-insert.adoc", "INSERT"),
                    ("reference/sql/sql-update.adoc", "UPDATE"),
                    ("reference/sql/sql-delete.adoc", "DELETE"),
                    ("reference/sql/sql-match.adoc", "MATCH"),
                    ("reference/sql/sql-traverse.adoc", "TRAVERSE"),
                    ("reference/sql/sql-move.adoc", "MOVE VERTEX"),
                    ("reference/sql/sql-create-vertex.adoc", "CREATE VERTEX"),
                    ("reference/sql/sql-create-edge.adoc", "CREATE EDGE"),
                ]),
                ("Schema (DDL)", [
                    ("reference/sql/sql-types.adoc", "Types"),
                    ("reference/sql/sql-properties.adoc", "Properties"),
                    ("reference/sql/sql-indexes.adoc", "Indexes"),
                    ("reference/sql/sql-buckets.adoc", "Buckets"),
                    ("reference/sql/sql-triggers-ddl.adoc", "Triggers"),
                    ("reference/sql/sql-materialized-views.adoc", "Materialized Views"),
                ]),
                ("reference/sql/sql-database-admin.adoc", "Database Admin"),
                ("reference/sql/sql-inspection.adoc", "Inspection"),
                ("Query Shaping", [
                    ("reference/sql/sql-projections.adoc", "Projections"),
                    ("reference/sql/sql-pagination.adoc", "Pagination"),
                    ("reference/sql/sql-where.adoc", "Filtering"),
                ]),
                ("Reference", [
                    ("reference/sql/sql-script.adoc", "SQL Script"),
                    ("reference/sql/sql-functions.adoc", "Functions"),
                    ("reference/sql/sql-methods.adoc", "Methods"),
                    ("reference/sql/sql-triggers.adoc", "Triggers (concept)"),
                    ("reference/sql/sql-custom-functions.adoc", "Custom Functions"),
                    ("reference/sql/sql-select-execution.adoc", "SELECT Execution Model"),
                ]),
            ]),
            ("Cypher (openCypher)", [
                ("reference/cypher/cypher-introduction.adoc", "Introduction"),
                ("reference/cypher/cypher-tutorial.adoc", "Tutorial"),
                ("reference/cypher/cypher-clauses.adoc", "Clauses"),
                ("reference/cypher/cypher-expressions.adoc", "Expressions"),
                ("reference/cypher/cypher-compatibility.adoc", "Compatibility"),
            ]),
            # Single-page languages — collapsed from "<Lang> > <single child>"
            # to a single clickable entry that lands directly on the page.
            (("reference/gremlin/gremlin.adoc", "Gremlin"), []),
            (("reference/graphql/graphql.adoc", "GraphQL"), []),
            (("reference/mongodb-ql/mongo.adoc", "MongoDB QL"), []),
            (("reference/redis-ql/redis.adoc", "Redis"), []),
            (("reference/graph-algorithms/chapter.adoc", "Graph Algorithms"), [
                ("reference/graph-algorithms/path-finding.adoc", "Path Finding"),
                ("reference/graph-algorithms/centrality.adoc", "Centrality"),
                ("reference/graph-algorithms/community-detection.adoc", "Community Detection"),
                ("reference/graph-algorithms/structural-analysis.adoc", "Structural Analysis"),
                ("reference/graph-algorithms/similarity-link-prediction.adoc", "Similarity & Link Prediction"),
                ("reference/graph-algorithms/network-flow.adoc", "Network Flow"),
                ("reference/graph-algorithms/traversal-sampling.adoc", "Traversal & Sampling"),
                ("reference/graph-algorithms/network-science.adoc", "Network Science"),
                ("reference/graph-algorithms/community-quality.adoc", "Community Quality"),
                ("reference/graph-algorithms/graph-statistics.adoc", "Graph Statistics"),
                ("reference/graph-algorithms/node-embedding.adoc", "Node Embedding"),
                ("reference/graph-algorithms/sql-path-functions.adoc", "SQL Path Functions"),
                ("reference/graph-algorithms/notes.adoc", "Notes"),
            ]),
            (("reference/extended-functions.adoc", "Extended Functions"), [
                ("reference/extended-functions/aggregation.adoc", "Aggregation"),
                ("reference/extended-functions/collection-map.adoc", "Collection & Map"),
                ("reference/extended-functions/convert-create.adoc", "Convert & Create"),
                ("reference/extended-functions/date-math.adoc", "Date & Math"),
                ("reference/extended-functions/graph-elements.adoc", "Graph Elements"),
                ("reference/extended-functions/path-algorithms.adoc", "Path & Algorithms"),
                ("reference/extended-functions/schema-meta.adoc", "Schema & Meta"),
                ("reference/extended-functions/text.adoc", "Text"),
                ("reference/extended-functions/utility.adoc", "Utility"),
                ("reference/extended-functions/vector.adoc", "Vector"),
            ]),
        ],
    },
]


def first_heading(page_path: Path) -> str | None:
    if not page_path.exists():
        return None
    for line in page_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith((":", "//")):
            continue
        if s.startswith(("[[", "[#", "[discrete", "[id=")):
            continue
        m = HEADING_RE.match(s)
        if m:
            return m.group(1).replace("`", "").strip()
    return None


def normalize(entry):
    if isinstance(entry, tuple):
        return entry
    return (entry, None)


def render_nav(spec: dict, listed: set[str]) -> str:
    lines = [f".{spec['title']}"]
    for entry in spec.get("intro", []):
        path, label = normalize(entry)
        title = label or first_heading(PAGES / path) or path
        listed.add(path)
        lines.append(f"* xref:{path}[{title}]")
    for group_title, items in spec["groups"]:
        # Group header is either a plain string label (no link) or a
        # (path, label) tuple — in which case the header itself is a
        # clickable xref to a section landing page.
        if isinstance(group_title, tuple):
            header_path, header_label = group_title
            header_page = PAGES / header_path
            header_title = header_label or first_heading(header_page) or header_path
            listed.add(header_path)
            lines.append(f"* xref:{header_path}[{header_title}]")
        else:
            lines.append(f"* {group_title}")
        for entry in items:
            # Nested sub-group: (label, [child_items]) or ((path, label), [child_items])
            if isinstance(entry, tuple) and len(entry) == 2 and isinstance(entry[1], list):
                sub_title, sub_items = entry
                if isinstance(sub_title, tuple):
                    sub_path, sub_label = sub_title
                    sub_page = PAGES / sub_path
                    sub_t = sub_label or first_heading(sub_page) or sub_path
                    listed.add(sub_path)
                    lines.append(f"** xref:{sub_path}[{sub_t}]")
                else:
                    lines.append(f"** {sub_title}")
                for child in sub_items:
                    cpath, clabel = normalize(child)
                    cpage = PAGES / cpath
                    if not cpage.exists():
                        print(f"  WARN: nav references missing page {cpath}", file=sys.stderr)
                        continue
                    ctitle = clabel or first_heading(cpage) or cpath
                    listed.add(cpath)
                    lines.append(f"*** xref:{cpath}[{ctitle}]")
                continue
            path, label = normalize(entry)
            page = PAGES / path
            if not page.exists():
                print(f"  WARN: nav references missing page {path}", file=sys.stderr)
                continue
            title = label or first_heading(page) or path
            listed.add(path)
            lines.append(f"** xref:{path}[{title}]")
    return "\n".join(lines) + "\n"


def main() -> int:
    listed: set[str] = set()
    for spec in NAV_STRUCTURE:
        text = render_nav(spec, listed)
        out_path = NAV_DIR / spec["file"]
        out_path.write_text(text, encoding="utf-8")
        count = sum(1 for line in text.splitlines() if line.startswith("**"))
        print(f"Wrote {out_path.relative_to(REPO)} ({count} pages)")

    # Sanity: surface pages on disk that didn't make it into any nav,
    # excluding chapter aggregators (which the new structure replaces with
    # task-shaped groups) and the home page.
    on_disk = {
        p.relative_to(PAGES).as_posix()
        for p in PAGES.rglob("*.adoc")
        if p.name != "chapter.adoc"
    }
    on_disk.discard("index.adoc")
    missing = sorted(on_disk - listed)
    if missing:
        print(f"\n{len(missing)} pages exist on disk but are not in any nav:")
        for path in missing:
            print(f"  - {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
