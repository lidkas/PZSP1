from database_connection import DatabaseConnection
import pygame
from buttons import Button
from cards import Card
from player import Player

from device_connection import ArduinoConnection
from configuration import color_model_path, value_model_path
# from serial import SerialException
# import tensorflow as tf
# from scanner import receive_and_guess

# indeksy wykorzystywane przez rozpoznawanie kart
scores = {'9': 0, 'J': 2, 'Q': 3, 'K': 4, '10': 10, 'A': 11}
colors = {'S': 1, 'H': 2, 'D': 4, 'C': 3}

# po co to tutaj deklarować???
color_model = None
value_model = None

# inicjalizacja obiektów klasy player, połączenia z bazą danych ?'game'?
player1 = Player()
player2 = Player()
game = DatabaseConnection()

# generowanie listy pokoi pustych i z graczami
list_of_empty_rooms = game.select_empty_rooms()
list_of_hosted_rooms = game.select_started_rooms()

# flagi używane GLOBALNIE i modyfikowane prze wszystkie funkcje xd
running = True
round_ = 1
start_game = False
use_device = None
ard_conn = None
has_passed = False

# inicjalizacja pygame, ustawienia wyświetlanych napisów
pygame.init()
pygame.display.set_caption("Tysiąc")
icon = pygame.image.load('images_of_cards/honor_spade.jpg')
czcionka = pygame.font.SysFont("comicsans", 30)
text_your_turn = "Teraz twoja kolej"
text_opponent_turn = "Teraz gra przeciwnik"
text_musik = 'Wybierz musik'
text_remove_card = 'Usun dwie swoje karty'
text_waiting_for_player = "Czekamy na drugiego gracza"
text_waiting_for_player_auction = "Drugi gracz licytuje"
text_device_choice = 'Czy używasz urządzenia do rozdawania kart?'
text_no_device = 'Nie wykryto urządzenia. Podłącz i spróbuj ponownie lub wybierz grę bez niego.'
text_render_player_one_turn = czcionka.render(text_your_turn, True, (0, 0, 0))
text_render_player_two_turn = czcionka.render(text_opponent_turn, True, (0, 0, 0))
text_render_musik = czcionka.render(text_musik, True, (0, 0, 0))
text_render_remove_card = czcionka.render(text_remove_card, True, (0, 0, 0))
text_render_waiting_for_player = czcionka.render(text_waiting_for_player, True, (0, 0, 0))
text_render_waiting_for_player_auction = czcionka.render(text_waiting_for_player_auction, True, (0, 0, 0))
pygame.display.set_icon(icon)
screen = pygame.display.set_mode([1024, 768])

bg_green = (0, 122, 30)
screen.fill(bg_green)
list_of_buttons = []


def create_menu(_mouse_x, _mouse_y):
    list_of_empty_buttons = []
    list_of_hosted_buttons = []
    list_of_empty_buttons, list_of_hosted_buttons = draw_room_buttons(list_of_empty_buttons, list_of_hosted_buttons)
    for button in list_of_empty_buttons:
        if button.is_over(_mouse_x, _mouse_y):
            room_number = int(button.text.split()[2])
            empty_room(room_number)
            return True
    for button in list_of_hosted_buttons:
        if button.is_over(_mouse_x, _mouse_y):
            room_number = int(button.text.split()[2])
            hosted_room(room_number)
            game.set_game_info(3, 3)
            return True
    return False


def draw_room_buttons(list_of_empty_buttons, list_of_hosted_buttons):
    screen.fill(bg_green)
    _list_of_empty_rooms = game.select_empty_rooms()
    _list_of_hosted_rooms = game.select_started_rooms()
    y = -90
    for room in _list_of_empty_rooms:
        room_text = f'Pokój nr {str(room[0])}'
        y += 100
        button = Button((255, 0, 0), 300, y, 100, 60, room_text)
        button.draw(screen)
        list_of_empty_buttons.append(button)
    y = -90
    for room in _list_of_hosted_rooms:
        room_text = f'Pokój nr {str(room[0])}'
        y += 100
        button = Button((255, 255, 0), 500, y, 100, 60, room_text)
        button.draw(screen)
        list_of_hosted_buttons.append(button)
    return list_of_empty_buttons, list_of_hosted_buttons

"""
"""
# def tensorflow_load_models():
#     with tf.device('/CPU:0'):
#         _color_model = tf.keras.models.load_model(color_model_path)
#         _value_model = tf.keras.models.load_model(value_model_path)

#     return _color_model, _value_model


