[[SQL-Select]]
### SQL - `SELECT`

ArcadeDB supports the SQL language to execute queries against the database engine.  For more information, see <<operators,SQL-Where.md#operators) and <<functions,SQL-Where.md#functions).  For more information on the differences between this implementation and the SQL-92 standard, please refer to <<this,SQL-Introduction>> section.

**Syntax**:

```sql
SELECT << <Projections> ] << FROM <Target> << LET <Assignment>* ] ]
    << WHERE <Condition>* ]
    << GROUP BY <Field>* ]
    << ORDER BY <Fields>* << ASC|DESC ] * ]
    << UNWIND <Field>* ]
    << SKIP <SkipRecords> ]
    << LIMIT <MaxRecords> ]
    << FETCHPLAN <FetchPlan> ]
    << TIMEOUT <Timeout> << <STRATEGY> ]
    << PARALLEL ]
    << NOCACHE ]
```

- **<<`<Projections>`,SQL-Query.md#projections)** Indicates the data you want to extract from the query as the result-set.  Note: In ArcadeDB, this variable is optional.  In the projections you can define aliases for single fields, using the `AS` keyword; in current release aliases cannot be used in the WHERE condition, GROUP BY and ORDER BY (they will be evaluated to null)
- **`FROM`** Designates the object to query.  This can be a type, bucket, single <<Record ID,../datamodeling/Concepts.md#record-id), set of <<Record ID's,../datamodeling/Concepts.md#record-id), or (beginning in version 1.7.7) index values sorted by ascending or descending key order.
   - When querying a type, for `<target>` use the type name.
   - When querying a bucket, for `<target>` use `BUCKET:<bucket-name>` (eg. `BUCKET:person`) or `BUCKET:<bucket-id>` (eg. `BUCKET:12`).  This causes the query to execute only on records in that bucket. 
   - When querying record ID's, you can specific one or a small set of records to query.  This is useful when you need to specify a starting point in navigating graphs.
   - When querying indexes, use the following prefixes:
     - `INDEXVALUES:<index>` and `INDEXVALUESASC:<index>` sorts values into an ascending order of index keys.
     - `INDEXVALUESDESC:<index>` sorts the values into a descending order of index keys.
- **<<`WHERE`,SQL-Where>>** Designates conditions to filter the result-set.
- **<<`LET`,SQL-Query.md#let-block)** Binds context variables to use in projections, conditions or sub-queries.
- **`GROUP BY`** Designates field on which to group the result-set. 
- **`ORDER BY`** Designates the field with which to order the result-set.  Use the optional `ASC` and `DESC` operators to define the direction of the order.  The default is ascending.  Additionally, if you are using a <<projection,SQL-Query.md#projections), you need to include the `ORDER BY` field in the projection. Note that ORDER BY works only on projection fields (fields that are returned in the result set) not on LET variables.
- **<<`UNWIND`,SQL-Query.md#unwinding)** Designates the field on which to unwind the collection.  Introduced in version 2.1.
- **`SKIP`** Defines the number of records you want to skip from the start of the result-set.  You may find this useful in <<pagination,Pagination>>, when using it in conjunction with `LIMIT`.
- **`LIMIT`** Defines the maximum number of records in the result-set.  You may find this useful in <<pagination,Pagination>>, when using it in conjunction with `SKIP`. 
- **`FETCHPLAN`** Defines how you want it to fetch results.  For more information, see <<Fetching Strategy,../java/Fetching-Strategies>>.
- **`TIMEOUT`** Defines the maximum time in milliseconds for the query.  By default, queries have no timeouts.  If you don't specify a timeout strategy, it defaults to `EXCEPTION`.  These are the available timeout strategies:
  - `RETURN` Truncate the result-set, returning the data collected up to the timeout.
  - `EXCEPTION` Raises an exception.
- **`PARALLEL`** Executes the query against *x* concurrent threads, where *x* refers to the number of processors or cores found on the host operating system of the query.  You may find `PARALLEL` execution useful on long running queries or queries that involve multiple bucket.  For simple queries, using `PARALLEL` may cause a slow down due to the overhead inherent in using multiple threads.
- **`NOCACHE`** Defines whether you want to avoid using the cache.

>**NOTE**: Beginning with version 1.0 rc 7, the `RANGE` operator was removed.  To execute range queries, instead use the `BETWEEN` operator against `@RID`.  For more information, see <<Pagination,Pagination>>.


**Examples**:

- Return all records of the type `Person`, where the name starts with `Luk`:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM Person WHERE name LIKE 'Luk%'</code>
  </pre>

  Alternatively, you might also use either of these queries:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM Person WHERE name.left(3) = 'Luk'</code>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM Person WHERE name.substring(0,3) = 'Luk'</code>
  </pre>
  
- Return all records of the type `!AnimalType` where the collection `races` contains at least one entry where the first character is `e`, ignoring case:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM animaltype WHERE races CONTAINS( name.toLowerCase().subString(
            0, 1) = 'e' )</code>
  </pre>

- Return all records of type `!AnimalType` where the collection `races` contains at least one entry with names `European` or `Asiatic`:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT * FROM animaltype WHERE races CONTAINS(name in <<'European',
            'Asiatic'])</code>
  </pre>

- Return all records in the type `Profile` where any field contains the word `danger`:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM Profile WHERE ANY() LIKE '%danger%'</code>
  </pre>

- Return any record at any level that has the word `danger`:

  DEPRECATED SYNTAX
  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM Profile WHERE ANY() TRAVERSE( ANY() LIKE '%danger%' )</code>
  </pre>

- Return any record where up to the third level of connections has some field that contains the word `danger`, ignoring case:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM Profile WHERE ANY() TRAVERSE(0, 3) ( 
            ANY().toUpperCase().indexOf('danger') > -1 )</code>
  </pre>

