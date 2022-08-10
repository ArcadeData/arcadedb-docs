[[SQL-Create-Property]]
[discrete]
### SQL - `CREATE PROPERTY` 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Create-Property.md" float=right]

Creates a new property in the schema.  It requires that the type for the property already exist on the database.

**Syntax**

```
CREATE PROPERTY 
<type>.<property> <data-type> 
( <property-constraint> [, <property-constraint>]* ) 
```

- **`<type>`** Defines the type for the new property.
- **`<property>`** Defines the logical name for the property.
- **`<data-type>`** Defines the property data type.  For supported types, see the table below.
- **`<property-constraint>`** See <<SQL-Alter-Property,`ALTER PROPERTY`>> `<attribute-name> << <attribute-value>`
** `mandatory = <true|false>` If true, the property must be present. Default is false
** `notnull = <true|false>` If true, the property, if present, cannot be null. Default is false
** `readonly = <true|false>` If true, the property cannot be changed after the creation of the record. Default is false
** `min = <number|string>` Defines the minimum value for this property. For number types it is the minimum number as a value. For strings it represents the minimum number of characters. For dates is the minimum date (uses the database date format)
** `max = <number|string>` Defines the maximum value for this property. For number types it is the maximum number as a value. For strings it represents the maximum number of characters. For dates is the maximum date (uses the database date format)
** `regexp = <string>` Defines the mask to validate the input as a Regular Expression

NOTE: When you create a property, ArcadeDB checks the data for property and type.  In the event that persistent data contains incompatible values for the specified type, the property creation fails.  It applies no other constraints on the persistent data.

**Examples**

- Create the property `name` of the string type in the type `User`:

```
ArcadeDB> CREATE PROPERTY User.name STRING
```

- Create a property formed from a list of strings called `tags` in the type `Profile`:

```
ArcadeDB> CREATE PROPERTY Profile.tags LIST
```

- Create the property `friends`, as an embedded map:

```
ArcadeDB> CREATE PROPERTY Profile.friends MAP
```

- Create the property `date` of type date with additional constraints:

```
ArcadeDB> CREATE PROPERTY Transaction.createdOn DATE mandatory = true, notnull = true, readonly = true, min = "2010-01-01"
```

For more information, see:

- <<SQL-Alter-Property,`ALTER PROPERTY`>>
- <<SQL-Drop-Property,`DROP PROPERTY`>>


**Supported Types**

ArcadeDB supports the following data types for standard properties:

[%header,cols=5]
|===
| `BOOLEAN` | `SHORT` | `DATE` | `DATETIME` | `BYTE`
| `INTEGER` | `LONG` | `STRING` | `LINK` | `DECIMAL` 
| `DOUBLE` | `FLOAT` | `BINARY` | `EMBEDDED` | 
|===

It supports the following data types for container properties.  

[%header,cols=2]
|===
| `LIST` |  `MAP`
|===

For these data types, you can optionally define the contained type and type.  The supported link types are the same as the standard property data types above.

