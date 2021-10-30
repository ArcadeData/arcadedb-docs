[[SQL-Alter-Property]]
[discrete]

### SQL - `ALTER PROPERTY`

image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Alter-Property.md" float=right]

Change a property defined in the schema. The change is persistent.

**Syntax**

```sql
ALTER PROPERTY <type-name>.<property-name> <attribute-name> = <attribute-value>
```

- **`<type-name>`** Defines the type where the property is defined.
- **`<property-name>`** Defines the property in the `type-name` you want to change.
- **`<attribute-name>`** Defines the attribute you want to change. For a list of supported attributes, see the table below.
- **`<attribute-value>`** Defines the value you want to set.

**Examples**

- Set the custom value with key 'description': 

```
ArcadeDB> ALTER PROPERTY User.subscribedOn CUSTOM description = 'timestamp when the user subscribed'
```

- Remove the custom value set above

```
ArcadeDB> ALTER PROPERTY User.subscribedOn CUSTOM description = null
```

For more information, see:

- <<SQL-Create-Type,`CREATE PROPERTY`>>
- <<SQL-Drop-Type,`DROP PROPERTY`>>.
