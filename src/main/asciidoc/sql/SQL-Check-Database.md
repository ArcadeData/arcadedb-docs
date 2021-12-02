[[SQL-Check-Database]]
[discrete]

### SQL - `CHECK DATABASE`

image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Check-Database.md" float=right]

Executes an integrity check and in case a repair of the database. This commands analizes the following things:

- buckets: all the pages and records are scanned and checked if can be loaded (no physical corruption)
- vertices: all the vertices are loaded and all the connected edges are checked. In case some edges point to records that have been
  deleted they can be fixed automatically if the `FIX` option is enabled.
- edges: scan all the edges and check the incoming and outgoing links are consistent in the relative vertices. If not, the edges can
  be automatically removed if the `FIX` option is enabled.

**Syntax**

```sql
CHECK DATABASE [ TYPE <type-name>[,]* ] [ BUCKET <bucket-name>[,]* ] [ FIX ]
```

- **`<type-name>`** Optional, if specified limit the check (and the fix) only to the specific types
- **`<bucket-name>`** Optional, if specified limit the check (and the fix) only to the specific buckets
- **`FIX`** Optional, if defined autofix the issue found with the check

The command returns the integrity check report in one record.

**Examples**

- Execute the integrity check of the entire database without fixing any issue found.

```
ArcadeDB> CHECK DATABASE
```

- Execute the integrity check of the types 'Account' and 'Bill' without fixing any issue found.

```
ArcadeDB> CHECK DATABASE BUCKET "Account", "Bill"
```

- Execute the integrity check of the entire database and autofix any issues found.

```
ArcadeDB> CHECK DATABASE FIX
```

