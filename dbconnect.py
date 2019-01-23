import pymysql
import os
import time
import config as CONFIG

hostname = CONFIG.DB['host']
username = CONFIG.DB['username']
password = CONFIG.DB['password']
database = CONFIG.DB['database']

try:
    conn = pymysql.connect(
        host=hostname,
        user=username,
        passwd=password,
        db=database,
	port=3306
    )
    print('connected')
    conn.close()
except Exception as e:
    print('unable to connect')
    print(e)
    raise Exception(e)


def connection():
    try:
        conn = pymysql.connect(
            host=hostname,
            user=username,
            passwd=password,
            db=database
        )
        print ('connected')
        return conn
    except Exception as e:
        print('unable to connect')
        print (e)



def getData(query):
    my_connection = connection()
    try:
        with my_connection.cursor() as cursor:
            # Read a single record
            print (query)
            sql = query
            cursor.execute(sql)
            data = cursor.description
            for row in data:
                print (row)
            return cursor
    except Exception as e:
        print(e)
    finally:
        my_connection.close()


def setData(query):
    my_connection = connection()
    try:
        with my_connection.cursor() as cursor:
            # Create a new record
            print(query)
            sql = query
            cursor.execute(sql)

        # connection is not autocommit by default. So you must commit to save
        # your changes.
            my_connection.commit()
            return str(cursor.lastrowid)
    finally:
        my_connection.close()
