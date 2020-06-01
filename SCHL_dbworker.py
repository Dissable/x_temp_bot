import psycopg2
import os
import datetime
from shapely.geometry import Point


class Postgres(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            try:
                print('connecting to PostgreSQL database...')
                connection = Postgres._instance.connection = psycopg2.connect(os.environ['DATABASE_URL'],
                                                                              sslmode='require')
                cursor = Postgres._instance.cursor = connection.cursor()
                cursor.execute('SELECT VERSION()')
                db_version = cursor.fetchone()

            except Exception as error:
                print('Error: connection not established {}'.format(error))
                Postgres._instance = None

            else:
                print('connection established\n{}'.format(db_version[0]))

        return cls._instance

    def __init__(self):
        self.connection = self._instance.connection
        self.cursor = self._instance.cursor

    def insert_query(self, user_id, lat, lon, uname, fname, lname):
        post_query = f"SELECT latitude, longitude FROM users WHERE user_id={user_id} ORDER BY last_time DESC LIMIT 1"
        self.cursor.execute(post_query)
        result = self.cursor.fetchall()
        if result == [] or Point(result[0][0], result[0][1]).distance(Point(lat, lon)) > 0.005:
            postgres_insert_query = """ 
            INSERT INTO users (user_id, last_time, latitude, longitude, username, first_name, last_name) 
            VALUES (%s,NOW(),%s,%s,%s,%s,%s)    
            """
            record_to_insert = (user_id, lat, lon, uname, fname, lname)
            try:
                self.cursor.execute(postgres_insert_query, record_to_insert)
                self.connection.commit()
                count = self.cursor.rowcount
                print(count, "Record inserted successfully into users table")
            except (Exception, psycopg2.Error) as error:
                print("Failed to insert record into users table", error)
                self.connection.rollback()
                return None

    def select_query(self, user_id):
        try:
            self.cursor.execute(f"SELECT * FROM users WHERE user_id={user_id} ORDER BY last_time DESC LIMIT 1")
            if self.cursor.rowcount == 0:
                return None
            keys = [desc[0] for desc in self.cursor.description]
            result = self.cursor.fetchone()
            result = dict(zip(keys, result))
        except (Exception, psycopg2.Error) as error:
            print('Error executing query error: ', error)
            return None
        else:
            return result

    def __del__(self):
        self.connection.close()
        self.cursor.close()
