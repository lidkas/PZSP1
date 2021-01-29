from database_connection import DatabaseConnection
import pygame
from buttons import Button
from cards import Card
from player import Player

from device_connection import ArduinoConnection
from configuration import color_model_path, value_model_path
from serial import SerialException
import tensorflow as tf


# wartości punktowe kart
scores = {'9': 0, 'J': 2, 'Q': 3, 'K': 4, '10': 10, 'A': 11}
colors = {'S': 1, 'H': 2, 'D': 4, 'C': 3}

# modele sieci po co to tutaj deklarować???
color_model = None
value_model = None

# inicjalizacja obiektów klasy player, połączenia z bazą danych ?'game'?
player1 = Player()
player2 = Player()
game = DatabaseConnection()

# generowanie listy pokoi pustych i z graczami
list_of_empty_rooms = game.select_empty_rooms()
list_of_hosted_rooms = game.select_started_rooms()

# generowanie pustych list z musikami
musik1 = []
musik2 = []

# flagi używane GLOBALNIE i modyfikowane prze wszystkie funkcje 
running = True
round_ = 1
start_game = False
device_set = False
ard_conn = None
has_passed = False
card_given = False
musik_received = False
musik_removed = False
removed = 0
swapped_objects = False

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
text_deal_choice = 'Czy chcesz rozdawać karty (po jednej) za pomocą urządzenia?'
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



def tensorflow_load_models():
    with tf.device('/CPU:0'):
        _color_model = tf.keras.models.load_model(color_model_path)
        _value_model = tf.keras.models.load_model(value_model_path)

    return _color_model, _value_model


def device_choice_screen(_mouse_x, _mouse_y, _ard_conn):
    """Obsługa ekranu z pytaniem czy gra się z urządzeniem do rozdawania kart"""
    deal_with_device = None
    use_device = None
    if _ard_conn is not None:
        use_device = True
    button_yes = Button((0, 255, 255), 375, 300, 100, 60, 'Tak')
    button_no = Button((255, 0, 0), 575, 300, 100, 60, 'Nie')
    button_yes_deal = Button((0, 255, 255), 375, 500, 100, 60, 'Tak')
    button_no_deal = Button((255, 0, 0), 575, 500, 100, 60, 'Nie')
    if button_yes_deal.is_over(_mouse_x, _mouse_y):
        deal_with_device = True
    if button_no_deal.is_over(_mouse_x, _mouse_y):
        deal_with_device = False
    if button_yes.is_over(_mouse_x, _mouse_y):
        screen.fill(bg_green)
        add_text(text_deal_choice, 200, 450)
        button_yes_deal.draw(screen)
        button_no_deal.draw(screen)
        try:
            _ard_conn = ArduinoConnection()
            models = tensorflow_load_models()
            return True, _ard_conn, models, deal_with_device
        except SerialException:
            add_text(text_no_device, 300, 500)
    if button_no.is_over(_mouse_x, _mouse_y):
        screen.fill(bg_green)
        return False, _ard_conn, None, False
    add_text(text_device_choice, 300, 150)
    button_yes.draw(screen)
    button_no.draw(screen)
    return use_device, _ard_conn, None, deal_with_device


def auction():
    global has_passed
    if game.get_game_info(6)[0][0] == game.get_ownership() and not has_passed:
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
                game.set_game_info(3, 5)
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
    if max_bid > curr_bid:
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


def select_card(player, mouse_pos):
    _mouse_x, _mouse_y = mouse_pos
    print(f'{_mouse_x, _mouse_y} to są współrzędne myszki')
    """Wybranie karty, ktora gracz chce zagrac"""
    if use_device:
        player.selected_card = Card(ard_conn.scan_card(player.cards, models))
    if _mouse_x is not None:
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


# musiki
def append_to_musik():
    x = 150
    list_1 = game.select_cards(3)
    list_2 = game.select_cards(4)
    for each in list_1:
        card = Card(each[0], x, 250)
        x += 50
        musik1.append(card)
    x = 550
    for each in list_2:
        card = Card(each[0], x, 250)
        x += 50
        musik2.append(card)

