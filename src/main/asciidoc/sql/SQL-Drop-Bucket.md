[[SQL-Drop-Bucket]]
### SQL - `DROP BUCKET`

Removes the bucket and all of its content.  This operation is permanent and cannot be rolled back.

**Syntax**

```sql
DROP BUCKET <bucket-name>|<bucket-id>
```

- **`<bucket-name>`** Defines the name of the bucket you want to remove.
- **`<bucket-id>`** Defines the ID of the bucket you want to remove.

**Examples**

- Remove the bucket `Account`:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">DROP BUCKET Account</code>
  </pre>

>For more information, see
>- <<`CREATE BUCKET`,SQL-Create-Bucket>>
>- <<`ALTER BUCKET`,SQL-Alter-Bucket>>
>- <<`DROP TYPE`,SQL-Drop-Type>>
>- <<SQL Commands,SQL-Commands>>
>- <<Console Commands,../console/Console-Commands>>
