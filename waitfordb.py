import os
import sys
import time

import psycopg2


def waitforpostgres():
    dbname = os.environ.get("POSTGRES_DB")
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    host = os.environ.get("POSTGRES_HOST")
    port = os.environ.get("POSTGRES_PORT")

    while True:
        try:
            conn = psycopg2.connect(
                dbname=dbname, user=user, password=password, host=host, port=port
            )
            conn.close()
            print("PostgreSQL is ready!")
            break
        except psycopg2.OperationalError as e:
            print(f"Waiting for PostgreSQL... {e}")
            time.sleep(1)


if __name__ == "__main__":
    waitforpostgres()
