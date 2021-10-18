
[discrete]
#### Methods 
image:../images/edit.png[link="https://github.com/ArcadeData/arcadedb-docs/blob/main/src/main/asciidoc/sql/SQL-Methods.md" float=right]

SQL Methods are similar to <<SQL-Functions,SQL Functions>> but they apply to values. In Object-Oriented paradigm they are called "methods", as functions related to a type. So what's the difference between a function and a method?

This is a <<SQL-Function,SQL Functions>>:
```sql
SELECT FROM sum( salary ) FROM employee
```

This is a SQL method:
```sql
SELECT FROM salary.toJSON() FROM employee
```

As you can see the method is executed against a field/value. Methods can receive parameters, like functions. You can concatenate N operators in sequence.

!NOTE: methods are case-insensitive.


[[SQL-Method-Squared]]
[discrete]
##### `[]`
Execute an expression against the item. An item can be a multi-value object like a map, a list, an array or a document. For documents and maps, the item must be a string. For lists and arrays, the index is a number.

Syntax: ```<value>[<expression>]```

Applies to the following types:
- document,
- map,
- list,
- array

[discrete]
**Examples**

Get the item with key "phone" in a map:
```sql
SELECT FROM Profile WHERE '+39' IN contacts[phone].left(3)
```

Get the first 10 tags of posts:
```sql
SELECT FROM tags[0-9] FROM Posts
```

---

[discrete]
##### .append()
Appends a string to another one.

Syntax: ```<value>.append(<value>)```

Applies to the following types:
- string

[discrete]
**Examples**

```sql
SELECT name.append(' ').append(surname) FROM Employee
```


---

[discrete]
##### .asBoolean()
Transforms the field into a Boolean type. If the origin type is a string, then "true" and "false" is checked. If it's a number than 1 means TRUE while 0 means FALSE.

Syntax: ```<value>.asBoolean()```

Applies to the following types:
- string,
- short,
- int,
- long

[discrete]
**Examples**

```sql
SELECT FROM Users WHERE online.asBoolean() = true
```

---

[discrete]
##### .asDate()
Transforms the field into a Date type.

Syntax: ```<value>.asDate()```

Applies to the following types:
- string,
- long

[discrete]
**Examples**

Time is stored as long type measuring milliseconds since a particular day. Returns all the records where time is before the year 2010:

```sql
SELECT FROM Log WHERE time.asDateTime() < '01-01-2010 00:00:00' 
```
---

[discrete]
##### .asDateTime()
Transforms the field into a Date type but parsing also the time information.

Syntax: ```<value>.asDateTime()```

Applies to the following types:
- string,
- long

[discrete]
**Examples**

Time is stored as long type measuring milliseconds since a particular day. Returns all the records where time is before the year 2010:

```sql
SELECT FROM Log WHERE time.asDateTime() < '01-01-2010 00:00:00' 
```

---

[discrete]
##### .asDecimal()
Transforms the field into an Decimal type. Use Decimal type when treat currencies.

Syntax: ```<value>.asDecimal()```

Applies to the following types:
- any

[discrete]
**Examples**

```sql
SELECT salary.asDecimal() FROM Employee
```

---

[discrete]
##### .asFloat()
Transforms the field into a float type.

Syntax: ```<value>.asFloat()```

Applies to the following types:
- any

[discrete]
**Examples**

```sql
SELECT ray.asFloat() > 3.14
```


---


[discrete]
##### .asInteger()
Transforms the field into an integer type.

Syntax: ```<value>.asInteger()```

Applies to the following types:
- any

[discrete]
**Examples**

Converts the first 3 chars of 'value' field in an integer:
```sql
SELECT value.left(3).asInteger() FROM Log
```

---


[discrete]
##### .asList()
Transforms the value in a List. If it's a single item, a new list is created.

Syntax: ```<value>.asList()```

Applies to the following types:
- any

[discrete]
**Examples**

```sql
SELECT tags.asList() FROM Friend
```

---


[discrete]
##### .asLong()
Transforms the field into a Long type.

Syntax: ```<value>.asLong()```

Applies to the following types:
- any

[discrete]
**Examples**

```sql
SELECT date.asLong() FROM Log
```

---

[discrete]
##### .asMap()
Transforms the value in a Map where even items are the keys and odd items are values.

Syntax: ```<value>.asMap()```

Applies to the following types:
- collections

[discrete]
**Examples**

```sql
SELECT tags.asMap() FROM Friend
```
---

[discrete]
##### .asSet()
Transforms the value in a Set. If it's a single item, a new set is created. Sets do not allow duplicates.

Syntax: ```<value>.asSet()```

Applies to the following types:
- any

[discrete]
**Examples**

```sql
SELECT tags.asSet() FROM Friend
```

---

[discrete]
##### .asString()
Transforms the field into a string type.

