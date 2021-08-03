[[SQL-Truncate-Bucket]]
### SQL - `TRUNCATE BUCKET`

Deletes all records of a bucket.  This command operates at a lower level than the standard <<`DELETE`,SQL-Delete>> command.

Truncation is not permitted on vertex or edge typees, but you can force its execution using the `UNSAFE` keyword.  Forcing truncation is strongly discouraged, as it can leave the graph in an inconsistent state.

**Syntax**

```
TRUNCATE BUCKET <bucket>
```

- **`<bucket>`** Defines the bucket to delete.
- **`UNSAFE`** Defines whether the command forces truncation on vertex or edge types, (that is, sub-types that extend the types `V` or `E`).

**Examples**

- Remove all records in the bucket `profile`:

```
ArcadeDB> TRUNCATE BUCKET profile
```

>For more information, see:

- <<SQL-Delete,`DELETE`>>
- <<SQL-Truncate-Type,`TRUNCATE TYPE`>>
