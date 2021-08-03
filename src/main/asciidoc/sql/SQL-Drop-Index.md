[[SQL-Drop-Index]]
### SQL - `DROP INDEX`

Removes an index from a property defined in the schema.

If the index does not exist, this call just returns with no errors.

**Syntax**

```sql
DROP INDEX <index>|<type>.<property> << IF EXISTS ]
```

- **`<index>`** Defines the name of the index.
- **`<type>`** Defines the type the index uses.
- **`<property>`** Defines the property the index uses.

**Examples**

- Remove the index on the `Id` property of the `Users` type:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">DROP INDEX Users.Id</code>
  </pre>


>For more information, see
>- <<`CREATE INDEX`,SQL-Create-Index>>
>- <<Indexes,../indexing/Indexes>>
>- <<SQL Commands,SQL-Commands>>
