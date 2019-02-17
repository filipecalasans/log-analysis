#!/usr/bin/env python3

import sys
import psycopg2
import psycopg2.extras

article_paths_view = "article_paths"
author_list_size = 3
articles_list_size = 3

DB_NAME = "news"
DB_CONNECTION_STRING = "dbname={}".format(DB_NAME)

db = psycopg2.connect(DB_CONNECTION_STRING)
if db is None:
    print("Could not connect to the Database")
    exit(1)


def cursorFactory():
    return db.cursor(cursor_factory=psycopg2.extras.DictCursor)


def most_popular_articles_all_time():
    """

    answares: What are the most popular three articles of all time?

    return [{tile = "Article title", views = 12345}, ...]
    """

    popular_query = (
        "SELECT {view}.id, COUNT(*) as views "
        "FROM {view} JOIN log ON {view}.path = log.path "
        "GROUP BY {view}.id "
        "ORDER BY views DESC "
        "LIMIT {max}".format(view=article_paths_view,
                             max=articles_list_size)
    )

    query = (
        "WITH popular as ({popular}) "
        "SELECT title, views FROM popular JOIN articles "
        "ON articles.id = popular.id "
        "ORDER BY views DESC;".format(popular=popular_query)
    )

    cursor = cursorFactory()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def most_popular_author_of_all_time():
    """

    answares: Who are the most popular article authors of all time?

    return [{name = "Author Name", views = 12345}, ...]
    """

    # Get the most popular article
    subq = (
        "SELECT author as authorId, COUNT(*) as views "
        "FROM {view} JOIN log ON {view}.path = log.path "
        "GROUP BY author "
        "ORDER BY views DESC "
        "LIMIT {max}".format(view=article_paths_view,
                             max=author_list_size)
    )

    query = (
        "WITH popular_author as ({subquery})"
        "SELECT name, views FROM authors JOIN popular_author "
        "ON authorId = authors.id "
        "ORDER BY views DESC;".format(subquery=subq)
    )

    cursor = cursorFactory()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def days_with_more_than_1_pct_errors():
    """

    On which days did more than 1% of requests lead to errors?

    return [{month = 2, day = 20, year = 2019,
            date date(2019, 2, 20), total = 100, error = 1}, ...]
    """

    total_request = (
        "SELECT date_trunc('day', log.time) as day, COUNT(*) as total "
        "FROM log GROUP BY date_trunc('day', log.time)"
    )

    total_errors = (
        "SELECT day, COUNT(*) as error FROM "
        "("
        "SELECT date_trunc('day', log.time) as day "
        "FROM log WHERE status != '200 OK'"
        ") as subq "
        "GROUP BY day"
    )

    query = (
        "WITH total_requests as "
        "("
        "{total_requests}"
        "), "
        "errors as "
        "("
        "{total_errors}"
        ") "
        "SELECT "
        "EXTRACT(MONTH FROM date(total_requests.day)) as month, "
        "EXTRACT(DAY FROM date(total_requests.day)) as day, "
        "EXTRACT(YEAR FROM date(total_requests.day)) as year, "
        "to_char(date(total_requests.day),'FMMonth DD, YYYY') as date, "
        "total, "
        "error, "
        "ROUND((100.0*error)/total, 2) as error_pct "
        "FROM total_requests JOIN errors ON "
        "total_requests.day = errors.day "
        "WHERE (100*error) > total;".format(total_requests=total_request,
                                            total_errors=total_errors)
    )

    cursor = cursorFactory()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def view_popular_articles(data):
    str = ""
    for record in data:
        str += (
            "   \"{title}\" - {views} views\n"
        ).format(title=record['title'], views=record['views'])
    return str


def view_popular_author_all_times(data):
    str = ""
    for record in data:
        str += (
            "   {name} - {views} views\n"
        ).format(name=record['name'], views=record['views'])
    return str


def view_more_1_pct_error(data):

    str = ""
    for record in data:
        error_pct = record['error_pct']
        str += (
            "   {date} - {pct}% errors\n"
        ).format(date=record['date'],
                 pct=error_pct)
    return str


def main():
    print("\nWhat are the most popular three articles of all time?\n")
    print(view_popular_articles(most_popular_articles_all_time()))
    print("Who are the most popular article authors of all time?\n")
    print(view_popular_author_all_times(most_popular_author_of_all_time()))
    print("On which days did more than 1% of requests lead to errors?\n")
    print(view_more_1_pct_error(days_with_more_than_1_pct_errors()))


if __name__ == "__main__":
    args_len = len(sys.argv)
    if args_len > 1:
        author_list_size = int(sys.argv[1])
    if args_len > 2:
        articles_list_size = int(sys.argv[2])
    main()
