from sqlalchemy import create_engine
import psycopg2
import io
import pandas as pd
from check_table import config
import sys


def upload_to_postgres(df, table, new_table=False, pk=None):

    params = config(section='postgresql_engine')
    engine = create_engine(**params)

    # Drop old table and create new empty table
    if new_table:
        df.head(0).to_sql(table, engine, if_exists='replace', index=False)
        with engine.connect() as con:
            con.execute(f'ALTER TABLE {table} ADD CONSTRAINT pk_{table} PRIMARY KEY ({"pk"});')

    conn = engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    try:
        cur.copy_from(output, table, null="")  # null values become ''
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':

    df = pd.read_csv('output.csv')
    upload_to_postgres(df, table=sys.argv[1], new_table=False)


