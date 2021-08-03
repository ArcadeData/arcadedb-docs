
### SQL - `CREATE PROPERTY`

Creates a new property in the schema.  It requires that the type for the property already exist on the database.

**Syntax**

```
CREATE PROPERTY 
<type>.<property> <type> 
<<<link-type>|<link-type>] 
( <property constraint> <<, <property-constraint>]* ) 
<<UNSAFE]
```

- **`<type>`** Defines the type for the new property.
- **`<property>`** Defines the logical name for the property.
- **`<type>`** Defines the property data type.  For supported types, see the table below.
- **`<link-type>`** Defines the contained type for container property data types.  For supported link types, see the table below.
- **`<link-type>`** Defines the contained type for container property data types.  For supported link types, see the table below.
- **`<property-constraint>`** See <<`ALTER PROPERTY`,SQL-Alter-Property>> `<attribute-name> << <attribute-value> ]` (since V2.2.3)
- **`UNSAFE`** Defines whether it checks existing records.  On larger databases, with millions of records, this could take a great deal of time.  Skip the check when you are sure the property is new.  Introduced in version 2.0.


>When you create a property, ArcadeDB checks the data for property and type.  In the event that persistent data contains incompatible values for the specified type, the property creation fails.  It applies no other constraints on the persistent data.

**Examples**

- Create the property `name` of the string type in the type `User`:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE PROPERTY User.name STRING</code>
  </pre>

- Create a property formed from a list of strings called `tags` in the type `Profile`:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE PROPERTY Profile.tags EMBEDDEDLIST STRING</code>
  </pre>

- Create the property `friends`, as an embedded map in a circular reference:

  <pre>
  ArcadeDB> <code type='lang-sql userinput'>CREATE PROPERTY Profile.friends EMBEDDEDMAP Profile</code>
  </pre>

- Create the property `name` of the string type in the type `User`, mandatory, with minimum and maximum length (since V2.2.3):

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE PROPERTY User.name STRING (MANDATORY TRUE, MIN 5, MAX 25)  </code>
  </pre>



>For more information, see
>
>- <<`DROP PROPERTY`,SQL-Drop-Property>>
>- <<SQL Commands,SQL-Commands>>
>- <<Console Commands,../console/Console-Commands>>


#### Supported Types

ArcadeDB supports the following data types for standard properties:

| | | | | |
|---|---|---|---|---|
| `BOOLEAN` | `SHORT` | `DATE` | `DATETIME` | `BYTE`|
| `INTEGER` | `LONG` | `STRING` | `LINK` | `DECIMAL` |
| `DOUBLE` | `FLOAT` | `BINARY` | `EMBEDDED` | `LINKBAG` |

It supports the following data types for container properties.  

||||
|---|---|---|
| `EMBEDDEDLIST` | `EMBEDDEDSET` | `EMBEDDEDMAP` |
| `LINKLIST` | `LINKSET` | `LINKMAP` |

For these data types, you can optionally define the contained type and type.  The supported link types are the same as the standard property data types above.


