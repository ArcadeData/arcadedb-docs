
### SQL Methods

SQL Methods are similar to <<SQL functions,SQL-Functions>> but they apply to values. In Object Oriented paradigm they are called "methods", as functions related to a type. So what's the difference between a function and a method?

This is a <<SQL function,SQL-Functions>>:
```sql
SELECT FROM sum( salary ) FROM employee
```

This is a SQL method:
```sql
SELECT FROM salary.toJSON() FROM employee
```

As you can see the method is executed against a field/value. Methods can receive parameters, like functions. You can concatenate N operators in sequence.

>**Note**: operators are case-insensitive.

#### Bundled methods

##### Methods by category


[%header,cols=4]
|===
| Conversions | String manipulation | Collections | Misc
|<<convert(),SQL-Methods.md#convert)|<<append(),SQL-Methods.md#append)|<<\<<\],SQL-Methods>>|<<exclude(),SQL-Methods.md#exclude)
|<<asBoolean(),SQL-Methods.md#asboolean)|<<charAt(),SQL-Methods.md#charat)|<<size(),SQL-Methods.md#size)|<<include(),SQL-Methods.md#include)
|<<asDate(),SQL-Methods.md#asdate)|<<indexOf(),SQL-Methods.md#indexof)|<<remove(),SQL-Methods.md#remove)|<<javaType(),SQL-Methods.md#javatype)
|<<asDatetime(),SQL-Methods.md#asdatetime)|<<left(),SQL-Methods.md#left)|<<removeAll(),SQL-Methods.md#removeall)|<<toJSON(),SQL-Methods.md#tojson)
|<<asDecimal(),SQL-Methods.md#asdecimal)|<<right(),SQL-Methods.md#right)|<<keys(),SQL-Methods.md#keys)|<<type(),SQL-Methods.md#type)
|<<asFloat(),SQL-Methods.md#asfloat)|<<prefix(),SQL-Methods.md#prefix)|<<values(),SQL-Methods.md#values)
|<<asInteger(),SQL-Methods.md#asinteger)|<<trim(),SQL-Methods.md#trim)
|<<asList(),SQL-Methods.md#aslist)|<<replace(),SQL-Methods.md#replace)
|<<asLong(),SQL-Methods.md#aslong)|<<length(),SQL-Methods.md#length)
|<<asMap(),SQL-Methods.md#asmap)|<<subString(),SQL-Methods.md#substring)
|<<asSet(),SQL-Methods.md#asset)|<<toLowerCase(),SQL-Methods.md#tolowercase)
|<<asString(),SQL-Methods.md#asstring)|<<toUpperCase(),SQL-Methods.md#touppercase)
|<<normalize(),SQL-Methods.md#normalize)|<<hash(),SQL-Methods.md#hash)
||<<format(),SQL-Methods.md#format)
|===


##### Methods by name

[%header,cols=4]
|===
|<<\<<\],SQL-Methods>>|<<append(),SQL-Methods.md#append)|<<asBoolean(),SQL-Methods.md#asboolean)|<<asDate(),SQL-Methods.md#asdate)|<<asDatetime(),SQL-Methods.md#asdatetime)
|<<asDecimal(),SQL-Methods.md#asdecimal)|<<asFloat(),SQL-Methods.md#asfloat)|<<asInteger(),SQL-Methods.md#asinteger)|<<asList(),SQL-Methods.md#aslist)|<<asLong(),SQL-Methods.md#aslong)|<<asMap(),SQL-Methods.md#asmap)
|<<asSet(),SQL-Methods.md#asset)|<<asString(),SQL-Methods.md#asstring)|<<charAt(),SQL-Methods.md#charat)|<<convert(),SQL-Methods.md#convert)|<<exclude(),SQL-Methods.md#exclude)|<<format(),SQL-Methods.md#format)
|<<hash(),SQL-Methods.md#hash)|<<include(),SQL-Methods.md#include)|<<indexOf(),SQL-Methods.md#indexof)|<<javaType(),SQL-Methods.md#javatype)|<<keys(),SQL-Methods.md#keys)|<<left(),SQL-Methods.md#left)
|<<length(),SQL-Methods.md#length)|<<normalize(),SQL-Methods.md#normalize)|<<prefix(),SQL-Methods.md#prefix)|<<remove(),SQL-Methods.md#remove)|<<removeAll(),SQL-Methods.md#removeall)|<<replace(),SQL-Methods.md#replace)
|<<right(),SQL-Methods.md#right)|<<size(),SQL-Methods.md#size)|<<subString(),SQL-Methods.md#substring)|<<trim(),SQL-Methods.md#trim)|<<toJSON(),SQL-Methods.md#tojson)|<<toLowerCase(),SQL-Methods.md#tolowercase)
|<<toUpperCase(),SQL-Methods.md#touppercase)|<<type(),SQL-Methods.md#type)|<<values(),SQL-Methods.md#values)
|===


