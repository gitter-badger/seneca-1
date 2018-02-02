==Supported Types==

Types should be a combination of Python, Cassandra, and Redis supported data types with secondary thought into other
potentially supported systems. Thus:

    Python Types:
        int
        bool
        double <- fixed precision with Decimal library
        string

    Cassandra Types:
        blob / bytes / data
        json / dict?
        timestamp
        uuid
        tuple?

    Redis Types:
        hashmaps / hset, hget
        sets / sset, sget

==Control Flow==

    if / elif / else
    map()
    filter()
    try / except / eventually
    assert

==Data access==

Ultimately, data is accessed from the current state of the blockchain which is a Redis DB for now. Thus, getting variables and setting variables should feel like programming calls but are actually queries.

We need to be able to: SELECT, INSERT, UPDATE all with WHERE conditionals (I'm thinking using maps and filters to do this?)

We need to be able to CREATE new tables with a set schema. This schema should be Cassandra compatible, but worst comes to worst, it's just a bunch of data blobs that we serialize later. Would rather not do this for speed, however.

We need to be able to pull tables and join them either from the SQL database itself or via some library such as Pandas (http://pandas.pydata.org/pandas-docs/stable/merging.html).

JOINS and MERGEs should never alter the parent tables.

We *should* be able to create relationships between tables so that complex objects can be created and stored.

Data could be accessed in a way such as:

```
    x = get(from=<USER_PUBLIC_KEY>/<TABLE_NAME>, where=<CONDITIONAL>)
```