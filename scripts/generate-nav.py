#!/usr/bin/env python3
"""
Generate docs/modules/ROOT/nav*.adoc from an explicit, user-task-shaped
section structure.

The old generator walked the include tree of src/main/asciidoc/content.adoc,
which produced one giant Documentation sidebar that mixed concepts with Java
code with operations. This generator instead emits three sibling nav files
that show up as tabs in the sidebar:

  nav.adoc        — Documentation        (narrative: get started / build /
                                            model / operate / tools / use-cases)
  nav-query.adoc  — Query Languages      (SQL, Cypher, Gremlin, GraphQL,
                                            MongoDB QL, Redis, graph algorithms,
                                            vector functions)
  nav-api.adoc    — API Reference        (Java API, HTTP API, gRPC API, MCP)

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
            ("Get Started", [
                "tutorials/what-is-arcadedb.adoc",
                "tutorials/run.adoc",
                ("how-to/operations/docker.adoc", "Quick Start with Docker"),
                "tutorials/multimodel.adoc",
            ]),
            ("Build Applications", [
                "tutorials/embed-server.adoc",
                ("tutorials/java-tutorial.adoc", "10-Minute Java Tutorial (Embedded)"),
                ("tutorials/remote-tutorial.adoc", "10-Minute Java Tutorial (Remote)"),
                "tutorials/python-quickstart.adoc",
                "tutorials/javascript-quickstart.adoc",
                "tutorials/vector-search-tutorial.adoc",
                "tutorials/time-series-tutorial.adoc",
                ("how-to/connectivity/jdbc.adoc", "JDBC Driver"),
                ("how-to/connectivity/python.adoc", "Python Driver"),
                ("how-to/connectivity/http-nodejs.adoc", "HTTP from Node.js"),
                ("how-to/connectivity/http-csharp.adoc", "HTTP from C#"),
                ("how-to/connectivity/http-elixir.adoc", "HTTP from Elixir"),
                ("how-to/connectivity/postgres.adoc", "PostgreSQL Wire Protocol"),
                ("how-to/connectivity/bolt.adoc", "Neo4j Bolt Protocol"),
                ("how-to/connectivity/grafana.adoc", "Grafana Datasource"),
            ]),
            ("Data Modeling", [
                ("concepts/basics.adoc", "Records, Documents, Vertices & Edges"),
                "concepts/schema.adoc",
                "concepts/indexes.adoc",
                "concepts/inheritance.adoc",
                "concepts/transactions.adoc",
                "concepts/multi-model.adoc",
                "concepts/graphs.adoc",
                "concepts/timeseries.adoc",
                "concepts/vector-search.adoc",
                "concepts/databases.adoc",
                "concepts/high-availability.adoc",
                ("how-to/data-modeling/full-text-index.adoc", "Full-Text Index"),
                ("how-to/data-modeling/geospatial.adoc", "Geospatial Index"),
                ("how-to/data-modeling/materialized-views.adoc", "Materialized Views"),
                ("how-to/data-modeling/graph-olap.adoc", "Graph OLAP Engine"),
                ("how-to/data-modeling/vector-embeddings.adoc", "Vector Embeddings"),
                ("reference/datatypes.adoc", "Data Types"),
                ("reference/binary-types.adoc", "Binary Types (BLOB)"),
                ("reference/managing-dates.adoc", "Managing Dates"),
                ("reference/storage.adoc", "Storage Internals"),
                ("reference/lsm-tree.adoc", "LSM-Tree Algorithm"),
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
                ("how-to/operations/server.adoc", "Server Configuration"),
                ("how-to/operations/settings.adoc", "Changing Settings"),
                ("reference/settings.adoc", "Settings Reference"),
                ("how-to/operations/ha.adoc", "High Availability"),
                ("how-to/operations/backup.adoc", "Backup"),
                ("how-to/operations/auto-backup.adoc", "Automatic Backup"),
                ("how-to/operations/restore.adoc", "Restore"),
                "how-to/operations/monitoring.adoc",
                "how-to/operations/performance-tuning.adoc",
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
            ("BI & Analytics", [
                ("how-to/integrations/apache-superset.adoc", "Apache Superset"),
                ("how-to/integrations/grafana.adoc", "Grafana"),
                "how-to/integrations/metabase.adoc",
                ("how-to/integrations/power-bi.adoc", "Power BI"),
                "how-to/integrations/tableau.adoc",
            ]),
            ("Use Cases", [
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
            ("Help", [
                "appendix/community.adoc",
                ("appendix/issues.adoc", "Known Issues"),
                ("appendix/orientdb-differences.adoc", "OrientDB Differences"),
                ("appendix/neo4j-differences.adoc", "Neo4j Differences"),
                "reference/requirements.adoc",
            ]),
        ],
    },
    {
        "file": "nav-query.adoc",
        "title": "Query Languages",
        "intro": [],
        "groups": [
            ("SQL", [
                ("reference/sql/sql-introduction.adoc", "Introduction"),
                ("reference/sql-syntax.adoc", "SQL Syntax"),
                ("reference/sql/sql-projections.adoc", "Projections"),
                ("reference/sql/sql-pagination.adoc", "Pagination"),
                ("reference/sql/sql-where.adoc", "Filtering"),
                ("reference/sql/sql-select.adoc", "SELECT"),
                ("reference/sql/sql-insert.adoc", "INSERT"),
                ("reference/sql/sql-update.adoc", "UPDATE"),
                ("reference/sql/sql-delete.adoc", "DELETE"),
                ("reference/sql/sql-match.adoc", "MATCH"),
                ("reference/sql/sql-traverse.adoc", "TRAVERSE"),
                ("reference/sql/sql-move.adoc", "MOVE VERTEX"),
                ("reference/sql/sql-create-vertex.adoc", "CREATE VERTEX"),
                ("reference/sql/sql-create-edge.adoc", "CREATE EDGE"),
                ("reference/sql/sql-create-type.adoc", "CREATE TYPE"),
                ("reference/sql/sql-alter-type.adoc", "ALTER TYPE"),
                ("reference/sql/sql-drop-type.adoc", "DROP TYPE"),
                ("reference/sql/sql-truncate-type.adoc", "TRUNCATE TYPE"),
                ("reference/sql/sql-create-property.adoc", "CREATE PROPERTY"),
                ("reference/sql/sql-alter-property.adoc", "ALTER PROPERTY"),
                ("reference/sql/sql-drop-property.adoc", "DROP PROPERTY"),
                ("reference/sql/sql-create-bucket.adoc", "CREATE BUCKET"),
                ("reference/sql/sql-drop-bucket.adoc", "DROP BUCKET"),
                ("reference/sql/sql-truncate-bucket.adoc", "TRUNCATE BUCKET"),
                ("reference/sql/sql-create-index.adoc", "CREATE INDEX"),
                ("reference/sql/sql-rebuild-index.adoc", "REBUILD INDEX"),
                ("reference/sql/sql-drop-index.adoc", "DROP INDEX"),
                ("reference/sql/sql-create-trigger.adoc", "CREATE TRIGGER"),
                ("reference/sql/sql-drop-trigger.adoc", "DROP TRIGGER"),
                ("reference/sql/sql-create-materialized-view.adoc", "CREATE MATERIALIZED VIEW"),
                ("reference/sql/sql-alter-materialized-view.adoc", "ALTER MATERIALIZED VIEW"),
                ("reference/sql/sql-drop-materialized-view.adoc", "DROP MATERIALIZED VIEW"),
                ("reference/sql/sql-refresh-materialized-view.adoc", "REFRESH MATERIALIZED VIEW"),
                ("reference/sql/sql-align-database.adoc", "ALIGN DATABASE"),
                ("reference/sql/sql-alter-database.adoc", "ALTER DATABASE"),
                ("reference/sql/sql-backup-database.adoc", "BACKUP DATABASE"),
                ("reference/sql/sql-check-database.adoc", "CHECK DATABASE"),
                ("reference/sql/sql-export-database.adoc", "EXPORT DATABASE"),
                ("reference/sql/sql-import-database.adoc", "IMPORT DATABASE"),
                ("reference/sql/sql-explain.adoc", "EXPLAIN"),
                ("reference/sql/sql-profile.adoc", "PROFILE"),
                ("reference/sql/sql-console.adoc", "CONSOLE"),
                ("reference/sql/sql-script.adoc", "SCRIPT"),
                ("reference/sql/sql-functions.adoc", "Functions"),
                ("reference/sql/sql-methods.adoc", "Methods"),
                ("reference/sql/sql-triggers.adoc", "Triggers"),
                ("reference/sql/sql-custom-functions.adoc", "Custom Functions"),
                ("reference/sql/sql-select-execution.adoc", "SELECT Execution Model"),
                ("reference/extended-functions.adoc", "Extended Functions (APOC)"),
            ]),
            ("Cypher (openCypher)", [
                ("reference/cypher/cypher-overview.adoc", "Overview"),
                ("reference/cypher/cypher-introduction.adoc", "Introduction"),
                ("reference/cypher/cypher-tutorial.adoc", "Tutorial"),
                ("reference/cypher/cypher-clauses.adoc", "Clauses"),
                ("reference/cypher/cypher-expressions.adoc", "Expressions"),
                ("reference/cypher/cypher-compatibility.adoc", "Compatibility"),
            ]),
            ("Gremlin", [
                ("reference/gremlin/gremlin.adoc", "Apache TinkerPop Gremlin"),
            ]),
            ("GraphQL", [
                "reference/graphql/graphql.adoc",
            ]),
            ("MongoDB QL", [
                ("reference/mongodb-ql/mongo.adoc", "MongoDB Query Language"),
            ]),
            ("Redis", [
                ("reference/redis-ql/redis.adoc", "Redis Commands"),
            ]),
            ("Graph Algorithms", [
                ("reference/graph-algorithms/algorithms.adoc", "Algorithms Reference"),
                ("appendix/graph-algorithms.adoc", "Algorithms Appendix"),
            ]),
            ("Vector Functions", [
                ("reference/vector-functions/distance-similarity.adoc", "Distance & Similarity"),
                ("reference/vector-functions/manipulation.adoc", "Manipulation"),
                ("reference/vector-functions/quantization.adoc", "Quantization"),
                ("reference/vector-functions/scoring.adoc", "Scoring"),
                ("reference/vector-functions/sparse-vectors.adoc", "Sparse Vectors"),
            ]),
        ],
    },
    {
        "file": "nav-api.adoc",
        "title": "API Reference",
        "intro": [],
        "groups": [
            ("Java API", [
                ("reference/java-api/java-reference.adoc", "Overview"),
                ("reference/java-api/java-ref-database-factory.adoc", "DatabaseFactory"),
                ("reference/java-api/java-ref-database.adoc", "Database"),
                ("reference/java-api/java-ref-database-async.adoc", "Async Database"),
                ("reference/java-api/java-api-local.adoc", "Embedded (Local) Client"),
                ("reference/java-api/java-api-remote.adoc", "Remote Client"),
                ("reference/java-api/java-api-grpc.adoc", "gRPC Client"),
                ("reference/java-api/java-schema.adoc", "Schema API"),
                ("reference/java-api/java-embeddeddoc.adoc", "Embedded Documents"),
                ("reference/java-api/java-events.adoc", "Events"),
                ("reference/java-api/java-batch-importer.adoc", "Batch Importer"),
                ("reference/java-api/java-select-api.adoc", "Select API"),
                ("reference/java-api/java-vectors.adoc", "Vectors"),
            ]),
            ("HTTP API", [
                ("reference/http-api/http.adoc", "REST API"),
            ]),
            ("gRPC API", [
                ("reference/grpc-api/grpc-services.adoc", "Services"),
                ("reference/grpc-api/grpc-messages.adoc", "Messages"),
            ]),
            ("MCP Server", [
                ("reference/mcp/mcp.adoc", "Model Context Protocol Server"),
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
        lines.append(f"* {group_title}")
        for entry in items:
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
