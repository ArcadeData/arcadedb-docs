
### SQL - `CREATE VERTEX`

Creates a new vertex in the database.

The Vertex and Edge are the main components of a Graph database.  ArcadeDB supports polymorphism on vertices.  The base type for a vertex is `V`.


**Syntax**

```sql
CREATE VERTEX [<type>] <<BUCKET <bucket>] [SET <field> = <expression>[,]*]
```

- **`<type>`** Defines the type to which the vertex belongs.
- **`<bucket>`** Defines the bucket in which it stores the vertex.
- **`<field>`** Defines the field you want to set.
- **`<expression>`** Defines the express to set for the field.

NOTE: When using a distributed database, you can create vertexes through two steps (creation and update).  Doing so can break constraints defined at the type-level for vertices.  To avoid these issues, disable constraints in the vertex type.

**Examples**

- Create a new vertex on the base type `V`:

```
ArcadeDB> CREATE VERTEX
```

- Create a new vertex type, then create a vertex in that type:

```
ArcadeDB> CREATE TYPE V1 EXTENDS V
ArcadeDB> CREATE VERTEX V1
```

- Create a new vertex within a particular bucket:

```
ArcadeDB> <code type="userinput lang-sql">CREATE VERTEX V1 BUCKET recent
```

- Create a new vertex, defining its properties:

```
ArcadeDB> CREATE VERTEX SET brand = 'fiat'
```

- Create a new vertex of the type `V1`, defining its properties:

```
ArcadeDB> CREATE VERTEX V1 SET brand = 'fiat', name = 'wow'
```

- Create a vertex using JSON content:

```
ArcadeDB> CREATE VERTEX Employee CONTENT { "name" : "Jay", "surname" : "Miner" }
```

>For more information, see:

- <<SQL-Create-Edge,`CREATE EDGE`>>
