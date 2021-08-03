
### SQL - `CREATE EDGE`

Creates a new edge in the database.

**Syntax**

```sql
CREATE EDGE <type> <<BUCKET <bucket>] <<UPSERT] FROM <rid>|(<query>)|<<<rid>]* TO <rid>|(<query>)|<<<rid>]*
                    <<SET <field> = <expression><<,]*]|CONTENT {<JSON>}
                    <<RETRY <retry> <<WAIT <pauseBetweenRetriesInMs]] <<BATCH <batch-size>]
```

- **`<type>`** Defines the type name for the edge.  Use the default edge type `E` in the event that you don't want to use sub-types.
- **`<bucket>`** Defines the bucket in which you want to store the edge.
- **`UPSERT`** (since v 3.0.1) allows to skip the creation of edges that already exist between two vertices (ie. a unique edge for a couple of vertices). This works only if the edge type has a UNIQUE index on `out, in` fields, otherwise the statement fails.
- **`JSON`** Provides JSON content to set as the record.  Use this instead of entering data field by field.
- **`RETRY`** Define the number of retries to attempt in the event of conflict, (optimistic approach).
- **`WAIT`** Defines the time to delay between retries in milliseconds.
- **`BATCH`** Defines whether it breaks the command down into smaller blocks and the size of the batches.  This helps to avoid memory issues when the number of vertices is too high.  By default, it is set to `100`.  This feature was introduced in version 2.1.3.

Edges and Vertices form the main components of a Graph database.  ArcadeDB supports polymorphism on edges.  The base type for an edge is `E`. 

Beginning with version 2.1, when no edges are created ArcadeDB throws a `OCommandExecutionException` error.  This makes it easier to integrate edge creation in transactions.  In such cases, if the source or target vertices don't exist, it rolls back the transaction.  (Prior to 2.1, no such error is thrown.)


**Examples**

- Create an edge of the type `E` between two vertices:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE EDGE FROM #10:3 TO #11:4</code>
  </pre>

- Create a new edge type and an edge of the new type:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE TYPE E1 EXTENDS E</code>
  ArcadeDB> <code type="lang-sql userinput">CREATE EDGE E1 FROM #10:3 TO #11:4</code>
  </pre>

- Create an edge in a specific bucket:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE EDGE E1 BUCKET EuropeEdges FROM #10:3 TO #11:4</code>
  </pre>

- Create an edge and define its properties:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE EDGE FROM #10:3 TO #11:4 SET brand = 'fiat'</code>
  </pre>

- Create an edge of the type `E1` and define its properties:
 
  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE EDGE E1 FROM #10:3 TO #11:4 SET brand = 'fiat', name = 'wow'</code>
  </pre>

- Create edges of the type `Watched` between all action movies in the database and the user Luca, using sub-queries:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE EDGE Watched FROM (SELECT FROM account WHERE name = 'Luca') TO 
            (SELECT FROM movies WHERE type.name = 'action')</code>
  </pre>

- Create an edge using JSON content:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">CREATE EDGE E FROM #22:33 TO #22:55 CONTENT</code> <code type='lang-json userinput'>{ "name": "Jay", 
            "surname": "Miner" }</code>
  </pre>



>For more information, see
>
>- <<`CREATE VERTEX`,SQL-Create-Vertex>>


#### Control Vertices Version Increment

Creating and deleting edges causes ArcadeDB to update versions involved in the vertices.  To avoid this behavior, use the <<Bonsai Structure,../internals/RidBag>>.

By default, ArcadeDB uses Bonsai as soon as it reaches the threshold to optimize operation.  To always use Bonsai on your database, either set this configuration on the JVM or in the `ArcadeDB-server-config.xml` configuration file.

<pre>
$ <code type="userinput lang-sh">java -DridBag.embeddedToSbtreeBonsaiThreshold=-1</code>
</pre>

Alternatively, in your Java application use the following call before opening the database:

```java
OGlobalConfiguration.RID_BAG_EMBEDDED_TO_SBTREEBONSAI_THRESHOLD.setValue(-1);
```

>For more information, see <<Concurrency on Adding Edges,../general/Concurrency.md#concurrency-when-adding-edges).

| !<<NOTE,../images/warning.png) | When running a distributed database, edge creation can sometimes be done in two steps, (that is, create and update).  This can break some constraints defined in the Edge at the type-level.  To avoid such problems, disable the constraints in the Edge type.  Bear in mind that in distributed mode SB Tree index algorithm is not supported.  You must set `ridBag.embeddedToSbtreeBonsaiThreashold=Integer.Max\_VALUE` to avoid replication errrors|
|----|----|



#### History

##### 2.0

- Disables <<Lightweight Edges,../java/Lightweight-Edges>> in new databases by default.  This command now creates a regular edge.

##### 1.4

- Command uses the Blueprints API.  If you are in Java using the `OGraphDatabase` API, you may experience some differences in how ArcadeDB manages edges.

  >To force the command to work with the older API, change the GraphDB settings, as described in <<Graph backwards compatibility,SQL-Alter-Database>>.

##### 1.2

- Implements support for query and collection of Record ID's in the `FROM...TO` clause.

##### 1.1

- Initial version.