def device_choice_screen(_mouse_x, _mouse_y):
    """Obsługa ekranu z pytaniem czy gra się z urządzeniem do rozdawania kart"""
    _ard_conn = None
    button_yes = Button((0, 255, 255), 375, 300, 100, 60, 'Tak')
    button_no = Button((255, 0, 0), 575, 300, 100, 60, 'Nie')
    if button_yes.is_over(_mouse_x, _mouse_y):
        screen.fill(bg_green)
        # try:
        #     _ard_conn = ArduinoConnection('COM2')
        #     _color_model, _value_model = tensorflow_load_models()
        #     return True, _ard_conn
        # except SerialException:
        #     add_text(text_no_device, 300, 500)
    if button_no.is_over(_mouse_x, _mouse_y):
        screen.fill(bg_green)
        return False, _ard_conn
    add_text(text_device_choice, 300, 150)
    button_yes.draw(screen)
    button_no.draw(screen)
    return None, _ard_conn

def auction():
    global has_passed
    if game.get_game_info(6)[0][0] == game.get_ownership() and not has_passed :
        _my_bid = game.return_your_auction_points()
        if game.get_ownership() == 1:
            _player_to_send = player1
        else:
            _player_to_send = player2
        _taken_action, _my_bid = draw_auction(mouse_x, mouse_y, _player_to_send, _my_bid)
        if _taken_action == "bid":  # gracz zalicytował
            game.set_game_info(6, 3 - game.get_ownership())
            game.update_auction(_my_bid)
            if game.get_game_info(3)[0][0] == 4:
                game.set_game_info(3,5)
        elif _taken_action == "pass":   # gracz spasował
            has_passed = True
            game.set_game_info(6, 3-game.get_ownership())
            game.set_game_info(3, who_playing + 1)
            if game.get_game_info(3)[0][0] == 5:
                points = game.return_value_of_auction()
                if points[0][0] > points[0][1]:
                    auc_winner = 1
                else:
                    auc_winner = 2
                game.set_game_info(6, auc_winner)
                game.set_game_info(3, auc_winner)
                game.reset_auction()
    else:
        screen.fill((230, 122, 30))
        screen.blit(text_render_waiting_for_player, (500, 300))


def add_text(text, x, y):
    mrender = czcionka.render(text, True, (0, 0, 0))
    screen.blit(mrender, (x, y))


def udpate_my_bid(bid_value):
    """Zmiana wartości do zalicytowania na ekranie licytacji"""
    button_my_bid = Button((0, 122, 30), 210, 350, 60, 60, str(bid_value))
    button_my_bid.draw(screen)


def draw_auction(_mouse_x, _mouse_y, player_me, my_curr_bid):
    """Obsługa ekranu licytacji"""
    curr_bid = max(game.return_value_of_auction()[0])
    max_bid = max(int(game.count_points(game.get_ownership())/10)*10,100)
    screen.fill((0, 122, 30))
    add_text('LICYTACJA', 450, 125)
    add_text(f'Obecnie wylicytowano: {curr_bid}', 100, 300)
    button_add = Button((127, 127, 127), 300, 350, 60, 60, '+')
    button_subs = Button((127, 127, 127), 100, 350, 60, 60, '-')

    if button_add.is_over(_mouse_x, _mouse_y):
        my_curr_bid += 10
    if button_subs.is_over(_mouse_x, _mouse_y):
        my_curr_bid -= 10

    my_curr_bid = min(max(100, curr_bid, my_curr_bid), max_bid)

    udpate_my_bid(my_curr_bid)
    button_add.draw(screen)
    button_subs.draw(screen)

    _taken_action = 'wait'
    if  max_bid > curr_bid:
        button_bid = Button((127, 127, 127), 500, 350, 120, 60, 'Zalicytuj')
        if button_bid.is_over(_mouse_x, _mouse_y):
            _taken_action = 'bid'
        button_bid.draw(screen)
    button_pass = Button((127, 127, 127), 500, 450, 120, 60, 'Pass')
    if button_pass.is_over(_mouse_x, _mouse_y):
        _taken_action = 'pass'
    button_pass.draw(screen)

    player_me.player_cards(screen, False)

    return _taken_action, my_curr_bid


def select_card(player, _mouse_x=None, _mouse_y=None):
    """Wybranie karty, ktora gracz chce zagrac"""
    if _mouse_x:
        for card in player.cards:
            lower_x = card.positionx
            lower_y = card.positiony
            if lower_x < _mouse_x < lower_x + 100 and lower_y < _mouse_y < lower_y + 100:
                player.selected_card = card


def play_selected_card(_screen, player):
    """Wyswietlenie zagrywanej karty na ekran"""
    card = Card(player.selected_card.card_id, 400, 350)
    card.image_of_card(_screen)


def play_oponnent_card(_screen, player):
    card = Card(player.selected_card.card_id, 400, 250)
    card.image_of_card(_screen)