##### `<<]`
Execute an expression against the item. An item can be a multi-value object like a map, a list, an array or a document. For documents and maps, the item must be a string. For lists and arrays, the index is a number.

Syntax: ```<value><<<expression>]```

Applies to the following types:
- document,
- map,
- list,
- array

###### Examples

Get the item with key "phone" in a map:
```sql
SELECT FROM Profile WHERE '+39' IN contacts<<phone].left(3)
```

Get the first 10 tags of posts:
```sql
SELECT FROM tags<<0-9] FROM Posts
```

#### History

- 1.0rc5: First version

---

##### .append()
Appends a string to another one.

Syntax: ```<value>.append(<value>)```

Applies to the following types:
- string

###### Examples

```sql
SELECT name.append(' ').append(surname) FROM Employee
```

#### History

- 1.0rc1: First version

---

##### .asBoolean()
Transforms the field into a Boolean type. If the origin type is a string, then "true" and "false" is checked. If it's a number then 1 means TRUE while 0 means FALSE.

Syntax: ```<value>.asBoolean()```

Applies to the following types:
- string,
- short,
- int,
- long

###### Examples

```sql
SELECT FROM Users WHERE online.asBoolean() = true
```

#### History

- 0.9.15: First version

---

##### .asDate()
Transforms the field into a Date type. To know more about it, look at <<Managing Dates,../general/Managing-Dates>>.

Syntax: ```<value>.asDate()```

Applies to the following types:
- string,
- long

###### Examples

Time is stored as long type measuring milliseconds since a particular day. Returns all the records where time is before the year 2010:

```sql
SELECT FROM Log WHERE time.asDateTime() < '01-01-2010 00:00:00' 
```
#### History

- 0.9.14: First version

---

##### .asDateTime()
Transforms the field into a Date type but parsing also the time information. To know more about it, look at <<Managing Dates,../general/Managing-Dates>>.

Syntax: ```<value>.asDateTime()```

Applies to the following types:
- string,
- long

###### Examples

Time is stored as long type measuring milliseconds since a particular day. Returns all the records where time is before the year 2010:

```sql
SELECT FROM Log WHERE time.asDateTime() < '01-01-2010 00:00:00' 
```

#### History

- 0.9.14: First version

---

##### .asDecimal()
Transforms the field into an Decimal type. Use Decimal type when treat currencies.

Syntax: ```<value>.asDecimal()```

Applies to the following types:
- any

###### Examples

```sql
SELECT salary.asDecimal() FROM Employee
```
#### History

- 1.0rc1: First version

---

##### .asFloat()
Transforms the field into a float type.

Syntax: ```<value>.asFloat()```

Applies to the following types:
- any

###### Examples

```sql
SELECT ray.asFloat() > 3.14
```

#### History

- 0.9.14: First version

---


##### .asInteger()
Transforms the field into an integer type.

Syntax: ```<value>.asInteger()```

Applies to the following types:
- any

###### Examples

Converts the first 3 chars of 'value' field in an integer:
```sql
SELECT value.left(3).asInteger() FROM Log
```
#### History

- 0.9.14: First version

---


##### .asList()
Transforms the value in a List. If it's a single item, a new list is created.

Syntax: ```<value>.asList()```

Applies to the following types:
- any

###### Examples

```sql
SELECT tags.asList() FROM Friend
```
#### History

- 1.0rc2: First version

---


##### .asLong()
Transforms the field into a Long type. To know more about it, look at <<Managing Dates,../general/Managing-Dates>>.

Syntax: ```<value>.asLong()```

Applies to the following types:
- any

###### Examples

```sql
SELECT date.asLong() FROM Log
```
#### History

- 1.0rc1: First version

---

##### .asMap()
Transforms the value in a Map where even items are the keys and odd items are values.

Syntax: ```<value>.asMap()```

Applies to the following types:
- collections

###### Examples

```sql
SELECT tags.asMap() FROM Friend
```
#### History

- 1.0rc2: First version

---

##### .asSet()
Transforms the value in a Set. If it's a single item, a new set is created. Sets doesn't allow duplicates.

Syntax: ```<value>.asSet()```

Applies to the following types:
- any

###### Examples

```sql
SELECT tags.asSet() FROM Friend
```
#### History

- 1.0rc2: First version

---

##### .asString()
Transforms the field into a string type.

Syntax: ```<value>.asString()```

Applies to the following types:
- any

###### Examples

Get all the salaries with decimals:
```sql
SELECT salary.asString().indexof('.') > -1
```

#### History

- 0.9.14: First version

---

##### .charAt()
Returns the character of the string contained in the position 'position'. 'position' starts from 0 to string length.

Syntax: ```<value>.charAt(<position>)```

Applies to the following types:
- string

