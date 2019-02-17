# Project: Logs Analysis

This project implements a python script that answers the following questions regarding the data stored in PostgreSQL.

* What are the most popular three articles of all time?
* Who are the most popular article authors of all time?
* On which days did more than 1% of requests lead to errors?

## Dependencies

* Python 3
* psycopg2-binary

## Instructions. How to run this project

create the following view under the psql command line utility:


```sql

create view article_paths as select id, title, author, '/article/' || slug as path from articles;

```

In the commnad line execute:

```console
vagrant@vagrant:/vagrant/logreport$ chamod +x log_analysis.py
vagrant@vagrant:/vagrant/logreport$ ./log_analysis.py
```

The scripts can optionaly take up to two positional arguments, as follow:

```
log_analysis.py [MAX-AUTHOR-LIST-SIZE] [MAX-ARTICLES-LIST-SIZE]
```

where,

* MAX-AUTHOR-LIST-SIZE is the number of records returned in the Question 2; Default is 3.
* MAX-ARTICLES-LIST-SIZE is the number of records returned in the Question 1; Default is 3.

## Data Schema

I present in this section the data schema and some information I was able to infer from the dataset provided.

### Tables

* **articles**
  
    ```
    Column |           Type           |                       Modifiers                       
    --------+--------------------------+-------------------------------------------------------
    author | integer                  | not null
    title  | text                     | not null
    slug   | text                     | not null
    lead   | text                     | 
    body   | text                     | 
    time   | timestamp with time zone | default now()
    id     | integer                  | not null default nextval('articles_id_seq'::regclass)
    Indexes:
        "articles_pkey" PRIMARY KEY, btree (id)
        "articles_slug_key" UNIQUE CONSTRAINT, btree (slug)
    Foreign-key constraints:
        "articles_author_fkey" FOREIGN KEY (author) REFERENCES authors(id)
    ```

* **authors**
  
    ```
    Column |  Type   |                      Modifiers                       
    --------+---------+------------------------------------------------------
    name   | text    | not null
    bio    | text    | 
    id     | integer | not null default nextval('authors_id_seq'::regclass)
    Indexes:
        "authors_pkey" PRIMARY KEY, btree (id)
    Referenced by:
        TABLE "articles" CONSTRAINT "articles_author_fkey" FOREIGN KEY (author) REFERENCES authors(id)
    ```

* **log**

    ```
    Column |           Type           |                    Modifiers                     
    --------+--------------------------+--------------------------------------------------
    path   | text                     | 
    ip     | inet                     | 
    method | text                     | 
    status | text                     | 
    time   | timestamp with time zone | default now()
    id     | integer                  | not null default nextval('log_id_seq'::regclass)
    Indexes:
        "log_pkey" PRIMARY KEY, btree (id)
    ```

### Relationship between tables

#### Authors x Articles 
The table Articles has foreign key to Author without restrictions, hence there is a 1-to-many relashionship between them.
  
#### Log x Articles
Articles are accessiable under the following *path* syntax: **/article/\<*article-slug*\>**. Since *slug* uniquely identify an article, we can safely establish a direct relationship between the tables *Log* and *Articles* using the field path in the table log.

#### Log x Authors
There is no direct relationship between the two tables, therefore we need to establish the relationship through the table *Articles*.

### Views

We utilized the following view in this project:

```sql

create view article_paths as select id, title, author, '/article/' || slug as path from articles;

```

This view builds the article's path using the field slug. It can be used to match logs and articles.


