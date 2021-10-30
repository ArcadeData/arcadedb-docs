
[discrete]
### Functions
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Functions.md" float=right]

SQL Functions are all the functions bundled with OrientDB SQL engine. Look also to [SQL Methods](SQL-Methods.md).

SQL Functions can work in 2 ways based on the fact that they can receive one or more parameters:

[discrete]
#### Aggregated mode

When only one parameter is passed, the function aggregates the result in only one record. The classic example is the `sum()` function:
```sql
SELECT SUM(salary) FROM employee
```
This will always return one record: the sum of salary fields across every employee record.

[discrete]
#### Inline mode

When two or more parameters are passed:
```sql
SELECT SUM(salary, extra, benefits) AS total FROM employee
```
This will return the sum of the field "salary", "extra" and "benefits" as "total".

In case you need to use a function inline, when you only have one parameter, then add "null" as the second parameter:

```sql
SELECT first( out('friends').name, null ) as firstFriend FROM Profiles
```
In the above example, the `first()` function doesn't aggregate everything in only one record, but rather returns one record per `Profile`, where the `firstFriend` is the first item of the collection received as the parameter.

[discrete]
#### Function Reference

[discrete]
##### out()

Get the adjacent outgoing vertices starting from the current record as Vertex.

Syntax: ```out([<label-1>][,<label-n>]*)```

**Examples**

Get all the outgoing vertices from all the Vehicle vertices:
```sql
SELECT out() FROM V
```

Get all the incoming vertices connected with edges with label (class) "Eats" and "Favorited" from all the Restaurant vertices in Rome:

```sql
SELECT out('Eats','Favorited') FROM Restaurant WHERE city = 'Rome'
```
---
[discrete]
##### in()

Get the adjacent incoming vertices starting from the current record as Vertex.

Syntax:
```
in([<label-1>][,<label-n>]*)
```

**Examples**

Get all the incoming vertices from all the V vertices:

```sql
SELECT in() FROM V
```

Get all the incoming vertices connected with edges with label (class) "Friend" and "Brother":
```sql
SELECT in('Friend','Brother') FROM V
```
---
[discrete]
##### both()

Get the adjacent outgoing and incoming vertices starting from the current record as Vertex.

Syntax:
```
both([<label1>][,<label-n>]*)
```

**Examples**

Get all the incoming and outgoing vertices from vertex with rid #13:33:

```sql
SELECT both() FROM #13:33
```

Get all the incoming and outgoing vertices connected by edges with label (class) "Friend" and "Brother":

```sql
SELECT both('Friend','Brother') FROM V
```
---
[discrete]
##### outE()

Get the adjacent outgoing edges starting from the current record as Vertex.

Syntax:

```
outE([<label1>][,<label-n>]*)
```

**Examples**

Get all the outgoing edges from all the vertices:
```sql
SELECT outE() FROM V
```

Get all the outgoing edges of type "Eats" from all the SocialNetworkProfile vertices:
```sql
SELECT outE('Eats') FROM SocialNetworkProfile
```
---
[discrete]
##### inE()

Get the adjacent incoming edges starting from the current record as Vertex.

Syntax:
```
inE([<label1>][,<label-n>]*)
```

**Examples**

Get all the incoming edges from all the vertices:

```sql
SELECT inE() FROM V
```

Get all the incoming edges of type "Eats" from the Restaurant 'Bella Napoli':
```sql
SELECT inE('Eats') FROM Restaurant WHERE name = 'Bella Napoli'
```
---
[discrete]
##### bothE()

Get the adjacent outgoing and incoming edges starting from the current record as Vertex.

Syntax: ```bothE([<label1>][,<label-n>]*)```

**Examples**

Get both incoming and outgoing edges from all the vertices:
```sql
SELECT bothE() FROM V
```

Get all the incoming and outgoing edges of type "Friend" from the Profiles with nickname 'Jay'

```sql
SELECT bothE('Friend') FROM Profile WHERE nickname = 'Jay'
```

