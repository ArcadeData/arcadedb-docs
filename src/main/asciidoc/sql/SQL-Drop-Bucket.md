[[SQL-Drop-Bucket]]
[discrete]
### SQL - `DROP BUCKET` 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Drop-Bucket.md" float=right]

Removes the bucket and all of its content.  This operation is permanent and cannot be rolled back.

**Syntax**

```sql
DROP BUCKET <bucket-name>|<bucket-id>
```

- **`<bucket-name>`** Defines the name of the bucket you want to remove.
- **`<bucket-id>`** Defines the ID of the bucket you want to remove.

**Examples**

- Remove the bucket `Account`:

```
ArcadeDB> DROP BUCKET Account
```

>For more information, see:

- <<SQL-Create-Bucket,`CREATE BUCKET`>>
- <<SQL-Alter-Bucket,`ALTER BUCKET`>>
- <<SQL-Drop-Type,`DROP TYPE`>>

