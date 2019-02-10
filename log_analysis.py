#!/usr/bin/python3

import psycopg2
import psycopg2.extras

article_paths_view = "article_paths"

DB_NAME = "news"
DB_CONNECTION_STRING = "dbname={}".format(DB_NAME)

db = psycopg2.connect(DB_CONNECTION_STRING)

def cursorFactory():
    return db.cursor(cursor_factory = psycopg2.extras.DictCursor)

# What are the most popular three articles of all time?
# Princess Shellfish Marries Prince Handsome" — 1201 views
def most_popular_articles_all_time():

    popular_query = (
        "WITH popular as (SELECT {view}.id, COUNT(*) as views "
        "FROM {view} JOIN log ON {view}.path = log.path "
        "GROUP BY {view}.id "
        "ORDER BY views DESC "
        "LIMIT 3)".format(view=article_paths_view)
    )

    query = (
        "{popular} "
        "SELECT title, views FROM popular JOIN  articles "
        "ON articles.id = popular.id;".format(popular=popular_query)
    )

    cursor = cursorFactory()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


# Who are the most popular article authors of all time?
def most_popular_author_of_all_time():

    #Get the most popular article    
    subq = (
        "(SELECT author as authorId, COUNT(*) as views "
        "FROM {view} JOIN log ON {view}.path = log.path "
        "GROUP BY author "
        "ORDER BY views DESC "
        "LIMIT 1) as subq".format(view=article_paths_view)
    )

    query = (
        "SELECT name, views FROM authors JOIN {subquery} "
        "ON authorId = authors.id;".format(subquery=subq)
    )

    cursor = cursorFactory()
    cursor.execute(query)
    result = cursor.fetchall()
    return result

# On which days did more than 1% of requests lead to errors?
def days_with_more_than_1_pct_errors():
    pass

def main():
    print("What are the most popular three articles of all time?")
    print(most_popular_articles_all_time())
    print ("") 
    print("Who are the most popular article authors of all time?")
    print(most_popular_author_of_all_time()) 
if __name__ == "__main__":
    main()
	
