import mysql.connector
from mysql.connector.constants import ClientFlag
from mysql.connector import errorcode
from itertools import chain
import random


class DatabaseConnection:
    """
    Klasa umożliwiająca połączenie z bazą danych
    po całkowitej inicjalizacji gry powinna posiadać atrybuty
    _cnxn -> obiekt reprezentujący obiekt połączenia z bazą danych
    _ownership -> atrybut ocieniajacy czy gracz to host czy klient gry
    """

    def __init__(self):
        try:
            config = {
                'user': 'root',
                'password': 'j86qjNoFyhveen',
                'host': '34.107.75.136',
                'database': 'pzsp104',
                'client_flags': [ClientFlag.SSL],
                'ssl_ca': 'ssl/server-ca.pem',
                'ssl_cert': 'ssl/client-cert.pem',
                'ssl_key': 'ssl/client-key.pem',
                'autocommit': True
            }
            self._cnxn = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def select_empty_rooms(self):
        cursor = self._cnxn.cursor()
        query = "SELECT Room_no FROM rooms WHERE Room_no NOT IN (SELECT Room_no FROM game);"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def select_started_rooms(self):
        cursor = self._cnxn.cursor()
        query = "SELECT Room_no FROM game WHERE playing = 0"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def check_if_still_empty(self, room_no):
        # nie wiem czy implementujemy odswieżanie listy pokoi dlatego
        # ta funkcja będzie pełnić rolę zabezpieczenia sprawdzającego czy pokój jest wciąż pusty
        cursor = self._cnxn.cursor()
        query = "SELECT * FROM game WHERE Room_no = %s"
        data = (room_no,)
        cursor.execute(query, data)
        cursor.fetchall()
        rows = cursor.rowcount
        cursor.close()
        if rows == 0:
            return 1
        else:
            return 0

    def check_if_still_hosted(self, room_no):
        # funkcja sprawdza czy pokój dalej istnieje i gra się nie zaczęła
        cursor = self._cnxn.cursor()
        query = "SELECT * FROM game WHERE Room_no = %s AND playing = 0"
        data = (room_no,)
        cursor.execute(query, data)
        cursor.fetchall()
        rows = cursor.rowcount
        cursor.close()
        if rows == 1:
            return True
        return False

    def get_room_no(self):
        return self._room_no

    def set_room_no(self, number):
        self._room_no = number

    def get_ownership(self):
        return self._ownership

    def set_ownership(self, number):
        self._ownership = number

    def starting_new_game(self):
        cursor = self._cnxn.cursor()
        query = ("INSERT INTO game "
                 "(Room_no)"
                 "VALUES (%s)")
        data = (self.get_room_no(),)
        cursor.execute(query, data)
        self._cnxn.commit()
        cursor.close()

    def delete_game_record(self):
        cursor = self._cnxn.cursor()
        query = ("DELETE FROM game "
                 "WHERE Room_no = %s")
        data = (self.get_room_no(),)
        cursor.execute(query, data)
        self._cnxn.commit()
        cursor.close()

    @staticmethod
    def get_randomized_values():
        cards = [*range(1, 25)]
        list_of_cards = []
        for each in range(10):
            number = random.choice(cards)
            cards.remove(number)
            list_of_cards.append([number, 1])
        for each in range(10):
            number = random.choice(cards)
            cards.remove(number)
            list_of_cards.append([number, 2])
        for each in range(2):
            number = random.choice(cards)
            cards.remove(number)
            list_of_cards.append([number, 3])
        for each in cards:
            list_of_cards.append([each, 4])
        return list_of_cards

    def tuple_of_arguments_for_deck(self):
        # Funkcja zmienia listę zawierającą wylosowane kombinacje
        # w krotkę zawierającą argumenty do utworzenia rekordu
        list_of_cards = self.get_randomized_values()
        list_of_values = []
        room_no = self.get_room_no()
        for list_of_definitions in list_of_cards:
            for value in list_of_definitions:
                list_of_values.append(value)
        res = list(chain(*[list_of_values[i: i + 2] + [room_no]
                           if len(list_of_values[i: i + 2]) == 2
                           else list_of_values[i: i + 2]
                           for i in range(0, len(list_of_values), 2)]))
        return tuple(res)

    def count_points(self, value):
        """
        Metoda przyjmuje jako argument kategorie do policzenia punktów
        Sensowne wykorzystanie tylko dla 
        1 -> karty na rece gracza 1
        2 -> karty na rece gracza 2
        5 -> lewa gracza 1 
        6 -> lewa gracza 2
        7 -> wartosc ostatniej zagranej karty gracza 1
        8 -> wartosc ostatniej zagranej karty gracza 2
        """
        card_points = [11, 4, 3, 2, 10, 0]
        pik = 0
        trefl = 0
        karo = 0
        kier = 0
        points = 0
        cards = self.select_cards(value)
        for card in cards:
            if value not in [7, 8]:
                if card[0] == 5 or card[0] == 9:
                    pik = pik + 1
                    if pik == 2:
                        points = points + 40
                if card[0] == 8 or card[0] == 12:
                    trefl = trefl + 1
                    if trefl == 2:
                        points = points + 60
                if card[0] == 7 or card[0] == 11:
                    karo = karo + 1
                    if karo == 2:
                        points = points + 80
                if card[0] == 6 or card[0] == 10:
                    kier = kier + 1
                    if kier == 2:
                        points = points + 100
            id_minus_one = card[0] - 1
            points = points + card_points[int(id_minus_one / 4)]
        return points

    def create_deck(self):
        cursor = self._cnxn.cursor()
        deck = self.tuple_of_arguments_for_deck()
        query = ("INSERT INTO deck"
                 "(card_id, card_owner, room_id) "
                 "VALUES (%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s),"
                 "(%s,%s,%s)")
        cursor.execute(query, deck)
        self._cnxn.commit()
        cursor.close()

    def delete_current_deck(self):
        cursor = self._cnxn.cursor()
        query = "DELETE FROM deck WHERE room_id = %s"
        data = (self.get_room_no(),)
        cursor.execute(query, data)
        self._cnxn.commit()
        cursor.close()

    def select_cards(self, number):
        cursor = self._cnxn.cursor()
        query = "SELECT card_id FROM deck WHERE room_id = %s AND card_owner = %s"
        cursor.execute(query, (self.get_room_no(), number))
        result = cursor.fetchall()
        cursor.close()
        return result

    def reset_auction(self):
        cursor = self._cnxn.cursor()
        query = "UPDATE auction SET points_P1 = 100, points_P2 = 100 WHERE Room_no = %s"
        data = (self.get_room_no(),)
        cursor.execute(query, data)
        self._cnxn.commit()
        cursor.close()

    def update_auction(self, amount):
        cursor = self._cnxn.cursor()
        if self.get_ownership() == 1:
            query = "UPDATE auction SET points_P1 = %s WHERE Room_no = %s"
        else:
            query = "UPDATE auction SET points_P2 = %s WHERE Room_no = %s"
        data = (amount, self.get_room_no())
        cursor.execute(query, data)
        self._cnxn.commit()
        cursor.close()

    def return_your_auction_points(self):
        cursor = self._cnxn.cursor()
        if self.get_ownership() == 1:
            query = "SELECT points_P1 FROM auction WHERE Room_no = %s"
        else:
            query = "SELECT points_P2 FROM auction WHERE Room_no = %s"
        data = (self.get_room_no(),)
        cursor.execute(query, data)
        result = cursor.fetchall()
        cursor.close()
        return result[0][0]

    def return_value_of_auction(self):
        cursor = self._cnxn.cursor()
        query = "SELECT points_P1, points_P2 FROM auction WHERE Room_no = %s"
        data = (self.get_room_no(),)
        cursor.execute(query, data)
        result = cursor.fetchall()
        cursor.close()
        return result

    def set_game_info(self, which_column, values):
        """
        which_column określa które kolumny będziemy zmieniać:
        1 - kolor granych kart
        2 - numer rundy
        3 - który gracz aktualnie gra
        4 - id ostatniej zagranej karty
        5 - punkty graczy
        6 - zwycięzca aukcji
        UWAGA! jeżeli which_column == 5 to values musi zostać przedstawione w postaci
        encji zawierającej zdobyte punkty gracza pierwszego oraz drugiego
        """
        cursor = self._cnxn.cursor()
        data = (values, self.get_room_no())
        if which_column == 1:
            query = "UPDATE game SET ID_colour = %s WHERE Room_no = %s"
        elif which_column == 2:
            query = "UPDATE game SET round = %s WHERE Room_no = %s"
        elif which_column == 3:
            query = ("UPDATE game"
                     " SET playing = %s"
                     " WHERE Room_no = %s")
        elif which_column == 4:
            query = "UPDATE game SET card_id = %s WHERE Room_no = %s"
        elif which_column == 5:
            query = "UPDATE game SET P_1 = %s , P_2= %s WHERE Room_no = %s"
            data = (values[0], values[1], self.get_room_no())
        elif which_column == 6:
            query = "UPDATE game SET running_game = %s WHERE Room_no = %s"
        else:
            cursor.close()
            raise ValueError("Wartość dla which_column powinna być w zakresie <1;5>")
        cursor.execute(query, data)
        self._cnxn.commit()
        cursor.close()

    def get_game_info(self, which_column):
        """
        which_column określa które informacje chcemy pobrać:
        1 - kolor granych kart
        2 - numer rundy
        3 - który gracz aktualnie gra
        4 - id ostatniej zagranej karty
        5 - punkty graczy
        6 - "grający" - zwycięzca licytacji
        """
        cursor = self._cnxn.cursor()
        data = (self.get_room_no(),)
        if which_column == 1:
            query = "SELECT ID_colour FROM game WHERE Room_no = %s"
        elif which_column == 2:
            query = "SELECT round FROM game WHERE Room_no = %s"
        elif which_column == 3:
            query = "SELECT playing FROM game WHERE Room_no = %s"
        elif which_column == 4:
            query = "SELECT card_id FROM game WHERE Room_no = %s"
        elif which_column == 5:
            query = "SELECT P_1, P_2 FROM game WHERE Room_no = %s"
        elif which_column == 6:
            query = "SELECT running_game FROM game where Room_no = %s"
        else:
            cursor.close()
            raise ValueError("Wartość dla which_column powinna być w zakresie <1;5>")
        cursor.execute(query, data)
        result = cursor.fetchall()
        cursor.close()
        return result

    def change_card_owner(self, new_owner, card_id):
        """
        Zmienna new_owner odpowiada nowej przynależności karty:
        1 = Gracz pierwszy - Host
        2 = Gracz drugi
        3 = Musik pierwszy
        4 = Musik drugi
        5 = Lewa gracza 1
        6 = Lewa gracza 2
        7 = Ostatnio zagrana karta gracza 1
        8 = Ostatnio zagrana karta gracza 2
        """
        cursor = self._cnxn.cursor()
        query = ("UPDATE deck SET card_owner = %s"
                 " WHERE room_id = %s AND card_id = %s")
        data = (new_owner, self.get_room_no(), card_id)
        cursor.execute(query, data)
        self._cnxn.commit()
        cursor.close()

    def look_for_winner(self):
        """
        0 - zwrócona wartość oznacza brak zwycięzcy
        1 - zwycięzcą jest gracz 1
        2 - zwycięzcą jest gracz 2
        3 - remis, brak zwycięzcy
        """
        points = self.get_game_info(5)[0]
        if max(points) >= 1000:
            if points[0] == points[1]:
                return 3
            if min(points) >= 1000:
                x = self.get_game_info(6)
                return x[0]
            if points[0] > points[1]:
                return 1
            else:
                return 2
        return False

    def close_connection(self):
        self._cnxn.close()