def check_selected_card(_player1, _player2):
    """Sprawdzenie czy zagrywana karta jest tego samego koloru co juz rzucona"""
    if _player1.selected_card and _player2.selected_card:
        color = _player1.selected_card.suit
        if _player2.selected_card.suit != color and check_color_card(_player2, color):
            _player2.selected_card = None


def check_color_card(player, color):
    """sprawdzenie czy gracz ma zadany kolor"""
    for card in player.cards:
        if card.suit == color:
            return True


def change_color_for_id(suit):
    """zamiana koloru na id koloru"""
    for color in colors.keys():
        if color == suit:
            suit = colors[suit]
    return suit


"""
# not yet implemented
def select_musik(player, mouse_x=None, mouse_y=None):
    # Wybranie musika przez gracza, musik o rozmiarze 100x100
    if mouse_x:
        for card in list_of_musik1:
            lower_x, upper_x = (card.positionx, card.positionx + 100)
            lower_y, upper_y = (card.positiony, card.positiony + 100)
            if lower_x < mouse_x < upper_x and lower_y < mouse_y < upper_y:
                    player.selected_musik = card
        for card in list_of_musik2:
            lower_x, upper_x = (card.positionx, card.positionx + 100)
            lower_y, upper_y = (card.positiony, card.positiony + 100)
            if lower_x < mouse_x < upper_x and lower_y < mouse_y < upper_y:
                    player.selected_musik = card


def add_musik(player):
    if player == player1:
        x = 1
    if player == player2:
        x = 2
        x = 2
    if player.selected_musik in list_of_musik1:
        game.change_card_owner(x, list_of_musik1[0].card_id)
        player.append_card(list_of_musik1[0])
        game.change_card_owner(x, list_of_musik1[1].card_id)
        player.append_card(list_of_musik1[1])
    if player.selected_musik in list_of_musik2:
        game.change_card_owner(x, list_of_musik2[0].card_id)
        player.append_card(list_of_musik2[0])
        game.change_card_owner(x, list_of_musik2[1].card_id)
        player.append_card(list_of_musik2[1])


def show_musik(screen):
    x = 150
    for card in list_of_musik1:
        x += 25
        card.positionx = x
        card.positiony = 250
        card.image_of_card(screen)
    x = 600
    for card in list_of_musik2:
        x += 25
        card.positionx = x
        card.positiony = 250
        card.image_of_card(screen)
"""

# przekazujemy globale jako parametry funkcji
def player_scores(_screen, _player1, _player2):
    """Wyswietlanie punktow gracza"""
    _player1.score, _player2.score = game.get_game_info(5)[0]
    score_player_one = f"Twoje punkty:{_player1.score}"
    score_player_two = f"Punkty przeciwnika:{_player2.score}"
    text_render_player_one_score = czcionka.render(score_player_one, True, (0, 0, 0))
    text_render_player_two_score = czcionka.render(score_player_two, True, (0, 0, 0))
    _screen.blit(text_render_player_one_score, (50, 600))
    _screen.blit(text_render_player_two_score, (50, 100))


def calculate_points(card):
    """Liczenie punktow za jedna karte"""
    for value in scores.keys():
        if value == card.value:
            card_score = scores[card.value]
    return card_score


def choose_winner(_player1, _player2):
    """Wyłonienie zwyciezcy danej rundy"""
    round_winner = None
    if _player1.selected_card and _player2.selected_card:
        pygame.time.delay(20)
        if game.get_game_info(3)[0][0] == 2:
            color1 = _player1.selected_card.suit
            color2 = _player2.selected_card.suit
        else:
            color1 = _player2.selected_card.suit
            color2 = _player1.selected_card.suit
        if calculate_points(_player1.selected_card) > calculate_points(_player2.selected_card) and color1 == color2:
            round_winner = _player1
        elif calculate_points(_player1.selected_card) < calculate_points(_player2.selected_card) and color1 == color2:
            round_winner = _player2
        elif color1 != color2:
            if game.get_game_info(3)[0][0] == 2:
                round_winner = _player2
            else:
                round_winner = _player1
        round_winner.score += calculate_points(_player1.selected_card) + calculate_points(_player2.selected_card)
        _player1.selected_card, _player2.selected_card = None, None
        game.set_game_info(1, None)
        game.set_game_info(4, None)
    return round_winner


def empty_room(room_number):
    game.set_room_no(room_number)
    game.set_ownership(1)
    game.starting_new_game()
    game.create_deck()
    rooms_common()

def hosted_room(room_number):
    game.set_room_no(room_number)
    # set_ownership rozpoznaje kto gra?
    game.set_ownership(2)
    rooms_common()

