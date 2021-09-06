[[SQL-Create-Bucket]]
### SQL - `CREATE BUCKET` 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Create-Bucket.md" float=right]

Creates a new bucket in the database.  Once created, you can use the bucket to save records by specifying its name during saves.  If you want to add the new bucket to a type, follow its creation with the <<`ALTER TYPE`,SQL-Alter-Type>> command, using the `ADDBUCKET` option.


**Syntax**

```sql
CREATE BUCKET <bucket> [ID <bucket-id>]
```

- **`<bucket>`** Defines the name of the bucket you want to create.  You must use a letter for the first character, for all other characters, you can use alphanumeric characters, underscores and dashes.
- **`<bucket-id>`** Defines the numeric ID you want to use for the bucket.

**Examples**

- Create the bucket `account`:

```
ArcadeDB> CREATE BUCKET account
```

>For more information see:

- <<SQL-Drop-Bucket,`DROP BUCKET`>>
