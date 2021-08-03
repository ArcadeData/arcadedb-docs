[[SQL-Rebuild-Indexes]]
### SQL - `REBUILD INDEXES`

Rebuilds automatic indexes.

**Syntax**

```sql
REBUILD INDEX <index>
```

- **`<index>`** Defines the index that you want to rebuild.  Use `*` to rebuild all automatic indexes.

>**NOTE**: During the rebuild, any idempotent queries made against the index, skip the index and perform sequential scans.  This means that queries run slower during this operation.  Non-idempotent commands, such as <<`INSERT`,SQL-Insert>>, <<`UPDATE`,SQL-Update>>, and <<`DELETE`,SQL-Delete>> are blocked waiting until the indexes are rebuilt.

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
