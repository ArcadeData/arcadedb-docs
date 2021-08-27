[[SQL-Rebuild-Indexes]]
### SQL - `REBUILD INDEXES` image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Rebuild-Index.md" float=right]

Rebuilds automatic indexes.

**Syntax**

```sql
REBUILD INDEX <index>
```

- **`<index>`** Defines the index that you want to rebuild.  Use `*` to rebuild all automatic indexes.

NOTE: During the rebuild, any idempotent queries made against the index, skip the index and perform sequential scans.  This means that queries run slower during this operation.  Non-idempotent commands, such as <<SQL-Insert,`INSERT`>>, <<SQL-Update,`UPDATE`>>, and <<SQL-Delete,`DELETE`>> are blocked waiting until the indexes are rebuilt.

**Examples**

- Rebuild an index on the `nick` property on the type `Profile`:

```
ArcadeDB> REBUILD INDEX Profile.nick
```

- Rebuild all indexes:
  
```
ArcadeDB> REBUILD INDEX *
```

>For more information, see:

- <<SQL-Create-Index,`CREATE INDEX`>>
- <<SQL-Drop-Index,`DROP INDEX`>>
- <<Indexes>>