###### Examples

Get the first character of the users' name:
```sql
SELECT FROM User WHERE name.charAt( 0 ) = 'L'
```
#### History

- 0.9.7: First version

---

##### .convert()
Convert a value to another type.

Syntax: ```<value>.convert(<type>)```

Applies to the following types:
- any

###### Examples

```sql
SELECT dob.convert( 'date' ) FROM User
```
#### History

- 1.0rc2: First version

---

##### .exclude()
Excludes some properties in the resulting document.

Syntax: ```<value>.exclude(<field-name><<,]*)```

Applies to the following types:
- document record

###### Examples

```sql
SELECT EXPAND( @this.exclude( 'password' ) ) FROM OUser
```


Starting from 2.2.19 you can specify a wildcard as ending character to exclude all the fields that start with a certain string. Example to exclude all the outgoing and incloming edges:

```sql
SELECT EXPAND( @this.exclude( 'out_*', 'in_*' ) ) FROM V
```

---

##### .format()
Returns the value formatted using the common "printf" syntax. For the complete reference goto <<Java Formatter JavaDoc,http://java.sun.com/j2se/1.5.0/docs/api/java/util/Formatter.html#syntax).  To know more about it, look at <<Managing Dates,../general/Managing-Dates>>.

Syntax: ```<value>.format(<format>)```

Applies to the following types:
- any

###### Examples
Formats salaries as number with 11 digits filling with 0 at left:

```sql
SELECT salary.format("%-011d") FROM Employee
```

#### History

- 0.9.8: First version

---

##### .hash()

Returns the hash of the field. Supports all the algorithms available in the JVM.

