[[SQL-Drop-Type]]
### SQL - `DROP TYPE`

Removes a type from the schema.

**Syntax**

```sql
DROP TYPE <type> << UNSAFE ]
```

- **`<type>`** Defines the type you want to remove.
- **`UNSAFE`** Defines whether the command drops non-empty edge and vertex typees.  Note, this can disrupt data consistency.  Be sure to create a backup before running it.



>**NOTE**: Bear in mind, that the schema must remain coherent.  For instance, avoid removing calsses that are super-typees to others.  This operation won't delete the associated bucket.

**Examples**

- Remove the type `Account`:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">DROP TYPE Account</code>
  </pre>


>For more information, see
>- <<`CREATE TYPE`,SQL-Create-Type>>
>- <<`ALTER TYPE`,SQL-Alter-Type>>
>- <<`ALTER BUCKET`,SQL-Alter-Bucket>>
>- <<SQL Commands,SQL-Commands>>
