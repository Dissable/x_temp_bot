#для работы с базой данных
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