Syntax: ```<value>.asString()```

Applies to the following types:
- any

[discrete]
**Examples**

Get all the salaries with decimals:
```sql
SELECT salary.asString().indexof('.') > -1
```

---

[discrete]
##### .charAt()
Returns the character of the string contained in the position 'position'. 'position' starts from 0 to string length.

Syntax: ```<value>.charAt(<position>)```

Applies to the following types:
- string

[discrete]
**Examples**

Get the first character of the users' name:
```sql
SELECT FROM User WHERE name.charAt( 0 ) = 'L'
```

---

[discrete]
##### .convert()
Convert a value to another type.

Syntax: ```<value>.convert(<type>)```

Applies to the following types:
- any

[discrete]
**Examples**

```sql
SELECT dob.convert( 'date' ) FROM User
```

---

[discrete]
##### .exclude()
Excludes some properties in the resulting document.

Syntax: ```<value>.exclude(<field-name>[,]*)```

Applies to the following types:
- document record

[discrete]
**Examples**

```sql
SELECT EXPAND( @this.exclude( 'password' ) ) FROM OUser
```


You can specify a wildcard as ending character to exclude all the fields that start with a certain string. Example to exclude all the outgoing and incoming edges:

```sql
SELECT EXPAND( @this.exclude( 'out_*', 'in_*' ) ) FROM V
```

---

[discrete]
##### .format()
Returns the value formatted using the common "printf" syntax. For the complete reference goto http://java.sun.com/j2se/1.5.0/docs/api/java/util/Formatter.html#syntax[Java Formatter JavaDoc].

Syntax: ```<value>.format(<format>)```

Applies to the following types:
- any

[discrete]
**Examples**
Formats salaries as number with 11 digits filling with 0 at left:

```sql
SELECT salary.format("%-011d") FROM Employee
```

---

[discrete]
##### .hash()

Returns the hash of the field. Supports all the algorithms available in the JVM.

