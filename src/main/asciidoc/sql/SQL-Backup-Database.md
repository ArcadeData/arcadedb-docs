[[SQL-Backup-Database]]
[discrete]
### SQL - `BACKUP DATABASE`

image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Backup-Database.md" float=right]

Executes a backup of the current database. The resulting file is a compressed archive using ZIP as algorithm. The archive contains
the database directory without the transaction logs. The backup is executed taking a snapshot of the database at the time the
command is executed. Any pending transaction will not be in the backup archive. ArcadeDB allows to execute a non-stop backup of a
database while it is used without blocking writes or affecting performance.

**Syntax**

```sql
BACKUP DATABASE [ <backup-file-url> ]
```

- **`<backup-file-url>`** Optional, defines the location for the backup archive. If not specified, the backup file will
  be `backups/<db-name>/<db-name>-backup-<timestamp>.tgz`, where the timestamp is expresses from the year to the millisecond.
  Example of backup file name `backups/TheMatrix/TheMatrix-backup-20210921-172750767.zip`.

**Examples**

- Execute the backup of the current database with the default filename.

```
ArcadeDB> BACKUP DATABASE
```