---
[discrete]
##### bothV()

Get the adjacent outgoing and incoming vertices starting from the current record as Edge.

Syntax: ```bothV()```

**Examples**

Get both incoming and outgoing vertices from all the edges:
```sql
SELECT bothV() FROM E
```

[discrete]
##### outV()

Get outgoing vertices starting from the current record as Edge.

Syntax:
```
outV()
```

**Examples**

Get outgoing vertices from all edges
```sql
SELECT outV() FROM E
```

[discrete]
##### inV()

Get incoming vertices starting from the current record as Edge.

Syntax:
```
inV()
```

**Examples**

Get incoming vertices from all edges
```sql
SELECT inV() FROM E
```

[discrete]
##### eval()

Syntax: ```eval('<expression>')```

Evaluates the expression between quotes (or double quotes).

**Examples**

```sql
SELECT eval('price * 120 / 100 - discount') AS finalPrice FROM Order
```

[discrete]
##### coalesce()

Returns the first field/value not null parameter. If no field/value is not null, returns null.

Syntax:
```
coalesce(<field|value> [, <field-n|value-n>]*)
```

**Examples**

```sql
SELECT coalesce(amount, amount2, amount3) FROM Account
```

[discrete]
##### if()

Syntax:
```
if(<expression>, <result-if-true>, <result-if-false>)
```

Evaluates a condition (first parameters) and returns the second parameter if the condition is true, and the third parameter otherwise.

**Examples**:
```
SELECT if(eval("name = 'John'"), "My name is John", "My name is not John") FROM Person
```


[discrete]
##### ifnull()

Returns the passed field/value (or optional parameter *return_value_if_not_null*). If field/value is not null, otherwise it returns *return_value_if_null*.

Syntax:
```java
ifnull( <field/value>, <return_value_if_null>)
```

**Examples**

```sql
SELECT ifnull(salary, 0) FROM Account
```

---
[discrete]
##### expand()

This function has two meanings:

- When used on a collection field, it unwinds the collection in the field <field> and use it as result.
- When used on a link (RID) field, it expands the document pointed by that link.

Syntax: ```expand(<field>)```

