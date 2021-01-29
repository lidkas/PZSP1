from cards import Card


class Player:
    def __init__(self):
        self.score = 0
        self.cards = [] # każdy gracz ma swoją własną talie, przechowywane lokalnie
        self.selected_card = None
        self.selected_musik = None
    
    def player_cards(self, screen, up):
        """GUI, pokazywanie karty na ekranie, 
        flaga 'up' czy na górze, 
        czy na dole w zależności czyje?"""
        x = 200
        for card in self.cards:
            x += 50
            card.positionx = x
            if up:
                card.positiony = 600
            else:
                card.positiony = 0
            card.image_of_card(screen)
        
    def remove_from_player(self, card):
        if card and card in self.cards:
            self.cards.remove(card)
            return card  # ?????????????????????????????????
    
    def append_card(self, card):
        if card:
            self.cards.append(card)
            return card
                









    

