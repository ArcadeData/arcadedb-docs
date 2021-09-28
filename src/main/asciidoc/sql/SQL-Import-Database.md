[[SQL-Import-Database]]
[discrete]
### SQL - `IMPORT DATABASE`

image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Import-Database.md" float=right]

Executes an import of the database into the current one. Usually an import database is executed on an empty database, but it is
possible to execute on any database. In case of conflict (unique index key already existent, etc.), the conflicting records will not
be imported. The importer automatically recognize the file between the following formats:

- OrientDB database export
- Neo4J database export
- GraphML database export

**Syntax**

```sql
IMPORT DATABASE [ <url> ]
```

* **`<url>`** Defines the location of the file to import. Use:
** `file://` as prefix for files located on the same file system where ArcadeDB is running.
** `https://` and `http://` as prefix for remote files.

**Examples**

- Import the public OpenBeer database available as demo database for OrientDB and exported in TGZ file 

```
ArcadeDB> IMPORT DATABASE https://github.com/ArcadeData/arcadedb-datasets/raw/main/orientdb/OpenBeer.gz
```

