[[SQL-Create-Property]]
[discrete]
### SQL - `CREATE PROPERTY` 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Create-Property.md" float=right]

Creates a new property in the schema.  It requires that the type for the property already exist on the database.

**Syntax**

```
CREATE PROPERTY 
<type>.<property> <data-type> 
[<link-type>|<link-type>] 
( <property-constraint> [, <property-constraint>]* ) 
[UNSAFE]
```

- **`<type>`** Defines the type for the new property.
- **`<property>`** Defines the logical name for the property.
- **`<data-type>`** Defines the property data type.  For supported types, see the table below.
- **`<link-type>`** Defines the contained type for container property data types.  For supported link types, see the table below.
- **`<link-type>`** Defines the contained type for container property data types.  For supported link types, see the table below.
- **`<property-constraint>`** See <<`ALTER PROPERTY`,SQL-Alter-Property>> `<attribute-name> << <attribute-value> ]`
- **`UNSAFE`** Defines whether it checks existing records.  On larger databases, with millions of records, this could take a great deal of time.  Skip the check when you are sure the property is new.


>When you create a property, ArcadeDB checks the data for property and type.  In the event that persistent data contains incompatible values for the specified type, the property creation fails.  It applies no other constraints on the persistent data.

**Examples**

- Create the property `name` of the string type in the type `User`:

```
ArcadeDB> CREATE PROPERTY User.name STRING
```

- Create a property formed from a list of strings called `tags` in the type `Profile`:

```
ArcadeDB> CREATE PROPERTY Profile.tags EMBEDDEDLIST STRING
```

- Create the property `friends`, as an embedded map in a circular reference:

```
ArcadeDB> CREATE PROPERTY Profile.friends EMBEDDEDMAP Profile
```



>For more information, see:

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


