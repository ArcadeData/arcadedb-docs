[[SQL-Delete]]
### SQL - `DELETE` 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Delete.md" float=right]

Removes one or more records from the database.  You can refine the set of records that it removes using the <<SQL-Where,`WHERE`>> clause.

**Syntax:**

```sql
DELETE FROM <Type>|BUCKET:<bucket>|INDEX:<index> [RETURN <returning>]
  [WHERE <Condition>*] [LIMIT <MaxRecords>] [TIMEOUT <timeout>]
```
- **`RETURN`** Defines  what values the database returns.  It takes one of the following values:
  - `COUNT` Returns the number of deleted records.  This is the default option.
  - `BEFORE` Returns the number of records before the removal.
- **<<SQL-Where,`WHERE`>>** Filters to the records you want to delete.
- **`LIMIT`** Defines the maximum number of records to delete.
- **`TIMEOUT`** Defines the time period to allow the operation to run, before it times out.
- **`UNSAFE`** Allows for the processing of a DELETE on a Vertex or an Edge, without an exception error. It is not recommended to use this! If you must delete an Edge or a Vertex, use the corresponding commands DELETE EDGE or DELETE VERTEX.   

**Examples:**

- Delete all records with the surname `unknown`, ignoring case:

```
ArcadeDB> DELETE FROM Profile WHERE surname.toLowerCase() = 'unknown'
```



