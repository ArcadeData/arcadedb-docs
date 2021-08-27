[[SQL-Traverse]]
### SQL - `TRAVERSE` 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Traverse.md" float=right]

Retrieves connected records crossing relationships.  This works with both the Document and Graph API's, meaning that you can traverse relationships between say invoices and customers on a graph, without the need to model the domain using the Graph API.

NOTE: In many cases, you may find it more efficient to use <<SQL-Query,`SELECT`>>, which can result in shorter and faster queries.  For more information, see <<traverse-versus-select,`TRAVERSE` versus `SELECT`) below.

**Syntax**

```sql
TRAVERSE [<type.]field>|*|any()|all()
         [FROM <target>]
         [
           MAXDEPTH <number>
           |
           WHILE <condition> 
         ]
         [LIMIT <max-records>]
         [STRATEGY <strategy>]
```

- <<fields,`<fields>`>> Defines the fields you want to traverse.
- <<target,`<target>`>> Defines the target you want to traverse.  This can be a type, one or more buckets, a single Record ID, set of Record ID's, or a sub-query.
- **`MAXDEPTH`** Defines the maximum depth of the traversal.  `0` indicates that you only want to traverse the root node.  Negative values are invalid.
- **`WHILE`** Defines the condition for continuing the traversal while it is true.  
- **`LIMIT`** Defines the maximum number of results the command can return.
- <<traversal-strategies,`STRATEGY`>> Defines strategy for traversing the graph.

NOTE: The use of the <<SQL-Where,`WHERE`>> clause has been deprecated for this command.

NOTE: There is a difference between `MAXDEPTH N` and `WHILE DEPTH <= N`: the `MAXDEPTH` will evaluate exactly N levels, while the `WHILE` will evaluate N+1 levels and will discard the N+1th, so the `MAXDEPTH` in general has better performance.


**Examples**

In a social network-like domain, a user profile is connected to friend through links.  The following examples consider common operations on a user with the record ID `#10:1234`.

- Traverse all fields in the root record:

```sql
ArcadeDB> TRAVERSE * FROM #10:1234
```

- Specify fields and depth up to the third level, using the <<Traversal-Strategies,`BREADTH_FIRST`) strategy:

```
ArcadeDB> TRAVERSE out("Friend") FROM #10:1234 MAXDEPTH 3 
            STRATEGY BREADTH_FIRST
```

- Execute the same command, this time filtering for a minimum depth to exclude the first target vertex:

```sql
ArcadeDB> SELECT FROM (TRAVERSE out("Friend") FROM #10:1234 MAXDEPTH 3) 
            WHERE $depth >= 1
```

NOTE: You can also define the maximum depth in the <<SQL-Query,`SELECT`>> command, but it's much more efficient to set it at the inner <<SQL-Traverse,`TRAVERSE`>> statement because the returning record sets are already filtered by depth.

- Combine traversal with <<SQL-Query,`SELECT`>> command to filter the result-set.  Repeat the above example, filtering for users in Rome:

```sql
ArcadeDB> SELECT FROM (TRAVERSE out("Friend") FROM #10:1234 MAXDEPTH 3) 
            WHERE city = 'Rome'
```

- Extract movies of actors that have worked, at least once, in any movie produced by J.J. Abrams:

```sql
ArcadeDB> SELECT FROM (TRAVERSE out("Actors"), out("Movies") FROM (SELECT FROM 
            Movie WHERE producer = "J.J. Abrams") MAXDEPTH 3) WHERE 
            @type = 'Movie'
```

- Display the current path in the traversal:

```sql
ArcadeDB> SELECT $path FROM ( TRAVERSE out() FROM V MAXDEPTH 10 )
```


**Supported Variables**

**Fields**

Defines the fields that you want to traverse.  If set to `*`, `any()` or `all()` then it traverses all fields.  This can prove costly to performance and resource usage, so it is recommended that you optimize the command to only traverse the pertinent fields.

In addition to his, you can specify the fields at a type-level.  <<Inheritance,Inheritance>> is supported.  By specifying `Person.city` and the type `Customer` extends person, you also traverse fields in `Customer`.