def show_musik():
    for card in [*musik1, *musik2]:
        card.image_of_card(screen)

def select_musik(mouse, player):
    # Wybranie musika przez gracza, musik o rozmiarze 100x100
    global musik_received
    mouse_x, mouse_y = mouse
    if mouse_x is not None:
        if 150 < mouse_x < 300 and 250 < mouse_y < 350:
            add_musik(player,1)
            musik_received = True
        elif 550 < mouse_x < 700 and 250 < mouse_y < 350:
            add_musik(player,2)
            musik_received = True


def add_musik(player, which_one):
    owner = game.get_ownership()
    if which_one == 1:
        for card in musik1:
            game.change_card_owner(owner, card.card_id)
            player.append_card(card)
    else:
        for card in musik2:
            game.change_card_owner(owner, card.card_id)
            player.append_card(card)

def receive_musik(mouse, player):
    show_musik()
    select_musik(mouse, player)


# usunięcie 2 kart z ręki
def select_card_to_remove(player, mouse):
    global removed
    x, y = mouse
    if mouse_x is not None:
        for card in player.cards:
            if card.positionx < x < card.positionx + 100 and card.positiony < y < card.positiony + 100:
                remove_from_hand(player, card)
                removed += 1


def remove_from_hand(player, card):
    player.cards.remove(card)
    game.change_card_owner(3,card.card_id)


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
    append_to_musik()
    for card in game.select_cards(1):
        player1.cards.append(Card(card[0]))
    for card in game.select_cards(2):
        player2.cards.append(Card(card[0]))


# czy przeciwnik zagrał karte, nic nie zwraca, usuwa karte z lokalnej ręki
def check_if_oponnent_card(player):
    # ostatnio zagrana karta
    card_id_db = game.get_game_info(4)[0][0]
    # jeżeli była zagrana
    if card_id_db:
        player.selected_card = Card(card_id_db)
        # skanuj ręke
        for card in player.cards:
            # xdddd
            if card.card_id == card_id_db:
                player.remove_from_player(card)


def set_game_info(player, turn):
    game.set_game_info(1, change_color_for_id(player.selected_card.suit))
    game.set_game_info(3, turn)
    game.set_game_info(4, player.selected_card.card_id)


def set_who_start_round(winner):
    if winner == player1:
        game.set_game_info(3, 1)
    else:
        game.set_game_info(3, 2)


# korzysta z globala
def set_round(_round):
    game.set_game_info(2, _round)


def get_player_turn():
    return game.get_game_info(3)[0][0]


def get_round():
    return game.get_game_info(2)[0][0]


# przekazujemy globalne obiekty jako parametr
def end_round(_player1, _player2):
    winner = choose_winner(_player1, _player2)
    if winner:
        set_who_start_round(winner)


# fumkcja w teorii zajmuje się przebiegiem rundy
def round_playthrough(player_me, opponent, mouse_pos):
    screen.blit(text_render_player_one_turn, (350, 500))
    check_if_oponnent_card(opponent)
    select_card(player_me, mouse_pos)
    check_selected_card(opponent, player_me)
    player_me.remove_from_player(player_me.selected_card)
    if player_me.selected_card:
        # 4 + game.get_ownership() // czyli 1 lub dwa, da nam to karte gracza 1 lub 2
        game.change_card_owner(4+game.get_ownership(), player_me.selected_card.card_id)
        game.set_game_info(3, 3 - game.get_ownership())


def next_deal():
    # wykasować stare karty graczy lokalnie 
    # wykasować stare karty graczy z bazy danych
    # od nowa:
        # musiki
        # licytacja
    # eh
    pass


# rozwiązanie sytuacji, kiedy tylko jednemu graczowi kończą się karty przez błąd synchronizacji
def is_any_hand_empty():
    if len(player1.cards) == 0 or len(player2.cards) == 0:
        return True
    return False


# koniec pracy programu
def terminate_game():
    global running
    pygame.quit()
    game.delete_game_record()
    game.delete_current_deck()
    game.reset_auction()
    running = False
    quit()


