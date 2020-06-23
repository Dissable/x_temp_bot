#для работы с базой данных
import datetime
import psycopg2

class Postgres(object):
    _instance = None


    def get_connec():
        try:
            with open('E:\\Agnbad\\Sunny\\Pyton\\HSE\\Homework\\x-temp-bot2\\dbconn.txt') as f:
                dbconn=f.read().split('\n')
                connec=psycopg2.connect(dbname=dbconn[0], user=dbconn[1], password=dbconn[2], host=dbconn[3])
            local_start=True
            print('local_start='+str(local_start))
            return connec
        except:
            DATABASE_URL = os.environ['DATABASE_URL']
            connec = psycopg2.connect(DATABASE_URL, sslmode='require')
            local_start=False
            print('local_start='+str(local_start))
            return connec


    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            try:
                print('connecting to PostgreSQL database...')
                #connection = Postgres._instance.connection = psycopg2.connect(os.environ['DATABASE_URL'],
                #                                                              sslmode='require')
                cls._instance.connection = get_connec()
                cls._instance.cursor = cls._instance.connection.cursor()
                cls._instance.cursor.execute('SELECT VERSION()')
                db_version = cls._instance.cursor.fetchone()

            except Exception as error:
                print('Error: connection not established {}'.format(error))
                cls._instance = None

            else:
                print('connection established\n{}'.format(db_version[0]))

        return cls._instance


    def __init__(self):
        self.connection = self._instance.connection
        self.cursor = self._instance.cursor


    def insertt (self, TEMP, MUSER_ID: int, DATA=datetime.datetime.today().strftime('%Y-%m-%d')):
        sql = f'''INSERT INTO "TBTEMPERATURE" ("DATA", "MUSER_ID", "TEMP") VALUEs ('{DATA}', {MUSER_ID}, {TEMP}) ON CONFLICT ("DATA", "MUSER_ID") DO UPDATE SET "TEMP"={TEMP} '''
        print(sql)
        self.cursor.execute(sql)
        self.connection.commit()
        print('temp insert commit')

    #это старая функция - в неё подглядываем и пишем функцию выше    
    def db_insert_temp(TEMP, MUSER_ID: int, DATA=datetime.datetime.today().strftime('%Y-%m-%d')):
        with closing(connec) as conn:
            with conn.cursor() as cursor:
                sql = f'''INSERT INTO "TBTEMPERATURE" ("DATA", "MUSER_ID", "TEMP") VALUEs ('{DATA}', {MUSER_ID}, {TEMP}) ON CONFLICT ("DATA", "MUSER_ID") DO UPDATE SET "TEMP"={TEMP} '''
                print(sql)
                cursor.execute(sql)
            conn.commit()
            print('done')