Syntax: ```<value>```.hash([<algorithm>])```

Applies to the following types:
- string

[discrete]
###### Example

Get the SHA-512 of the field "password" in the type User:

```sql
SELECT password.hash('SHA-512') FROM User
```

---

[discrete]
##### .include()
Include only some properties in the resulting document.

Syntax: ```<value>.include(<field-name>[,]*)```

Applies to the following types:
- document record

[discrete]
**Examples**

```sql
SELECT EXPAND( @this.include( 'name' ) ) FROM OUser
```

You can specify a wildcard as ending character to inclide all the fields that start with a certain string. Example to include all the fields that starts with `amonut`:

```sql
SELECT EXPAND( @this.exclude( 'amount*' ) ) FROM V
```

---

[discrete]
##### .indexOf()
Returns the position of the 'string-to-search' inside the value. It returns -1 if no occurrences are found. 'begin-position' is the optional position where to start, otherwise the beginning of the string is taken (=0).

Syntax: ```<value>.indexOf(<string-to-search> <<, <begin-position>)```

Applies to the following types:
- string

[discrete]
**Examples**
Returns all the UK numbers:
```sql
SELECT FROM Contact WHERE phone.indexOf('+44') > -1
```
---

[discrete]
##### .javaType()
Returns the corresponding Java Type.

Syntax: ```<value>.javaType()```

Applies to the following types:
- any

[discrete]
**Examples**
Prints the Java type used to store dates:
```sql
SELECT FROM date.javaType() FROM Events
```

---

[discrete]
##### .keys()
Returns the map's keys as a separate set. Useful to use in conjunction with IN, CONTAINS and CONTAINSALL operators.

Syntax: ```<value>.keys()```

Applies to the following types:
- maps
- documents

[discrete]
**Examples**
```sql
SELECT FROM Actor WHERE 'Luke' IN map.keys()
```

---


[discrete]
##### .left()
Returns a substring of the original cutting from the begin and getting 'len' characters.

Syntax: ```<value>.left(<length>)```

Applies to the following types:
- string

[discrete]
**Examples**
```sql
SELECT FROM Actors WHERE name.left( 4 ) = 'Luke'
```

---

[discrete]
##### .length()
Returns the length of the string. If the string is null 0 will be returned.

Syntax: ```<value>.length()```

Applies to the following types:
- string

[discrete]
**Examples**
```sql
SELECT FROM Providers WHERE name.length() > 0
```

---


[discrete]
##### .normalize()
Form can be NDF, NFD, NFKC, NFKD. Default is NDF. pattern-matching if not defined is "\\p{InCombiningDiacriticalMarks}+". For more information look at <a href="http://www.unicode.org/reports/tr15/tr15-23.html">Unicode Standard</a>.

Syntax: ```<value>.normalize( [<form>] <<,<pattern-matching>] )```

Applies to the following types:
- string

[discrete]
**Examples**
```sql
SELECT FROM V WHERE name.normalize() AND name.normalize('NFD')
```
---

[discrete]
##### .prefix()
Prefixes a string to another one.

Syntax: ```<value>.prefix('<string>')```

Applies to the following types:
- string

[discrete]
**Examples**
```sql
SELECT name.prefix('Mr. ') FROM Profile
```

---

[discrete]
##### .remove()
Removes the first occurrence of the passed items.

Syntax: ```<value>.remove(<item>*)```

Applies to the following types:
- collection

[discrete]
**Examples**

```sql
SELECT out().in().remove( @this ) FROM V
```


---

[discrete]
##### .removeAll()
Removes all the occurrences of the passed items.

Syntax: ```<value>.removeAll(<item>*)```

Applies to the following types:
- collection

[discrete]
**Examples**

```sql
SELECT out().in().removeAll( @this ) FROM V
```

---

[discrete]
##### .replace()
Replace a string with another one.

Syntax: ```<value>.replace(<to-find>, <to-replace>)```

Applies to the following types:
- string

[discrete]
**Examples**

```sql
SELECT name.replace('Mr.', 'Ms.') FROM User
```

---

[discrete]
##### .right()
Returns a substring of the original cutting from the end of the string 'length' characters.

Syntax: ```<value>.right(<length>)```

Applies to the following types:
- string

[discrete]
**Examples**

Returns all the vertices where the name ends by "ke".
```sql
SELECT FROM V WHERE name.right( 2 ) = 'ke'
```

---

[discrete]
##### .size()
Returns the size of the collection.

Syntax: ```<value>.size()```

Applies to the following types:
- collection

[discrete]
**Examples**

Returns all the items in a tree with children:
```sql
SELECT FROM TreeItem WHERE children.size() > 0
```

---

[discrete]
##### .subString()
Returns a substring of the original cutting from 'begin' index up to 'end' index (not included).

Syntax: ```<value>.subString(<begin> <<,<end>] )```

Applies to the following types:
- string

[discrete]
**Examples**

Get all the items where the name begins with an "L":
```sql
SELECT name.substring( 0, 1 ) = 'L' FROM StockItems
```

Substring of `ArcadeDB`
```sql
SELECT "ArcadeDB".substring(0,6)
```
returns `Orient`

---

[discrete]
##### .trim()
Returns the original string removing white spaces from the begin and the end.

Syntax: ```<value>.trim()```

Applies to the following types:
- string

[discrete]
**Examples**
```sql
SELECT name.trim() == 'Luke' FROM Actors
```

---

[discrete]
##### .toJSON()
Returns the record in JSON format.

Syntax: ```<value>.toJSON([<format>])```

Where:
- **format** optional, allows custom formatting rules (separate multiple options by comma). Rules are the following:
 - **rid** to include records's RIDs as attribute "@rid"
 - **type** to include the type name in the attribute "@type"
 - **attribSameRow** put all the attributes in the same row
 - **indent** is the indent level as integer. By Default no ident is used
 - **fetchPlan** is the <<FetchPlan,../java/Fetching-Strategies>> to use while fetching linked records
 - **alwaysFetchEmbedded** to always fetch embedded records (without considering the fetch plan)
 - **dateAsLong** to return dates (Date and Datetime types) as long numers
 - **prettyPrint** indent the returning JSON in readeable (pretty) way

Applies to the following types:
- record

[discrete]
**Examples**
```sql
create vertex type Test
insert into Test content {"attr1": "value 1", "attr2": "value 2"}

select @this.toJson('rid,version,fetchPlan:in_*:-2 out_*:-2') from Test
```

---

[discrete]
##### .toLowerCase()
Returns the string in lower case.

Syntax: ```<value>.toLowerCase()```

Applies to the following types:
- string

[discrete]
**Examples**
```sql
SELECT name.toLowerCase() == 'luke' FROM Actors
```

---

[discrete]
##### .toUpperCase()
Returns the string in upper case.

Syntax: ```<value>.toUpperCase()```

Applies to the following types:
- string

[discrete]
**Examples**
```sql
SELECT name.toUpperCase() == 'LUKE' FROM Actors
```

---

[discrete]
##### .type()
Returns the value's ArcadeDB Type.

Syntax: ```<value>.type()```

Applies to the following types:
- any

[discrete]
**Examples**
Prints the type used to store dates:
```sql
SELECT FROM date.type() FROM Events
```

---


[discrete]
##### .values()
Returns the map's values as a separate collection. Useful to use in conjunction with IN, CONTAINS and CONTAINSALL operators.

Syntax: ```<value>.values()```

Applies to the following types:
- maps
- documents


[discrete]
**Examples**
```sql
SELECT FROM Clients WHERE map.values() CONTAINSALL ( name is not null)
```
---
