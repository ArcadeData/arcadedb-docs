[[SQL-Drop-Property]]
### SQL - `DROP PROPERTY` 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Drop-Property.md" float=right]

Removes a property from the schema.  Does not remove the property values in the records, it just changes the schema information.  Records continue to have the property values, if any.

**Syntax**

```sql
DROP PROPERTY <type>.<property> <<FORCE]
```

- **`<type>`** Defines the type where the property exists.
- **`<property>`** Defines the property you want to remove.
- **FORCE** In case one or more indexes are defined on the property, the command will throw an exception. Use FORCE to drop indexes together with the property

**Examples**

- Remove the `name` property from the type `User`:

```
ArcadeDB> DROP PROPERTY User.name
```


>For more information, see:

- <<SQL-Create-Property,`CREATE PROPERTY`>>
