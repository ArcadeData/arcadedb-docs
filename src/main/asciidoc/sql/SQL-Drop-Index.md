[[SQL-Drop-Index]]
### SQL - `DROP INDEX` 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Drop-Index.md" float=right]

Removes an index from a property defined in the schema.

If the index does not exist, this call just returns with no errors.

**Syntax**

```sql
DROP INDEX <index>|<type>.<property> [ IF EXISTS ]
```

- **`<index>`** Defines the name of the index.
- **`<type>`** Defines the type the index uses.
- **`<property>`** Defines the property the index uses.

**Examples**

- Remove the index on the `Id` property of the `Users` type:

```
ArcadeDB> DROP INDEX Users.Id
```


>For more information, see:
 
- <<SQL-Create-Index,`CREATE INDEX`>>
- <<Indexes,Indexes>>

