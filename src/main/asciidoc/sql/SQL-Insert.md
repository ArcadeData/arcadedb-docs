[[SQL-Insert]]
### SQL - `INSERT`

The <<`INSERT`,SQL-Insert>> command creates a new record in the database.  Records can be schema-less or follow rules specified in your model.

**Syntax**:

```sql
INSERT INTO <<TYPE:]<type>|BUCKET:<bucket>|INDEX:<index>
  <<(<field><<,]*) VALUES (<expression><<,]*)<<,]*]|
  <<SET <field> = <expression>|<sub-command><<,]*]|
  <<CONTENT {<JSON>}]
  <<RETURN <expression>] 
  <<FROM <query>]
```

- **`CONTENT`** Defines JSON data as an option to set field values.
- **`RETURN`** Defines an expression to return instead of the number of inserted records.  You can use any valid SQL expression.  The most common use-cases,
  - `@rid` Returns the Record ID of the new record.
  - `@this` Returns the entire new record.
- **`FROM`** Defines where you want to insert the result-set.  Introduced in version 1.7.

**Examples**:

- Inserts a new record with the name `Jay` and surname `Miner`.

  As an example, in the SQL-92 standard, such as with a Relational database, you might use:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Profile (name, surname) 
            VALUES ('Jay', 'Miner')</code>
  </pre>

  Alternatively, in the ArcadeDB abbreviated syntax, the query would be written as,

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Profile SET name = 'Jay', surname = 'Miner'</code>
  </pre>

  In JSON content syntax, it would be written as this,

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Profile CONTENT {"name": "Jay", "surname": "Miner"}</code>
  </pre>

- Insert a new record of the type `Profile`, but in a different bucket from the default.  

  In SQL-92 syntax:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Profile BUCKET profile_recent (name, surname) VALUES 
            ('Jay', 'Miner')</code>
  </pre>

  Alternative, in the ArcadeDB abbreviated syntax:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Profile BUCKET profile_recent SET name = 'Jay', 
            surname = 'Miner'</code>
  </pre>

- Insert several records at the same time:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Profile(name, surname) VALUES ('Jay', 'Miner'), 
            ('Frank', 'Hermier'), ('Emily', 'Sout')</code>
  </pre>

- Insert a new record, adding a relationship.

  In SQL-93 syntax:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Employee (name, boss) VALUES ('jack', #11:09)</code>
  </pre>

  In the ArcadeDB abbreviated syntax:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Employee SET name = 'jack', boss = #11:99</code>
  </pre>

- Insert a new record, add a collection of relationships.

  In SQL-93 syntax:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Profile (name, friends) VALUES ('Luca', <<#10:3, #10:4])</code>
  </pre>

  In the ArcadeDB abbreviated syntax:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Profiles SET name = 'Luca', friends = <<#10:3, #10:4]</code>
  </pre>

- Inserts using <<`SELECT`,SQL-Query>> sub-queries

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Diver SET name = 'Luca', buddy = (SELECT FROM Diver 
            WHERE name = 'Marko')</code>
  </pre>

- Inserts using <<`INSERT`,SQL-Insert>> sub-queries:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Diver SET name = 'Luca', buddy = (INSERT INTO Diver 
            SET name = 'Marko')</code>
  </pre>

- Inserting into a different bucket:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO BUCKET:asiaemployee (name) VALUES ('Matthew')</code>
  </pre>

  However, note that the document has no assigned type.  To create a document of a certain type, but in a different bucket than the default, instead use:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO BUCKET:asiaemployee (@type, content) VALUES 
            ('Employee', 'Matthew')</code>
  </pre>

  That inserts the document of the type `Employee` into the bucket `asiaemployee`.

- Insert a new record, adding it as an embedded document:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO Profile (name, address) VALUES ('Luca', { "@type": "d", 
            "street": "Melrose Avenue", "@version": 0 })</code>
  </pre>

- Insert from a query.

  To copy records from another type, use:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO GermanyClient FROM SELECT FROM Client WHERE 
            country = 'Germany'</code>
  </pre>

  This inserts all the records from the type `Client` where the country is Germany, in the type `GermanyClient`.

  To copy records from one type into another, while adding a field:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">INSERT INTO GermanyClient FROM SELECT *, true AS copied FROM Client 
            WHERE country = 'Germany'</code>
  </pre>

  This inserts all records from the type `Client` where the country is Germany into the type `GermanClient`, with the addition field `copied` to the value `true`.

For more information on SQL, see <<SQL Commands,SQL-Commands>>.