- Return all results on type `Profile`, ordered by the field `name` in descending order:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM Profile ORDER BY name DESC</code>
  </pre>

- Return the number of records in the type `Account` per city:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT SUM(*) FROM Account GROUP BY city</code>
  </pre>

- Traverse records from a root node:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM 11:4 WHERE ANY() TRAVERSE(0,10) (address.city = 'Rome')</code>
  </pre>

- Return only a limited set of records:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM <<#10:3, #10:4, #10:5]</code>
  </pre>

- Return three fields from the type `Profile`:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT nick, followings, followers FROM Profile</code>
  </pre>

- Return the field `name` in uppercase and the field country name of the linked city of the address:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT name.toUppercase(), address.city.country.name FROM Profile</code>
  </pre>

- Return records from the type `Profile` in descending order of their creation:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT FROM Profile ORDER BY @rid DESC</code>
  </pre>
  
- Return value of `email` which is stored in a JSON field `data` (type EMBEDDED)  of the type `Person`, where the name starts with `Luk`:

  <pre>
  ArcadeDB> <code type="lang-sql userinput">SELECT data.email FROM Person WHERE name LIKE 'Luk%'</code>
  </pre>

  Beginning in version 1.7.7, ArcadeDB can open an inverse cursor against buckets.  This is very fast and doesn't require the typeic ordering resources, CPU and RAM.


[[SQL-Select-Projections]]
** Projections **

In the standard implementations of SQL, projections are mandatory.  In ArcadeDB, the omission of projects translates to its returning the entire record.  That is, it reads no projection as the equivalent of the `*` wildcard.

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT FROM Account</code>
</pre>

For all projections except the wildcard `*`, it creates a new temporary document, which does not include the `@rid` and `@version` fields of the original record.

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT name, age FROM Account</code>
</pre>

The naming convention for the returned document fields are:
- Field name for plain fields, like `invoice` becoming `invoice`.
- First field name for chained fields, like `invoice.customer.name` becoming `invoice`.
- Function name for functions, like `MAX(salary)` becoming `max`.

In the event that the target field exists, it uses a numeric progression.  For instance,

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT MAX(incoming), MAX(cost) FROM Balance</code>

------+------
 max  | max2
------+------
 1342 | 2478
------+------
</pre>

To override the display for the field names, use the `AS`.

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT MAX(incoming) AS max_incoming, MAX(cost) AS max_cost FROM Balance</code>

---------------+----------
 max_incoming  | max_cost
---------------+----------
 1342          | 2478
---------------+----------
</pre>

With the dollar sign `$`, you can access the context variables.  Each time you run the command, ArcadeDB accesses the context to read and write the variables.  For instance, say you want to display the path and depth levels up to the fifth of a <<`TRAVERSE`,SQL-Traverse>> on all records in the `Movie` type.

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT $path, $depth FROM ( TRAVERSE * FROM Movie WHERE $depth <= 5 )</code>
</pre>


[[SQL-Select-Let]]
** `LET` Block **

The `LET` block contains context variables to assign each time ArcadeDB evaluates a record.  It destroys these values once the query execution ends.  You can use context variables in projections, conditions, and sub-queries.

** Assigning Fields for Reuse **

ArcadeDB allows for crossing relationships.  In single queries, you need to evaluate the same branch of the nested relationship.  This is better than using a context variable that refers to the full relationship.

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT FROM Profile WHERE address.city.name LIKE '%Saint%"' AND 
          ( address.city.country.name = 'Italy' OR 
            address.city.country.name = 'France' )</code>
</pre>

Using the `LET` makes the query shorter and faster, because it traverses the relationships only once:

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT FROM Profile LET $city = address.city WHERE $city.name LIKE 
          '%Saint%"' AND ($city.country.name = 'Italy' OR $city.country.name = 'France')</code>
</pre>

In this case, it traverses the path till `address.city` only once.

** Sub-query **

The `LET` block allows you to assign a context variable to the result of a sub-query.

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT FROM Document LET $temp = ( SELECT @rid, $depth FROM (TRAVERSE 
          V.OUT, E.IN FROM $parent.current ) WHERE @type = 'Concept' AND 
          ( id = 'first concept' OR id = 'second concept' )) WHERE $temp.SIZE() > 0</code>
</pre>

** `LET` Block in Projection **

You can use context variables as part of a result-set in <<projections,#projections).  For instance, the query below displays the city name from the previous example:

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT $temp.name FROM Profile LET $temp = address.city WHERE $city.name 
          LIKE '%Saint%"' AND ( $city.country.name = 'Italy' OR 
          $city.country.name = 'France' )</code>
</pre>


** Unwinding **

Beginning with version 2.1, ArcadeDB allows unwinding of collection fields and obtaining multiple records as a result, one for each element in the collection:

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT name, OUT("Friend").name AS friendName FROM Person</code>

--------+-------------------
 name   | friendName
--------+-------------------
 'John' | <<'Mark', 'Steve']
--------+-------------------
</pre>

In the event if you want one record for each element in `friendName`, you can rewrite the query using `UNWIND`:

<pre>
ArcadeDB> <code type="lang-sql userinput">SELECT name, OUT("Friend").name AS friendName FROM Person UNWIND friendName</code>

--------+-------------
 name   | friendName
--------+-------------
 'John' | 'Mark'
 'John' | 'Steve'
--------+-------------
</pre>

>**NOTE**: For more information on other SQL commands, see <<SQL Commands,SQL-Commands>>.


** Execution planning **

For details about query execution planning, please refer to <<SQL SELECT Execution,SQL-Select-Execution>>

