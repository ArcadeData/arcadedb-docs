
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

  <pre>
  ArcadeDB> <code type='lang-sql userinput'>REBUILD INDEX Profile.nick</code>
  </pre>

- Rebuild all indexes:
  
  <pre>
  ArcadeDB> <code type='lang-sql userinput'>REBUILD INDEX *</code>
  </pre>

>For more information, see
>- <<`CREATE INDEX`,SQL-Create-Index>>
>- <<`DROP INDEX`,SQL-Drop-Index>>
>- <<Indexes,../indexing/Indexes>>
>- <<SQL Commands,SQL-Commands>>
