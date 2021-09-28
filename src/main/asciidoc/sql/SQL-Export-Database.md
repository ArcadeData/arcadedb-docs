[[SQL-Export-Database]]
[discrete]
### SQL - `EXPORT DATABASE`

image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Export-Database.md" float=right]

Exports a database into a JSONL file on the local filesystem where ArcadeDB is running.

**Syntax**

```sql
EXPORT DATABASE [ <url> ]
```

* **`<url>`** Defines the location of the file to export. Use:
  ** `file://` as prefix for files located on the same file system where ArcadeDB is running.

**Examples**

- Export the current database:

```
ArcadeDB> EXPORT DATABASE /temp/database.jsonl
```