Syntax: ```<value>```.hash(<<<algorithm>])```

Applies to the following types:
- string

###### Example

Get the SHA-512 of the field "password" in the type User:

```sql
SELECT password.hash('SHA-512') FROM User
```
###### History
- 1.7: First version

---

##### .include()
Include only some properties in the resulting document.

Syntax: ```<value>.include(<field-name><<,]*)```

Applies to the following types:
- document record

###### Examples

```sql
SELECT EXPAND( @this.include( 'name' ) ) FROM OUser
```

Starting from 2.2.19 you can specify a wildcard as ending character to inclide all the fields that start with a certain string. Example to include all the fields that starts with `amonut`:

```sql
SELECT EXPAND( @this.exclude( 'amount*' ) ) FROM V
```

#### History

- 1.0rc2: First version

---

##### .indexOf()
Returns the position of the 'string-to-search' inside the value. It returns -1 if no occurrences are found. 'begin-position' is the optional position where to start, otherwise the beginning of the string is taken (=0).

Syntax: ```<value>.indexOf(<string-to-search> <<, <begin-position>)```

Applies to the following types:
- string

###### Examples
Returns all the UK numbers:
```sql
SELECT FROM Contact WHERE phone.indexOf('+44') > -1
```
#### History

- 0.9.10: First version

---

##### .javaType()
Returns the corresponding Java Type.

Syntax: ```<value>.javaType()```

Applies to the following types:
- any

###### Examples
Prints the Java type used to store dates:
```sql
SELECT FROM date.javaType() FROM Events
```
#### History

- 1.0rc1: First version

---

##### .keys()
Returns the map's keys as a separate set. Useful to use in conjunction with IN, CONTAINS and CONTAINSALL operators.

Syntax: ```<value>.keys()```

Applies to the following types:
- maps
- documents

###### Examples
```sql
SELECT FROM Actor WHERE 'Luke' IN map.keys()
```
#### History
- 1.0rc1: First version

---


##### .left()
Returns a substring of the original cutting from the begin and getting 'len' characters.

Syntax: ```<value>.left(<length>)```

Applies to the following types:
- string

###### Examples
```sql
SELECT FROM Actors WHERE name.left( 4 ) = 'Luke'
```

#### History
- 0.9.7: First version

---

##### .length()
Returns the length of the string. If the string is null 0 will be returned.

Syntax: ```<value>.length()```

Applies to the following types:
- string

###### Examples
```sql
SELECT FROM Providers WHERE name.length() > 0
```
#### History
- 0.9.7: First version

---


##### .normalize()
Form can be NDF, NFD, NFKC, NFKD. Default is NDF. pattern-matching if not defined is "\\p{InCombiningDiacriticalMarks}+". For more information look at <a href="http://www.unicode.org/reports/tr15/tr15-23.html">Unicode Standard</a>.

Syntax: ```<value>.normalize( <<<form>] <<,<pattern-matching>] )```

Applies to the following types:
- string

###### Examples
```sql
SELECT FROM V WHERE name.normalize() AND name.normalize('NFD')
```
#### History

- 1.4.0: First version
---



##### .prefix()
Prefixes a string to another one.

Syntax: ```<value>.prefix('<string>')```

Applies to the following types:
- string

###### Examples
```sql
SELECT name.prefix('Mr. ') FROM Profile
```
#### History
- 1.0rc1: First version

---

##### .remove()
Removes the first occurrence of the passed items.

Syntax: ```<value>.remove(<item>*)```

Applies to the following types:
- collection

###### Examples

```sql
SELECT out().in().remove( @this ) FROM V
```

#### History

- 1.0rc1: First version

---

##### .removeAll()
Removes all the occurrences of the passed items.

Syntax: ```<value>.removeAll(<item>*)```

Applies to the following types:
- collection

###### Examples

```sql
SELECT out().in().removeAll( @this ) FROM V
```

#### History

- 1.0rc1: First version

---

##### .replace()
Replace a string with another one.

Syntax: ```<value>.replace(<to-find>, <to-replace>)```

Applies to the following types:
- string

###### Examples

```sql
SELECT name.replace('Mr.', 'Ms.') FROM User
```

#### History

- 1.0rc1: First version

---


##### .right()
Returns a substring of the original cutting from the end of the string 'length' characters.

Syntax: ```<value>.right(<length>)```

Applies to the following types:
- string

###### Examples

Returns all the vertices where the name ends by "ke".
```sql
SELECT FROM V WHERE name.right( 2 ) = 'ke'
```

#### History

- 0.9.7: First version

---

##### .size()
Returns the size of the collection.

Syntax: ```<value>.size()```

Applies to the following types:
- collection

###### Examples

Returns all the items in a tree with children:
```sql
SELECT FROM TreeItem WHERE children.size() > 0
```

#### History

- 0.9.7: First version

---

##### .subString()
Returns a substring of the original cutting from 'begin' index up to 'end' index (not included).

Syntax: ```<value>.subString(<begin> <<,<end>] )```

Applies to the following types:
- string

###### Examples

Get all the items where the name begins with an "L":
```sql
SELECT name.substring( 0, 1 ) = 'L' FROM StockItems
```

Substring of `ArcadeDB`
```sql
SELECT "ArcadeDB".substring(0,6)
```
returns `Orient`

#### History
- 0.9.7: First version

---

##### .trim()
Returns the original string removing white spaces from the begin and the end.

Syntax: ```<value>.trim()```

Applies to the following types:
- string

###### Examples
```sql
SELECT name.trim() == 'Luke' FROM Actors
```

#### History

- 0.9.7: First version

---

##### .toJSON()
Returns the record in JSON format.

Syntax: ```<value>.toJSON(<<<format>])```

Where:
- **format** optional, allows custom formatting rules (separate multiple options by comma). Rules are the following:
 - **type** to include the fields' types in the "@fieldTypes" attribute
 - **rid** to include records's RIDs as attribute "@rid"
 - **version** to include records' versions in the attribute "@version"
 - **type** to include the type name in the attribute "@type"
 - **attribSameRow** put all the attributes in the same row
 - **indent** is the indent level as integer. By Default no ident is used
 - **fetchPlan** is the <<FetchPlan,../java/Fetching-Strategies>> to use while fetching linked records
 - **alwaysFetchEmbedded** to always fetch embedded records (without considering the fetch plan)
 - **dateAsLong** to return dates (Date and Datetime types) as long numers
 - **prettyPrint** indent the returning JSON in readeable (pretty) way

Applies to the following types:
- record

###### Examples
```sql
create type Test extends V
insert into Test content {"attr1": "value 1", "attr2": "value 2"}

select @this.toJson('rid,version,fetchPlan:in_*:-2 out_*:-2') from Test
```
#### History
- 0.9.8: First version

---


##### .toLowerCase()
Returns the string in lower case.

Syntax: ```<value>.toLowerCase()```

Applies to the following types:
- string

###### Examples
```sql
SELECT name.toLowerCase() == 'luke' FROM Actors
```

#### History
- 0.9.7: First version
---


##### .toUpperCase()
Returns the string in upper case.

Syntax: ```<value>.toUpperCase()```

Applies to the following types:
- string

###### Examples
```sql
SELECT name.toUpperCase() == 'LUKE' FROM Actors
```

#### History
- 0.9.7: First version

---

##### .type()
Returns the value's ArcadeDB Type.

Syntax: ```<value>.type()```

Applies to the following types:
- any

###### Examples
Prints the type used to store dates:
```sql
SELECT FROM date.type() FROM Events
```
#### History

- 1.0rc1: First version

---


##### .values()
Returns the map's values as a separate collection. Useful to use in conjunction with IN, CONTAINS and CONTAINSALL operators.

Syntax: ```<value>.values()```

Applies to the following types:
- maps
- documents


###### Examples
```sql
SELECT FROM Clients WHERE map.values() CONTAINSALL ( name is not null)
```
#### History

- 1.0rc1: First version
---
