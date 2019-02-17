#!/usr/bin/python3

import sys
import psycopg2
import psycopg2.extras

article_paths_view = "article_paths"
author_list_size = 3
articles_list_size = 3

DB_NAME = "news"
DB_CONNECTION_STRING = "dbname={}".format(DB_NAME)

db = psycopg2.connect(DB_CONNECTION_STRING)


def cursorFactory():
    return db.cursor(cursor_factory=psycopg2.extras.DictCursor)


# What are the most popular three articles of all time?
# Princess Shellfish Marries Prince Handsome" — 1201 views
#
# return [{tile = "Article title", views = 12345}, ...]
#
def most_popular_articles_all_time():

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


# Who are the most popular article authors of all time?
#
# return [{name = "Author Name", views = 12345}, ...]
#
def most_popular_author_of_all_time():

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
        "ON authorId = authors.id;".format(subquery=subq)
    )

    cursor = cursorFactory()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


# On which days did more than 1% of requests lead to errors?
#
# July 29, 2016 — 2.5% errors
#
# return [{month = 2, day = 20, year = 2019,
#          date date(2019, 2, 20), total = 100, error = 1}, ...]
def days_with_more_than_1_pct_errors():
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
        "date(total_requests.day) as date, "
        "total, "
        "error "
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

    month_list = ['January', 'February', 'March',
                  'April', 'May', 'June', 'July',
                  'August', 'September', 'October',
                  'November', 'December']

    str = ""
    for record in data:
        errors = float(record['error'])
        total = float(record['total'])
        error_pct = float(format((100.0 * errors)/total, '.1f'))
        month_num = int(record['month'])
        str += (
            "   {month} {day}, {year} - {pct}% errors\n"
        ).format(month=month_list[month_num-1],
                 day=int(record['day']),
                 year=int(record['year']),
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