# reduce empty_room and hosted_room
def rooms_common():
    for card in game.select_cards(1):
        player1.cards.append(Card(card[0]))
    for card in game.select_cards(2):
        player2.cards.append(Card(card[0]))

# czy przeciwnik zagrał karte, zwraca ostatnią karte przeciwnika
def check_if_oponnent_card(player):
    # ostatnio zagrana karta
    card_id = game.get_game_info(4)[0][0]
    # jeżeli była zagrana
    if card_id:
        player.selected_card = Card(card_id)
        # skanuj ręke
        for card in player.cards:
            # xdddd
            if card.card_id == card_id:
                player.remove_from_player(card)


# !!!! missing dispaly score
def set_game_info(player, turn):
    game.set_game_info(1, change_color_for_id(player.selected_card.suit))
    game.set_game_info(3, turn)
    game.set_game_info(4, player.selected_card.card_id)


def set_who_start_round(winner):
    if winner == player1:
        game.set_game_info(3, 1)
    else:
        game.set_game_info(3, 2)

# god level set method, korzysta z globala
def set_round(_round):
    game.set_game_info(2, _round)


def get_player_turn():
    return game.get_game_info(3)[0][0]


def get_round():
    return game.get_game_info(2)[0][0]


# przekazujemy globalne wartości jako parametr
def end_round(_player1, _player2):
    winner = choose_winner(_player1, _player2)
    if winner:
        set_who_start_round(winner)

"""
# game can never end
def end_game():
    not implemented in the main loop yet
    if look_for_winner() == 3:
        text_endgame = 'draw'
    else:
        text_endgame = 'player {} wins'.format(look_for_winner())
    czcionka = pygame.font.SysFont("comicsans", 70)
    text_render_engame = czcionka.render(text_endgame, True, (0, 0, 0))
    screen.fill(bg_green)
    screen.blit(text_render_endgame, (500, 300))
"""


while running:
    # print(game.select_started_rooms())
    mouse_x, mouse_y = None, None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            # dodać tutaj flage dla drugiego gracza o zakończeniu gry i poczekać na drugą zwrotną
            game.delete_game_record()
            game.delete_current_deck()
            game.reset_auction()
            running = False
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
    # możliwoć grania z robotem
    if use_device is None:
        use_device, ard_conn = device_choice_screen(mouse_x, mouse_y)
    # start gry if device not none?, co z grającymi bez bota?
    if not start_game and use_device is not None:
        screen.fill(bg_green)
        start_game = create_menu(mouse_x, mouse_y)
    if start_game and use_device is not None:
        who_playing = game.get_game_info(3)[0][0]
        if who_playing == 0:
            screen.fill((230, 122, 30))
            screen.blit(text_render_waiting_for_player, (500, 300))
        # markery 3, 4 oznaczają licytacje
        if 3 <= who_playing < 5:
            auction()
        # właściwa runda
        if who_playing == 1 or who_playing == 2:
            screen.fill((0, 122, 30))




            if game.get_ownership() == 1:
                if get_player_turn() == 1:
                    screen.blit(text_render_player_one_turn, (350, 500))
                    check_if_oponnent_card(player2)
                    select_card(player1, mouse_x, mouse_y)
                    check_selected_card(player2, player1)
                    player1.remove_from_player(player1.selected_card)
                    if player1.selected_card:
                        game.change_card_owner(5, player1.selected_card.card_id)
                        set_game_info(player1, 2)
                if player2.selected_card:
                    play_oponnent_card(screen, player2)
                if player1.selected_card:
                    play_selected_card(screen, player1)
                if get_player_turn() == 2:
                    screen.blit(text_render_player_two_turn, (350, 100))
                player1.player_cards(screen, True)
                player2.player_cards(screen, False)
            if game.get_ownership() == 2:
                if get_player_turn() == 2:
                    screen.blit(text_render_player_one_turn, (350, 500))
                    check_if_oponnent_card(player1)
                    select_card(player2, mouse_x, mouse_y)
                    check_selected_card(player1, player2)
                    player2.remove_from_player(player2.selected_card)
                    if player2.selected_card:
                        game.change_card_owner(6, player2.selected_card.card_id)
                        set_game_info(player2, 1)
                if player1.selected_card:
                    play_oponnent_card(screen, player1)
                if player2.selected_card:
                    play_selected_card(screen, player2)
                if get_player_turn() == 1:
                    screen.blit(text_render_player_two_turn, (350, 100))
                player1.player_cards(screen, False)
                player2.player_cards(screen, True)


            player_scores(screen, player1, player2)
            if player1.selected_card and player2.selected_card:
                end_round(player1, player2)





    pygame.display.update()

if use_device:
    ard_conn.ser.close()
game.close_connection()

