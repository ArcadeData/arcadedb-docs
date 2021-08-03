
### SQL - `CREATE VERTEX`

Creates a new vertex in the database.

The Vertex and Edge are the main components of a Graph database.  ArcadeDB supports polymorphism on vertices.  The base type for a vertex is `V`.


**Syntax**

```sql
CREATE VERTEX <<<type>] <<BUCKET <bucket>] <<SET <field> = <expression><<,]*]
```

- **`<type>`** Defines the type to which the vertex belongs.
- **`<bucket>`** Defines the bucket in which it stores the vertex.
- **`<field>`** Defines the field you want to set.
- **`<expression>`** Defines the express to set for the field.

|----|----|
| !<<NOTE,../images/warning.png) | **NOTE**: When using a distributed database, you can create vertexes through two steps (creation and update).  Doing so can break constraints defined at the type-level for vertices.  To avoid these issues, disable constraints in the vertex type.|

**Examples**

- Create a new vertex on the base type `V`:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE VERTEX</code>
  </pre>

- Create a new vertex type, then create a vertex in that type:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE TYPE V1 EXTENDS V</code>
  ArcadeDB> <code type="lang-sql userinput">CREATE VERTEX V1</code>
  </pre>

- Create a new vertex within a particular bucket:

  <pre>
  ArcadeDB> <code type="userinput lang-sql">CREATE VERTEX V1 BUCKET recent</code>
  </pre>

- Create a new vertex, defining its properties:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE VERTEX SET brand = 'fiat'</code>
  </pre>

- Create a new vertex of the type `V1`, defining its properties:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE VERTEX V1 SET brand = 'fiat', name = 'wow'</code>
  </pre>

- Create a vertex using JSON content:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE VERTEX Employee CONTENT { "name" : "Jay", "surname" : "Miner" }</code>
  </pre>

>For more information, see
>
>- <<`CREATE EDGE`,SQL-Create-Edge>>
>- <<SQL Commands,SQL-Commands>>

#### History

##### 1.4

- Command begins using the Blueprints API.  When using Java with the OGraphDatabase API, you may experience unexpected results in how it manages edges.

  To force the command to work with the older API, update the GraphDB settings, use the <<`ALTER DATABASE`,SQL-Alter-Database>> command.

##### 1.1

- Initial implementation of feature.
