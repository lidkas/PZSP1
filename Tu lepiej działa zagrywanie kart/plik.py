import mysql.connector
from mysql.connector.constants import ClientFlag
from mysql.connector import errorcode


def database_edition():
    """
    tej funkcji lepiej nie wywoływać
    jej celem jest zmian struktury bazy danych jeżeli konieczna będzie jakaś zmiana
    """
    try:
        config = {
            'user': 'root',
            'password': 'j86qjNoFyhveen',
            'host': '34.107.75.136',
            'database': 'pzsp104',
            'client_flags': [ClientFlag.SSL],
            'ssl_ca': 'ssl/server-ca.pem',
            'ssl_cert': 'ssl/client-cert.pem',
            'ssl_key': 'ssl/client-key.pem'
        }
        cnxn = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = cnxn.cursor()
    query = "DELETE from game"
    cursor.execute(query)
    cnxn.commit()
    cursor.close()
    cnxn.close()


def database_see():
    """
    funkcja w obsłudze jest bardzo prosta,
    jeżeli chcesz dodać interesującą cię informację z bazy danych zeby sprawdzić czy dziala
    zmien zmienna query poniżej według wzoru
    SELECT [interesujące cie kolumny, gwiazdka zwraca wszystko]
    FROM [nazwa tabeli]
    WHERE [warunek po którym szukac np Room_no = 4 zwróci rekordy gdzie Room_no jest równe 4]
    """
    try:
        config = {
            'user': 'root',
            'password': 'j86qjNoFyhveen',
            'host': '34.107.75.136',
            'database': 'pzsp104',
            'client_flags': [ClientFlag.SSL],
            'ssl_ca': 'ssl/server-ca.pem',
            'ssl_cert': 'ssl/client-cert.pem',
            'ssl_key': 'ssl/client-key.pem'
        }
        cnxn = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    cursor = cnxn.cursor()
    query = "SELECT * FROM game WHERE Room_no = 4"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return result

# database_edition()
# x = database_see()

# for row in x:
# print(row)
