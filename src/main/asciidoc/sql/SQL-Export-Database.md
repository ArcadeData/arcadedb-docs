[[SQL-Export-Database]]
[discrete]

### SQL - `EXPORT DATABASE`

image:
../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Export-Database.md" float=right]

Exports a database in the `exports` directory under the root directory where ArcadeDB is running.

**Syntax**

```sql
EXPORT DATABASE <url> [FORMAT "JSONL"|"GRAPHML"] [OVERWRITE TRUE|FALSE]
```

* **`<url>`** Defines the location of the file to export. Use:
  ** `file://` as prefix for files located on the same file system where ArcadeDB is running. For security reasons, it is not
  possible to provide an absolute or relative path to the file
* **`<FORMAT>`** The format of the export as a quoted string
  ** `JSONL` exports in JSONL format (one json per line)
  ** `GRAPHML` exports in the popular GraphML format. GraphML is supported by all the major Graph DBMS
* **`<OVERWRITE>`** Overwrite the export file if exists. Default is false.

**Examples**

- Export the current database under the `exports/` directory:

```
ArcadeDB> EXPORT DATABASE database.jsonl.tgz
```

- Export the current database in GraphML format, overwriting any existent file if present:

```
ArcadeDB> EXPORT DATABASE database.jsonl.tgz FORMAT 'GraphML' OVERWRITE true
```

