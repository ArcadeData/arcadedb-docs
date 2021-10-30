[[SQL-Alter-Type]]
[discrete]

### SQL - `ALTER TYPE`

image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Alter-Type.md" float=right]

Change a type defined in the schema. The change is persistent.

**Syntax**

```sql
ALTER TYPE <type> [<attribute-name> <attribute-value>] [CUSTOM <custom-key> <custom-value>]
```

- **`<type>`** Defines the type you want to change.
- **`<attribute-name>`** Defines the attribute you want to change. For a list of supported attributes, see the table below.
- **`<attribute-value>`** Defines the value you want to set.
- **`<custom-key>`** Defines the custom property you want to define.
- **`<custom-value>`** Defines the custom value for the property you want to set. Supported types are strings and numbers.

**Examples**

- Define a super-type:

```
ArcadeDB> ALTER TYPE Employee SUPERTYPE Person
```

- Add `Person' to the super types:

```
ArcadeDB> ALTER TYPE Employee SUPERTYPE +Person
```

- Remove a super-type:

```
ArcadeDB> ALTER TYPE Employee SUPERTYPE -Person
```

- Define multiple inheritances:

```
ArcadeDB> ALTER TYPE Employee SUPERTYPES Person, `Resource`
```

- Add the "account2" bucket to the type `Account`.

```
ArcadeDB> ALTER TYPE Account BUCKET +account2
```

In the event that the bucket does not exist, it automatically creates it.

- Remove a bucket from the type `Account` with the ID `34`:

```
ArcadeDB> ALTER TYPE Account BUCKET -34
```

- Set the custom value with key 'description':

```
ArcadeDB> ALTER TYPE Account CUSTOM description = 'All users'
```

For more information, see:

- <<SQL-Create-Type,`CREATE TYPE`>>
- <<SQL-Drop-Type,`DROP TYPE`>>.

## Supported Attributes

[%header,cols="20%,20%,20%,40%",stripes=even]
|===
| Attribute | Type | Support| Description
| `NAME` | Identifier | | Changes the type name. 
| `SUPERTYPE` | Identifier | |Defines a super-type for the type. Use `NULL` to remove a super-type assignment. Beginning with version 2.1, it supports multiple
inheritances. To add a new type, you can use the syntax `+<type>`, to remove it use `-<type>`. 
| `BUCKET` | Identifier or Integer | | `+` to add a bucket
and `-` to remove it from the type. If the bucket doesn't exist, it creates a physical bucket. Adding buckets to a type is also
useful in storing records in distributed servers.
|===
