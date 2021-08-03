
### SQL - `TRUNCATE BUCKET`

Deletes all records of a bucket.  This command operates at a lower level than the standard <<`DELETE`,SQL-Delete>> command.

Truncation is not permitted on vertex or edge typees, but you can force its execution using the `UNSAFE` keyword.  Forcing truncation is strongly discouraged, as it can leave the graph in an inconsistent state.

**Syntax**

```
TRUNCATE BUCKET <bucket>
```

- **`<bucket>`** Defines the bucket to delete.
- **`UNSAFE`** Defines whether the command forces truncation on vertex or edge typees, (that is, sub-typees that extend the typees `V` or `E`).

**Examples**

- Remove all records in the bucket `profile`:

  <pre>
  ArcadeDB> <code type='lang-sql userinput'>TRUNCATE BUCKET profile</code>
  </pre>

>For more information, see
>- <<`DELETE`,SQL-Delete>>
>- <<`TRUNCATE TYPE`,SQL-Truncate-Type>>
>- <<SQL Commands,SQL-Commands>>
>- <<Console Commands,../console/Console-Commands>>
