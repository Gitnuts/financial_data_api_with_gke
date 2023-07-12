import psycopg2
from configparser import ConfigParser
import sys


def config(filename='postgresdb.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def check_table_exists(table_name):
    params = config()

    # connect to the PostgreSQL server
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)

    cursor = conn.cursor()

    # Query to check if the table exists in the database
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM pg_catalog.pg_tables
            WHERE tablename = %s
        )
    """

    cursor.execute(query, (table_name,))
    exists = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return exists


if __name__ == '__main__':
    table_name = sys.argv[1]
    table_exists = check_table_exists(table_name)
    if table_exists:
        print(f"The table {table_name} exists. Continuing.")
        exit(0)
    else:
        print(f"The table {table_name} does not exist.")
        exit(1)
