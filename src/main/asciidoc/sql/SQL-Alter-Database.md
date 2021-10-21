[[SQL-Alter-Database]]
[discrete]

### SQL - `ALTER DATABASE`

image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Alter-Database.md" float=right]

Change a database setting. You can find the available settings in <<Settings,Settings>> appendix. The update is persistent.

**Syntax**

```sql
ALTER DATABASE <setting-name> <setting-value>
```

- **`<setting-name>`** Check the available settings in <<Settings,Settings>> appendix. Since the setting name contains `.`
  characters, surround the setting name with `\``.
- **`<setting-value>`** The new value to set

**Examples**

- Set the default page size for buckets to 262,144 bytes. This is useful when importing database with records bigger than the
  default page.

```
ArcadeDB> ALTER DATABASE `arcadedb.bucketDefaultPageSize` 262144
```