Field names are case-sensitive, typees not.

**Target**

Targets for traversal can be:

- **`<type>`** Defines the type that you want to traverse.  
- **`BUCKET:<bucket>`** Defines the bucket you want to traverse.
- **`<record-id>`** Individual root Record ID that you want to traverse.
- **`[<record-id>,<record-id>,...]`** Set of Record ID's that you want to traverse.  This is useful when navigating graphs starting from the same root nodes.

**Context Variables**

In addition to the above, you can use the following context variables in traversals:

- **`$parent`** Gives the parent context, if any.  You may find this useful when traversing from a sub-query. 
- **`$current`** Gives the current record in the iteration.  To get the upper-level record in nested queries, you can use `$parent.$current`.
- **`$depth`** Gives the current depth of nesting.
- **`$path`** Gives a string representation of the current path.  For instance, `#5:0.out`.  You can also display it through <<SQL-Query,`SELECT`>>:

```sql
ArcadeDB> SELECT $path FROM (TRAVERSE * FROM V)
```

**Use Cases**

[[traverse-versus-select]]
**`TRAVERSE` versus `SELECT`**

When you already know traversal information, such as relationship names and depth-level, consider using <<SQL-Query,`SELECT`>> instead of <<SQL-Traverse,`TRAVERSE`>> as it is faster in some cases. 

For example, this query traverses the `follow` relationship on Twitter accounts, getting the second level of friendship:

```sql
ArcadeDB> SELECT FROM (TRAVERSE out('follow') FROM TwitterAccounts MAXDEPTH 2 )
          WHERE $depth = 2
```

But, you could also express this same query using <<SQL-Query,`SELECT`>> operation, in a way that is also shorter and faster:

```sql
ArcadeDB> SELECT out('follow').out('follow') FROM TwitterAccounts
```

**`TRAVERSE` with the Graph Model and API**

While you can use the <<SQL-Traverse,`TRAVERSE`>> command with any domain model, it provides the greatest utility with the <<Graph-Model,Graph Model>>.

This model is based on the concepts of the Vertex (or Node) as the type `V` and the Edge (or Arc, Connection, Link, etc.) as the type `E`.  If you want to traverse in a direction, you have to use the type name when declaring the traversing fields.  The supported directions are:

- **Vertex to outgoing edges**  Using `outE()` or `outE('EdgeTypeName')`.  That is, going out from a vertex and into the outgoing edges.
- **Vertex to incoming edges**  Using `inE()` or `inE('EdgeTypeName')`.  That is, going from a vertex and into the incoming edges.
- **Vertex to all edges**  Using `bothE()` or `bothE('EdgeTypeName')`.  That is, going from a vertex and into all the connected edges.
- **Edge to Vertex (end point)** Using `inV()` .  That is, going out from an edge and into a vertex.
- **Edge to Vertex (starting point)** Using `outV()` .  That is, going back from an edge and into a vertex.
- **Edge to Vertex (both sizes)** Using `bothV()` .  That is, going from an edge and into connected vertices.
- **Vertex to Vertex (outgoing edges)** Using `out()` or `out('EdgeTypeName')`. This is the same as  `outE().inV()`
- **Vertex to Vertex (incoming edges)** Using `in()` or `in('EdgeTypeName')`. This is the same as  `outE().inV()`
- **Vertex to Vertex (all directions)** Using `both()` or `both('EdgeTypeName')`. 


For instance, traversing outgoing edges on the record `#10:3434`:

```
ArcadeDB> TRAVERSE out() FROM #10:3434
```

In a domain for emails, to find all messages sent on January 1, 2012 from the user Luca, assuming that they are stored in the vertex type `User` and that the messages are contained in the vertex type `Message`.  Sent messages are stored as `out` connections on the edge type `SentMessage`:

```
ArcadeDB> SELECT FROM (TRAVERSE outE(), inV() FROM (SELECT FROM User WHERE 
          name = 'Luca') MAXDEPTH 2 AND (@type = 'Message' or 
          (@type = 'SentMessage' AND sentOn = '01/01/2012') )) WHERE 
          @type = 'Message'
```

