[[SQL-Explain]]
### SQL - `EXPLAIN` 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Explain.md" float=right]

EXPLAIN SQL command returns information about query execution planning of a specific statement, without executing the statement itself.

**Syntax**

```
EXPLAIN <command>
```

- **`<command>`** Defines the command that you want to profile, eg. a SELECT statement

**Examples**


- Profile a query that executes on a type filtering based on an attribute:

```
  ArcadeDB {db=foo}> explain select from v where name = 'a'

  Profiled command '[{

  executionPlan:{...},

  executionPlanAsString:

  + FETCH FROM TYPE v
    + FETCH FROM BUCKET 9 ASC
    + FETCH FROM BUCKET 10 ASC
    + FETCH FROM BUCKET 11 ASC
    + FETCH FROM BUCKET 12 ASC
    + FETCH FROM BUCKET 13 ASC
    + FETCH FROM BUCKET 14 ASC
    + FETCH FROM BUCKET 15 ASC
    + FETCH FROM BUCKET 16 ASC
    + FETCH NEW RECORDS FROM CURRENT TRANSACTION SCOPE (if any)
  + FILTER ITEMS WHERE 
    name = 'a'
  
  }]' in 0,022000 sec(s):

```

>For more information, see:

- <<SQL-Commands,SQL Commands>>
- <<SQL-Profile,PROFILE>>

