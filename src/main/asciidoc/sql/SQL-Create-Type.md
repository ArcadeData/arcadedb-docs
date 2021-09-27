### SQL - `CREATE TYPE`

image:
../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Create-Type.md" float=right]

Creates a new type in the schema.

**Syntax**

```sql
CREATE <DOCUMENT|VERTEX|EDGE> TYPE <type> 
[ IF NOT EXISTS ]
[EXTENDS <super-type>] [BUCKET <bucket-id>*] [BUCKETS <total-bucket-number>]
```

- Use **`<DOCUMENT|VERTEX|EDGE>` if you are creating respectively a document, vertex or edge type.
- **`<type>`** Defines the name of the type you want to create. You must use a letter, underscore or dollar for the first character,
  for all other characters you can use alphanumeric characters, underscores and dollar.
- **IF NOT EXISTS** Specifying this option, the type creation will just be ignored if the type already exists (instead of failing
  with an error)
- **`<super-type>`** Defines the super-type you want to extend with this type.
- **`<bucket-id>`**  Defines in a comma-separated list the ID's of the buckets you want this type to use.
- **`<total-bucket-number>`** Defines the total number of buckets you want to create for this type. The default value is `1`.

In the event that a bucket of the same name exists in the bucket, the new type uses this bucket by default. If you do not define a
bucket in the command and a bucket of this name does not exist, ArcadeDB creates one. The new bucket has the same name as the type,
but in lower-case.

When working with multiple cores, it is recommended that you use multiple buckets to improve concurrency during inserts. To change
the number of buckets created by default, <<`ALTER DATABASE`,SQL-Alter-Database>> command to update the `minimumbuckets` property.
You can also define the number of buckets you want to create using the `BUCKETS` option when you create the type.

**Examples**

- Create the document type `Account`:

```
ArcadeDB> CREATE DOCUMENT TYPE Account
```

- Create the vertex type `Car` to extend `Vehicle`:

```
ArcadeDB> CREATE VERTEX TYPE Car EXTENDS Vehicle
```

- Create the vertex type `Car`, using the bucket ID of `10`:

```
ArcadeDB> CREATE TYPE Car BUCKET 10
```

**Bucket Selection Strategies**

When you create a type, it inherits the bucket selection strategy defined at the database-level. By default, this is set to
`round-robin`. You can change the database default using the <<`ALTER DATABASE`,SQL-Alter-Database>> command and the selection
strategy for the type using the <<`ALTER TYPE`,SQL-Alter-Type>> command.

Supported Strategies:

[%header,cols=2]
|===
| Strategy | Description
| `round-robin` | Selects the next bucket in a circular order, restarting once complete.
| `thread` | Selects the next bucket by using the partition (mod) from the current thread id.
| `partitioned` | Selects the smallest bucket. Allows the type to have
all underlying buckets balanced on size. When adding a new bucket to an existing type, it fills the new bucket first. When using a
distributed database, this keeps the servers balanced with the same amount of data. It calculates the bucket size every five seconds
or more to avoid slow-downs on insertion.
|===

> For more information, see:

- <<SQL-Alter-Type,`ALTER TYPE`>>
- <<SQL-Drop-Type,`DROP TYPE`>>
- <<SQL-Create-Bucket,`CREATE BUCKET`>>

