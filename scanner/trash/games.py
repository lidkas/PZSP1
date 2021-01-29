from deck import Deck, Player

class Makao():
    special_ranks = ('two', 'three', 'four', 'jack', 'queen', 'king', 'ace')

    def __init__(self):
        self.table = []
        self.players = []
        self.number_of_players = 0
        self.deck = Deck(self.table)
    def add_player(self, name):
        self.players.append(Player(self.deck, self.table, name))
        self.number_of_players += 1
    def start_game(self):
        for i in range(5):
            for player in self.players:
                player.draw_card()
        while True:
            self.deck.card_on_table()
            if self.table[-1][0] not in Makao.special_ranks:
                break
    def getstats(self):
        print(self.deck)
        for player in self.players:
            print(player.getname(), player.show_hand())
        print(self.table)











        
"""
class Wojna():
    suit = ('hearts', 'spades', 'diamond', 'clubs')
    ranks = ('two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'jack', 'queen', 'king', 'ace')
    suit_values = (2, 3, 1, 0)
    rank_values = range(2, 15)

    def __init__(self):
        self.table = []
        self.players = []
        self.number_of_players = 0
        self.deck = Deck(self.table)
        self.rounds_played = 0

    def check_boldness(self):
        for player in self.players:
            if player.getsize() == 0:
                print(player.getname(), player.getscore(), 'eliminated')
                self.players.remove(player)
                self.number_of_players -= 1
                return True
        return False

    def add_player(self, name):
        self.players.append(Player(self.deck, self.table, name))
        self.number_of_players += 1

    def remove_player(self, player):
        self.players.remove(player)
        self.number_of_players -= 1

    def getnumberofplayers(self):
        return self.number_of_players

    def start_game(self):
        while self.deck.size()+1 > len(self.players):
            for player in self.players:
                player.draw_card()

    def round(self):
        self.rounds_played += 1
        for player in self.players:
            player.shuffle()
            player.card_on_table(0)
        max_value = [0, 0]
        iterator = -len(self.players)
        winner = self.players[0]
        for player in self.players:
            iterator += 1
            current_value = Wojna.rank_values[Wojna.ranks.index(self.table[iterator][0])], Wojna.suit_values[Wojna.suit.index(self.table[iterator][1])]
            if max_value[0] < current_value[0] or (max_value == current_value and max_value[1] < current_value[1]):
                max_value = current_value
                winner = player
        winner.add_points(1)
        winner.take_table()

    def getstats(self):
        for player in self.players:
            print(player.getname(), player.getscore(), 'wins')

    def round_number(self):
        return self.rounds_played


wojna = Wojna()
wojna.add_player('emoboi')
wojna.add_player('mareczek')
wojna.add_player('koksuPL')
wojna.start_game()
while wojna.number_of_players > 1:
    wojna.check_boldness()
    if wojna.rounds_played > 10000:
        break
    wojna.round()
wojna.getstats()"""