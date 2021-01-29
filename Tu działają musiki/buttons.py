import pygame


class Button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)
        font = pygame.font.SysFont('comicsans', 20)
        text = font.render(self.text, True, (0, 0, 0))
        screen.blit(text, (self.x + (self.width / 2 - text.get_width() / 2),
                            self.y + (self.height / 2 - text.get_height() / 2)))

    def is_over(self, mouse_x=None, mouse_y=None):
        if mouse_x:
            if self.x < mouse_x < self.x + self.width and self.y < mouse_y < self.y + self.height:
                return True
        return False
