[[SQL-Truncate-Type]]
### SQL - `TRUNCATE TYPE`

Deletes records of all buckets defined as part of the type.  

By default, every type has an associated bucket with the same name.  This command operates at a lower level than <<`DELETE`,SQL-Delete>>.  This commands ignores sub-typees, (That is, their records remain in their buckets).  If you want to also remove all records from the type hierarchy, you need to use the `POLYMORPHIC` keyword.

Truncation is not permitted on vertex or edge typees, but you can force its execution using the `UNSAFE` keyword.  Forcing truncation is strongly discouraged, as it can leave the graph in an inconsistent state.

**Syntax**

```
TRUNCATE TYPE <type> << POLYMORPHIC ] << UNSAFE ] 
```

- **`<type>`** Defines the type you want to truncate.
- **`POLYMORPHIC`** Defines whether the command also truncates the type hierarchy.
- **`UNSAFE`** Defines whether the command forces truncation on vertex or edge typees, (that is, sub-typees that extend the typees `V` or `E`).

**Examples**

- Remove all records of the type `Profile`:

  <pre>
  ArcadeDB> <code type='lang-sql userinput'>TRUNCATE TYPE Profile</code>
  </pre>

>For more information, see
>- <<`DELETE`,SQL-Delete>>
>- <<`TRUNCATE BUCKET`,SQL-Truncate-Bucket>>
>- <<`CREATE TYPE`,SQL-Create-Type>>
>- <<SQL Commands,SQL-Commands>>
>- <<Console Commands,../console/Console-Commands>>
