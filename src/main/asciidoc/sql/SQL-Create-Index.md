[[SQL-Create-Index]]
[discrete]
### SQL - `CREATE INDEX` 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Create-Index.md" float=right]

Creates a new index.  Indexes can be
- **Unique** Where they don't allow duplicates.
- **Not Unique** Where they allow duplicates.
- **Full Text** Where they index any single word of text.

>There are several index algorithms available to determine how ArcadeDB indexes your database.  For more information on these, see <<Indexes,../indexing/Indexes>>.


**Syntax**

```sql
CREATE INDEX <name>
[ IF NOT EXISTS ]
[ ON <type> (<property>*) ] 
<index-type> [<key-type>]
```
- **`<name>`** Defines the logical name for the index.  If a schema already exists, you can use `<type>.<property>` to create automatic indexes bound to the schema property.  Because of this, you cannot use the period "`.`" character in index names.
- **IF NOT EXISTS** Specifying this option, the index creation will just be ignored if the index already exists (instead of failing with an error)
- **`<type>`** Defines the type to create an automatic index for.  The type must already exist.
- **`<property>`** Defines the property you want to automatically index.  The property must already exist.  

  >If the property is of the Map type (`MAP`) then you can specify the keys or values to use in index generation, using the `BY KEY` or `BY VALUE` clause.

- **`<index-type>`** Defines the index type you want to use.  For a complete list, see <<Indexes,../indexing/Indexes>>.
- **`<key-type>`** Defines the key type.  With automatic indexes, the key type is automatically selected when the database reads the target schema property.  For manual indexes, when not specified, it selects the key at run-time during the first insertion by reading the type of the type.  In creating composite indexes, it uses a comma-separated list of types.

To create an automatic index bound to the schema property, use the `ON` clause, or use a `<type>.<property>` name for the index.  In order to create an index, the schema must already exist in your database.

In the event that the `ON` and `<key-type>` clauses both exist, the database validates the specified property types.  If the property types don't equal those specified in the key type list, it throws an exception.

!NOTE: Null values are not indexed, so any query that is looking for null values will not use the index with a full scan.

>You can use list key types when creating manual composite indexes, but bear in mind that such indexes are not yet fully supported.


**Examples**

- Create a manual index to store dates:

```
ArcadeDB> CREATE INDEX mostRecentRecords UNIQUE DATE
```

- Create an automatic index bound to the new property `id` in the type `User`:

```
ArcadeDB> CREATE PROPERTY User.id BINARY
ArcadeDB> CREATE INDEX User.id UNIQUE
```

- Create a series automatic indexes for the `thumbs` property in the type `Movie`:

```
ArcadeDB> CREATE INDEX thumbsAuthor ON Movie (thumbs) UNIQUE
ArcadeDB> CREATE INDEX thumbsAuthor ON Movie (thumbs BY KEY) UNIQUE
ArcadeDB> CREATE INDEX thumbsValue ON Movie (thumbs BY VALUE) UNIQUE
```

- Create a series of properties and on them create a composite index:

```
ArcadeDB> CREATE PROPERTY Book.author STRING
ArcadeDB> CREATE PROPERTY Book.title STRING
ArcadeDB> CREATE PROPERTY Book.publicationYears EMBEDDEDLIST INTEGER
ArcadeDB> CREATE INDEX books ON Book (author, title, publicationYears) UNIQUE
```


- Create an index on an edge's date range:

```
ArcadeDB> CREATE VERTEX TYPE File
ArcadeDB> CREATE EDGE TYPE Has
ArcadeDB> CREATE PROPERTY Has.started DATETIME
ArcadeDB> CREATE PROPERTY Has.ended DATETIME
ArcadeDB> CREATE INDEX Has.started_ended ON Has (started, ended) NOTUNIQUE
```

  >You can create indexes on edge typees only if they contain the begin and end date range of validity.  This is use case is very common with historical graphs, such as the example above.

- Using the above index, retrieve all the edges that existed in the year 2014:

```
ArcadeDB> SELECT FROM Has WHERE started >= '2014-01-01 00:00:00.000' AND 
            ended < '2015-01-01 00:00:00.000'
```

- Using the above index, retrieve all edges that existed in 2014 and write them to the parent file:

```
ArcadeDB> SELECT outV() FROM Has WHERE started >= '2014-01-01 00:00:00.000' 
            AND ended < '2015-01-01 00:00:00.000'
```

- Using the above index, retrieve all the 2014 edges and connect them to children files:

```
ArcadeDB> SELECT inV() FROM Has WHERE started >= '2014-01-01 00:00:00.000' 
            AND ended < '2015-01-01 00:00:00.000'
```


- Create an index that includes null values.  

  By default, indexes ignore null values.  Queries against null values that use an index returns no entries.  To index null values, see `{ ignoreNullValues: false }` as metadata.

```
ArcadeDB> CREATE INDEX addresses ON Employee (address) NOTUNIQUE
```

For more information, see:

- <<SQL-Drop-Index,`DROP INDEX`>>