# GUI końca gry
def end_game(_mouse_x, _mouse_y):
    if game.look_for_winner() == 3:
        text_endgame = 'draw'
    else:
        text_endgame = 'player {} wins'.format(game.look_for_winner())
    czcionka = pygame.font.SysFont("comicsans", 70)
    text_render_endgame = czcionka.render(text_endgame, True, (0, 0, 0))
    screen.fill(bg_green)
    screen.blit(text_render_endgame, (500, 300))
    pygame.display.update
    close_button = Button((0, 255, 255), 375, 300, 100, 60, 'xkill')
    while running:
        if close_button.is_over(_mouse_x, _mouse_y):
            terminate_game()


# wymusić koniec rundy, jeżeli ktokolwiek lokalnie ma 0 kart
while running:
    # print(game.select_started_rooms())
    mouse_x, mouse_y = None, None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
    # możliwoć grania z robotem
    if not device_set:
        use_device, ard_conn, models, deal_with_device = device_choice_screen(mouse_x, mouse_y, ard_conn)
        device_set = use_device is not None and deal_with_device is not None
    # use_device set False
    if not start_game and device_set:
        screen.fill(bg_green)
        start_game = create_menu(mouse_x, mouse_y)
    if start_game and device_set:
        who_playing = game.get_game_info(3)[0][0]
        if who_playing == 0:
            screen.fill((230, 122, 30))
            screen.blit(text_render_waiting_for_player, (500, 300))
        # markery 3, 4 oznaczają licytacje
        if 3 <= who_playing < 5:
            if not card_given and deal_with_device:
                my_deck = game.select_cards(game.get_ownership())[0]
                ard_conn.deal_cards(my_deck, models)
                card_given = True
                # wydajesz karty graczom
            auction()

        # właściwa runda
        if who_playing == 1 or who_playing == 2:
            screen.fill((0, 122, 30))
            auc_winner = game.get_game_info(6)[0][0]
            
            # ustalamy karty po stronie klienta i karty przeciwnika dla przejrzystosci
            if game.get_ownership() == 2 and not swapped_objects:
                temp = player1
                player1 = player2
                player2 = temp
                swapped_objects = True
                del temp

            # Otrzymywanie musików
            if game.get_ownership() == auc_winner and not musik_received:
                player1.player_cards(screen, True)
                receive_musik((mouse_x, mouse_y),player1)
            elif game.get_ownership() == auc_winner and not musik_removed:
                if removed < 2:
                    player1.player_cards(screen, True)
                    select_card_to_remove(player1, (mouse_x, mouse_y))
                else:
                    musik_removed = True
            else:
                
                # jeżeli tura w db zgadza się z twoim numerem odpalana jest funkcja gry
                if who_playing == game.get_ownership():
                    screen.blit(text_render_player_one_turn, (350, 500))
                    check_if_oponnent_card(player2)
                    select_card(player1, (mouse_x, mouse_y))
                    check_selected_card(player2, player1)
                    player1.remove_from_player(player1.selected_card)
                    if player1.selected_card:
                        # 4 + game.get_ownership() // czyli 1 lub dwa, da nam to karte gracza 1 lub 2
                        game.change_card_owner(4+game.get_ownership(), player1.selected_card.card_id)
                        game.set_game_info(3, 3 - game.get_ownership())
                
                # wyświetlanie kart
                if player2.selected_card:
                    play_oponnent_card(screen, player2)
                if player1.selected_card:
                    play_selected_card(screen, player1)

                if get_player_turn() == (3 - game.get_ownership()):
                    screen.blit(text_render_player_two_turn, (350, 100))

                player1.player_cards(screen, True)
                player2.player_cards(screen, False)
            player_scores(screen, player1, player2)
            if player1.selected_card is not None and player2.selected_card is not None:
                end_round(player1, player2)


            if is_any_hand_empty:
                next_deal()
        
        # zakończenie gry, jeżeli ktoś uzyskał 1000 pkt
        if game.look_for_winner():
            end_game(mouse_x, mouse_y)
        
    pygame.display.update()

if use_device:
    ard_conn.ser.close()
game.close_connection()
