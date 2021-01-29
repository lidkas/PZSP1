import pygame

id_cards = {
                '1': 'AS', '2': 'AH', '3': 'AD', '4': 'AC', '5': 'KS', '6': 'KH', '7': 'KD', '8': 'KC', '9': 'QS',
                '10': 'QH', '11': 'QD', '12': 'QC', '13': 'JS', '14': 'JH', '15': 'JD', '16': 'JC', '17': '10S',
                '18': '10H', '19': '10D', '20': '10C', '21': '9S', '22': '9H', '23': '9D', '24': '9C'
            }


class Card:
    def __init__(self, card_id, _positionx=None, _positiony=None):
        self.positionx = _positionx
        self.positiony = _positiony
        self.card_id = card_id
        self.name = id_cards[str(self.card_id)]
        if self.name[0] == '1':
            self.value = self.name[:2]
            self.suit = self.name[2]
        else:
            self.value = self.name[0]
            self.suit = self.name[1]

    def image_of_card(self, screen):
        """Creating photo of card"""
        card = pygame.image.load(f'images_of_cards/{self.name}.png').convert_alpha()
        card = pygame.transform.scale(card, (75, 100))
        screen.blit(card, (self.positionx, self.positiony))
        return card