Since version 2.1 the preferred operator to unwind collections is [UNWIND](SQL-Query.md#unwinding). Expand usage for this use case will probably be deprecated in next releases

**Examples**

on collectinos:
```sql
SELECT EXPAND( addresses ) FROM Account. 
```

on RIDs
```sql
SELECT EXPAND( addresses ) FROM Account. 
```
This replaces the flatten() now deprecated

---
[discrete]
##### flatten()

> Deprecated, use the EXPAND() instead.

Extracts the collection in the field <field> and use it as result.

Syntax:
```
flatten(<field>)
```

**Examples**

```sql
SELECT flatten( addresses ) FROM Account
```
---
[discrete]
##### first()

Retrieves only the first item of multi-value fields (arrays, collections and maps). For non multi-value types just returns the value.

Syntax: ```first(<field>)```

**Examples**

```sql
select first( addresses ) from Account
```
---
[discrete]
##### last()

Retrieves only the last item of multi-value fields (arrays, collections and maps). For non multi-value types just returns the value.

Syntax: ```last(<field>)```

**Examples**

```sql
SELECT last( addresses ) FROM Account
```
---
[discrete]
##### count()

Counts the records that match the query condition. If \* is not used as a field, then the record will be counted only if the field content is not null.

Syntax: ```count(<field>)```

**Examples**

```sql
SELECT COUNT(*) FROM Account
```
---
[discrete]
##### min()

Returns the minimum value. If invoked with more than one parameter, the function doesn't aggregate but returns the minimum value between all the arguments.

Syntax: ```min(<field> [, <field-n>]* )```

**Examples**

Returns the minimum salary of all the Account records:
```sql
SELECT min(salary) FROM Account
```
Returns the minimum value between 'salary1', 'salary2' and 'salary3' fields.
```sql
SELECT min(salary1, salary2, salary3) FROM Account
```
---
[discrete]
##### max()

Returns the maximum value. If invoked with more than one parameter, the function doesn't aggregate, but returns the maximum value between all the arguments.

Syntax: ```max(<field> [, <field-n>]* )```

**Examples**

Returns the maximum salary of all the Account records:
```sql
SELECT max(salary) FROM Account.
```

Returns the maximum value between 'salary1', 'salary2' and 'salary3' fields.
```sql
SELECT max(salary1, salary2, salary3) FROM Account
```

---
[discrete]
##### abs()

Returns the absolute value. It works with Integer, Long, Short, Double, Float, BigInteger, BigDecimal, null.

Syntax: ```abs(<field>)```

**Examples**

```sql
SELECT abs(score) FROM Account
SELECT abs(-2332) FROM Account
SELECT abs(999) FROM Account
```

---
[discrete]
##### avg()

Returns the average value.

Syntax: ```avg(<field>)```

**Examples**

```sql
SELECT avg(salary) FROM Account
```

---
[discrete]
##### sum()

Syntax: ```sum(<field>)```

Returns the sum of all the values returned.

**Examples**

```sql
SELECT sum(salary) FROM Account
```
---
[discrete]
##### date()

Returns a date formatting a string. &lt;date-as-string&gt; is the date in string format, and &lt;format&gt; is the date format following these [rules](http://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html). If no format is specified, then the default database format is used. To know more about it, look at [Managing Dates](../general/Managing-Dates.md).

Syntax: ```date( <date-as-string> [<format>] [,<timezone>] )```

**Examples**

```sql
SELECT FROM Account WHERE created <= date('2012-07-02', 'yyyy-MM-dd')
```
---
[discrete]
##### sysdate()

Returns the current date time. If executed with no parameters, it returns a Date object, otherwise a string with the requested format/timezone. To know more about it, look at [Managing Dates](../general/Managing-Dates.md).

Syntax: ```sysdate( [<format>] [,<timezone>] )```

**Examples**

```sql
SELECT sysdate('dd-MM-yyyy') FROM Account
```
---
[discrete]
##### format()

Formats a value using the [String.format()](http://download.oracle.com/javase/1.5.0/docs/api/java/lang/String.html) conventions. Look [here for more information](http://download.oracle.com/javase/1.5.0/docs/api/java/util/Formatter.html#syntax).

Syntax: ```format( <format> [,<arg1> ](,<arg-n>]*.md)```

**Examples**

```sql
SELECT format("%d - Mr. %s %s (%s)", id, name, surname, address) FROM Account
```
---


[discrete]
##### #decimal()

Converts a number or a String in an absolute precision, decimal number.

Syntax: ```decimal( <number> | <string> )```

**Examples**

```sql
SELECT decimal('99.999999999999999999') FROM Account
```
---


[discrete]
##### astar()

A*'s algorithm describes how to find the cheapest path from one node to another node in a directed weighted graph with husrestic function.

The first parameter is source record. The second parameter is destination record. The third parameter is a name of property that
represents 'weight' and fourth represnts the map of options.

If property is not defined in edge or is null, distance between vertexes are 0 .

Syntax: ```astar(<sourceVertex>, <destinationVertex>, <weightEdgeFieldName>, [<options>]) ```

options:
```
{
  direction:"OUT", //the edge direction (OUT, IN, BOTH)
  edgeTypeNames:[],  
  vertexAxisNames:[], 
  parallel : false, 
  tieBreaker:true,
  maxDepth:99999,
  dFactor:1.0,
  customHeuristicFormula:'custom_Function_Name_here'  // (MANHATAN, MAXAXIS, DIAGONAL, EUCLIDEAN, EUCLIDEANNOSQR, CUSTOM)
}
```
**Examples**

```sql
SELECT astar($current, #8:10, 'weight') FROM V
```
---
[discrete]
##### dijkstra()

Returns the cheapest path between two vertices using the [http://en.wikipedia.org/wiki/Dijkstra's_algorithm Dijkstra algorithm] where the **weightEdgeFieldName** parameter is the field containing the weight. Direction can be OUT (default), IN or BOTH.

Syntax: ```dijkstra(<sourceVertex>, <destinationVertex>, <weightEdgeFieldName> [, <direction>])```

**Examples**

```sql
SELECT dijkstra($current, #8:10, 'weight') FROM V
```
---
[discrete]
##### shortestPath()

Returns the shortest path between two vertices. Direction can be OUT (default), IN or BOTH.

Syntax: ```shortestPath( <sourceVertex>, <destinationVertex> [, <direction> [, <edgeClassName> [, <additionalParams>]]])```

Where:
- `sourceVertex` is the source vertex where to start the path
- `destinationVertex` is the destination vertex where the path ends
- `direction`, optional, is the direction of traversing. By default is "BOTH" (in+out). Supported values are "BOTH" (incoming and outgoing), "OUT" (outgoing) and "IN" (incoming)
- `edgeClassName`, optional, is the edge class to traverse. By default all edges are crossed. Since 2.0.9 and 2.1-rc2. This can also be a list of edge class names (eg. `["edgeType1", "edgeType2"]`)
- `additionalParams` (since v 2.1.12), optional, here you can pass a map of additional parametes (Map<String, Object> in Java, JSON from SQL). Currently allowed parameters are
    - 'maxDepth': integer, maximum depth for paths (ignore path longer that 'maxDepth')

**Examples** on finding the shortest path between vertices #8:32 and #8:10

```sql
SELECT shortestPath(#8:32, #8:10)
```

**Examples** on finding the shortest path between vertices #8:32 and #8:10 only crossing outgoing edges

```sql
SELECT shortestPath(#8:32, #8:10, 'OUT')
```

**Examples** on finding the shortest path between vertices #8:32 and #8:10 only crossing incoming edges of type 'Friend'
```sql
SELECT shortestPath(#8:32, #8:10, 'IN', 'Friend')
```

**Examples** on finding the shortest path between vertices #8:32 and #8:10 only crossing incoming edges of type 'Friend' or 'Colleague'
```sql
SELECT shortestPath(#8:32, #8:10, 'IN', ['Friend', 'Colleague'])
```

**Examples** on finding the shortest path between vertices #8:32 and #8:10, long at most five hops

```sql
SELECT shortestPath(#8:32, #8:10, null, null, {"maxDepth": 5})
```


---
[discrete]
##### distance()

Syntax: ```distance( <x-field>, <y-field>, <x-value>, <y-value> )```

Returns the distance between two points in the globe using the Haversine algorithm. Coordinates must be as degrees.

**Examples**

```sql
SELECT FROM POI WHERE distance(x, y, 52.20472, 0.14056 ) <= 30
```
---
[discrete]
##### distinct()

Syntax: ```distinct(<field>)```

Retrieves only unique data entries depending on the field you have specified as argument. The main difference compared to standard SQL DISTINCT is that with OrientDB, a function with parenthesis and only one field can be specified.

**Examples**

```sql
SELECT distinct(name) FROM City
```
---
[discrete]
##### unionall()

Syntax: ```unionall(<field> [,<field-n>]*)```

Works as aggregate or inline. If only one argument is passed then aggregates, otherwise executes and returns a UNION of all the collections received as parameters. Also works with no collection values.

**Examples**

```sql
SELECT unionall(friends) FROM profile
```

```sql
select unionall(inEdges, outEdges) from OGraphVertex where label = 'test'
```
---
[discrete]
##### intersect()

Syntax: ```intersect(<field> [,<field-n>]*)```

Works as aggregate or inline. If only one argument is passed then it aggregates, otherwise executes and returns the INTERSECTION of the collections received as parameters.

**Examples**

```sql
SELECT intersect(friends) FROM profile WHERE jobTitle = 'programmer'
```

```sql
SELECT intersect(inEdges, outEdges) FROM OGraphVertex
```
---
[discrete]
##### difference()

Syntax: ```difference(<field> [,<field-n>]*)```

Works as aggregate or inline. If only one argument is passed then it aggregates, otherwise it executes and returns the DIFFERENCE between the collections received as parameters.

**Examples**

```sql
SELECT difference(tags) FROM book
```

```sql
SELECT difference(inEdges, outEdges) FROM OGraphVertex
```
---

[discrete]
##### symmetricDifference()

Syntax: ```symmetricDifference(<field> [,<field-n>]*)```

Works as aggregate or inline. If only one argument is passed then it aggregates, otherwise executes and returns the SYMMETRIC DIFFERENCE between the collections received as parameters.

**Examples**

```sql
SELECT difference(tags) FROM book
```

```sql
SELECT difference(inEdges, outEdges) FROM OGraphVertex
```

---

[discrete]
##### set()

Adds a value to a set. The first time the set is created. If ```<value>``` is a collection, then is merged with the set, otherwise ```<value>``` is added to the set.

Syntax: ```set(<field>)```

**Examples**

```sql
SELECT name, set(roles.name) AS roles FROM OUser
```
---
[discrete]
##### list()

Adds a value to a list. The first time the list is created. If ```<value>``` is a collection, then is merged with the list, otherwise ```<value>``` is added to the list.

Syntax: ```list(<field>)```

**Examples**

```sql
SELECT name, list(roles.name) AS roles FROM OUser
```
---
[discrete]
##### map()

Adds a value to a map. The first time the map is created. If ```<value>``` is a map, then is merged with the map, otherwise the pair ```<key>``` and ```<value>``` is added to the map as new entry.

Syntax: ```map(<key>, <value>)```

**Examples**

```sql
SELECT map(name, roles.name) FROM OUser
```
---
[discrete]
##### traversedElement()

Returns the traversed element(s) in Traverse commands.

Syntax: ```traversedElement(<index> [,<items>])```

Where:
- ```<index>``` is the starting item to retrieve. Value >= 0 means absolute position in the traversed stack. 0 means the first record. Negative values are counted from the end: -1 means last one, -2 means the record before last one, etc.
- ```<items>```, optional, by default is 1. If >1 a collection of items is returned

**Examples**

Returns last traversed item of TRAVERSE command:
```sql
SELECT traversedElement(-1) FROM ( TRAVERSE out() FROM #34:3232 WHILE $depth <= 10 )
```

Returns last 3 traversed items of TRAVERSE command:
```sql
SELECT traversedElement(-1, 3) FROM ( TRAVERSE out() FROM #34:3232 WHILE $depth <= 10 )
```
---
[discrete]
##### traversedEdge()

Returns the traversed edge(s) in Traverse commands.

Syntax: ```traversedEdge(<index> [,<items>])```

Where:
- ```<index>``` is the starting edge to retrieve. Value >= 0 means absolute position in the traversed stack. 0 means the first record. Negative values are counted from the end: -1 means last one, -2 means the edge before last one, etc.
- ```<items>```, optional, by default is 1. If >1 a collection of edges is returned

**Examples**

Returns last traversed edge(s) of TRAVERSE command:
```sql
SELECT traversedEdge(-1) FROM ( TRAVERSE outE(), inV() FROM #34:3232 WHILE $depth <= 10 )
```

Returns last 3 traversed edge(s) of TRAVERSE command:
```sql
SELECT traversedEdge(-1, 3) FROM ( TRAVERSE outE(), inV() FROM #34:3232 WHILE $depth <= 10 )
```
---
[discrete]
##### traversedVertex()

Returns the traversed vertex(es) in Traverse commands.

Syntax: ```traversedVertex(<index> [,<items>])```

Where:
- ```<index>``` is the starting vertex to retrieve. Value >= 0 means absolute position in the traversed stack. 0 means the first vertex. Negative values are counted from the end: -1 means last one, -2 means the vertex before last one, etc.
- ```<items>```, optional, by default is 1. If >1 a collection of vertices is returned

**Examples**

Returns last traversed vertex of TRAVERSE command:
```sql
SELECT traversedVertex(-1) FROM ( TRAVERSE out() FROM #34:3232 WHILE $depth <= 10 )
```

Returns last 3 traversed vertices of TRAVERSE command:
```sql
SELECT traversedVertex(-1, 3) FROM ( TRAVERSE out() FROM #34:3232 WHILE $depth <= 10 )
```
---
[discrete]
##### mode()

Returns the values that occur with the greatest frequency. Nulls are ignored in the calculation.

Syntax: ```mode(<field>)```

**Examples**

```sql
SELECT mode(salary) FROM Account
```
---
[discrete]
##### median()

Returns the middle value or an interpolated value that represent the middle value after the values are sorted. Nulls are ignored in the calculation.

Syntax: ```median(<field>)```

**Examples**

```sql
select median(salary) from Account
```
---
[discrete]
##### percentile()

Returns the nth percentiles (the values that cut off the first n percent of the field values when it is sorted in ascending order). Nulls are ignored in the calculation.

Syntax: ```percentile(<field> [, <quantile-n>]*)```

The quantiles have to be in the range 0-1

**Examples**s

```sql
SELECT percentile(salary, 0.95) FROM Account
SELECT percentile(salary, 0.25, 0.75) AS IQR FROM Account
```
---
[discrete]
##### variance()

Returns the middle variance: the average of the squared differences from the mean. Nulls are ignored in the calculation.

Syntax: ```variance(<field>)```

**Examples**

```sql
SELECT variance(salary) FROM Account
```
---
[discrete]
##### stddev()

Returns the standard deviation: the measure of how spread out values are. Nulls are ignored in the calculation.

Syntax: ```stddev(<field>)```

**Examples**

```sql
SELECT stddev(salary) FROM Account
```
---
[discrete]
##### uuid()

Generates a UUID as a 128-bits value using the Leach-Salz variant. For more information look at: http://docs.oracle.com/javase/6/docs/api/java/util/UUID.html.

Syntax: ```uuid()```

**Examples**

Insert a new record with an automatic generated id:

```sql
INSERT INTO Account SET id = UUID()
```
---
[discrete]
##### strcmpci()

Compares two string ignoring case. Return value is -1 if first string ignoring case is less than second, 0 if strings ignoring case are equals, 1 if second string ignoring case is less than first one. Before comparison both strings are transformed to lowercase and then compared.

Syntax: ```strcmpci(<first_string>, <second_string>)```

**Examples**

Select all records where state name ignoring case is equal to "washington"

```sql
SELECT * from State where strcmpci("washington", name) = 0
```

---

[discrete]
## Custom functions

The SQL engine can be extended with custom functions written with a Scripting language or via Java.

[discrete]
##### Database's function

Look at the [Functions](../admin/Functions.md) page.

[discrete]
##### Custom functions in Java

Before to use them in your queries you need to register:

```java
// REGISTER 'BIGGER' FUNCTION WITH FIXED 2 PARAMETERS (MIN/MAX=2)
SQLEngine.getInstance().registerFunction("bigger",
                                          new SQLFunctionAbstract("bigger", 2, 2) {
  public String getSyntax() {
    return "bigger(<first>, <second>)";
  }

  public Object execute(Object[] iParameters) {
    if (iParameters[0] == null || iParameters[1] == null)
      // CHECK BOTH EXPECTED PARAMETERS
      return null;

    if (!(iParameters[0] instanceof Number) || !(iParameters[1] instanceof Number))
      // EXCLUDE IT FROM THE RESULT SET
      return null;

    // USE DOUBLE TO AVOID LOSS OF PRECISION
    final double v1 = ((Number) iParameters[0]).doubleValue();
    final double v2 = ((Number) iParameters[1]).doubleValue();

    return Math.max(v1, v2);
  }

  public boolean aggregateResults() {
    return false;
  }
});
```

Now you can execute it:

```java
Resultset result = database.command("sql", "SELECT FROM Account WHERE bigger( salary, 10 ) > 10");
```

