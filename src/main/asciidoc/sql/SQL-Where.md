[[SQL-Filtering]]
### SQL - Filtering

The Where condition is shared among many SQL commands.

#### Syntax

`<<<item>] <operator> <item>`

#### Items

And `item` can be:

[%header,cols=3]
|===
|**What**|**Description**|**Example**
|field|Document field|where *price* > 1000000
|field&lt;indexes&gt;|Document field part. To know more about field part look at the full syntax: <<properties,Document-API-Property>>|where tags<<name='Hi'] or tags<<0-3] IN ('Hello') and employees IS NOT NULL
|record attribute|Record attribute name with @ as prefix|where *@type* = 'Profile'
|column|The number of the column. Useful in Column Database|where *column(1)* > 300
|any()|Represents any field of the Document. The condition is true if ANY of the fields matches the condition|where *any()* like 'L%'
|all()|Represents all the fields of the Document. The condition is true if ALL the fields match the condition|where *all()* is null
|<<functions,SQL-Functions>>|Any <<function,SQL-Functions>> between the defined ones|where distance(x, y, 52.20472, 0.14056 ) <= 30
|<<$variable,SQL-Where.md#variables)|Context variable prefixed with $|where $depth <= 3
|===


##### Record attributes


[%header,cols=3]
|===
|Name|Description|Example
|@this|returns the record it self|select **@this.toJSON()** from Account
|@rid|returns the <<Record ID,../datamodeling/Concepts.md#record-id) in the form &lt;bucket:position&gt;. It's null for embedded records. *NOTE: using @rid in where condition slow down queries. Much better to use the <<Record ID,../datamodeling/Concepts.md#record-id) as target. Example: change this: select from Profile where @rid = #10:44 with this: select from #10:44 *|**@rid** = #11:0
|@size|returns the record size in bytes|**@size** > 1024
|@type|returns the record type between: 'document', 'column', 'flat', 'bytes'|**@type** = 'flat'
|===

[[SQL-Filtering-Operators]]
#### Operators

##### Conditional Operators

[%header,cols=4]
|===
|Apply to|Operator|Description|Example
|any|=|Equals to|name **=** 'Luke'
|string|like|Similar to equals, but allow the wildcard '%' that means 'any'|name **like** 'Luk%'
|any|<|Less than|age **<** 40
|any|<=|Less than or equal to|age **<=** 40
|any|>|Greater than|age **>** 40
|any|>=|Greater than or equal to|age **>=** 40
|any|<>|Not equals (same of !=)|age **<>** 40
|any|BETWEEN|The value is between a range. It's equivalent to &lt;field&gt; &gt;= &lt;from-value&gt; AND &lt;field&gt; &lt;= &lt;to-value&gt;|price BETWEEN 10 and 30
|any|IS|Used to test if a value is NULL|children **is** null
|record, string (as type name)|INSTANCEOF|Used to check if the record extends a type|@this **instanceof** 'Customer' or @type **instanceof** 'Provider'
|collection|IN|contains any of the elements listed|name **in** <<'European','Asiatic']
|collection|CONTAINS|true if the collection contains at least one element that satisfy the next condition. Condition can be a single item: in this case the behaviour is like the IN operator|children **contains** (name = 'Luke') - map.values() **contains** (name = 'Luke')
|collection|CONTAINSALL|true if all the elements of the collection satisfy the next condition|children *containsAll* (name = 'Luke')
|collection|CONTAINSANY|true if any the elements of the collection satisfy the next condition|children *containsAny* (name = 'Luke')
|map|CONTAINSKEY|true if the map contains at least one key equals to the requested. You can also use map.keys() CONTAINS in place of it|connections *containsKey* 'Luke'
|map|CONTAINSVALUE|true if the map contains at least one value equals to the requested. You can also use map.values() CONTAINS in place of it|connections *containsValue* 10:3
|string|CONTAINSTEXT| When used against an indexed field, a lookup in the index will be performed with the text specified as key. When there is no index a simple Java indexOf will be performed. So the result set could be different if you have an index or not on that field |text *containsText* 'jay'
|string|MATCHES|Matches the string using a http://www.regular-expressions.info/|Regular Expression|text matches '\b<<A-Z0-9.%+-]+@<<A-Z0-9.-]+\.<<A-Z]{2,4}\b'
|any|TRAVERSE<<(&lt;minDepth&gt; <<,&lt;maxDepth&gt; <<,&lt;fields&gt;]]|*This function was born before the SQL Traverse statement and today it's pretty limited. Look at <<Traversing graphs,../java/Java-Traverse>> to know more about traversing in better ways.* <br>true if traversing the declared field(s) at the level from &lt;minDepth&gt; to &lt;maxDepth&gt; matches the condition. A minDepth = 0 means the root node, maxDepth = -1 means no limit: traverse all the graph recursively. If &lt;minDepth&gt; and &lt;maxDepth&gt; are not used, then (0, -1) will be taken. If &lt;fields&gt; is not passed, than any() will be used.|select from profile where any() **traverse(0,7,'followers,followings')** ( address.city.name = 'Rome' )
|===

##### Logical Operators

[%header,cols=3]
|===
|Operator|Description|Example
|AND|true if both the conditions are true|name = 'Luke' **and** surname like 'Sky%'
|OR|true if at least one of the condition is true|name = 'Luke' **or** surname like 'Sky%'
|NOT|true if the condition is false. NOT needs parenthesis on the right with the condition to negate|**not** ( name = 'Luke')
|===

##### Mathematics Operators


[%header,cols=4]
|===
|Apply to|Operator|Description|Example
|Numbers|+|Plus|age + 34
|Numbers|-|Minus|salary - 34
|Numbers|\*|Multiply|factor \* 1.3
|Numbers|/|Divide|total / 12
|Numbers|%|Mod|total % 3
|===

Starting from v1.4 ArcadeDB supports the `eval()` function to execute complex operations. Example:
```sql
select eval( "amount * 120 / 100 - discount" ) as finalPrice from Order
```

##### Methods

Also called "Field Operators", are <<are treated on a separate page,SQL-Methods>>.

#### Variables

ArcadeDB supports variables managed in the context of the command/query. By default some variables are created. Below the table with the available variables:


[%header,cols=3]
|===
|Name    |Description    |Command(s)
|$parent|Get the parent context from a sub-query. Example: select from V let $type = ( traverse * from $parent.$current.children )|<<SELECT,SQL-Query>> and <<TRAVERSE,SQL-Traverse>>
|$current|Current record to use in sub-queries to refer from the parent's variable|<<SELECT,SQL-Query>> and <<TRAVERSE,SQL-Traverse>>
|$depth|The current depth of nesting|<<TRAVERSE,SQL-Traverse>>
|$path|The string representation of the current path. Example:  #6:0.in.#5:0#.out. You can also display it with -> select $path from (traverse * from V)|<<TRAVERSE,SQL-Traverse>>
|$stack|The List of operation in the stack. Use it to access to the history of the traversal|<<TRAVERSE,SQL-Traverse>>|1.1.0|
|$history|The set of all the records traversed as a Set&lt;ORID&gt;|<<TRAVERSE,SQL-Traverse>>
|===


To set custom variable use the <<LET,SQL-Select-Let) keyword.
