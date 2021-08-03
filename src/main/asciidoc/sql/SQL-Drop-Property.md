[[SQL-Drop-Property]]
### SQL - `DROP PROPERTY`

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

  <pre>
  ArcadeDB> <code type="lang-sql userinput">DROP PROPERTY User.name</code>
  </pre>


>For more information, see
>- <<`CREATE PROPERTY`,SQL-Create-Property>>
>- <<SQL Commands,SQL-Commands>>
>- <<Console Commands,../console/Console-Commands>>
