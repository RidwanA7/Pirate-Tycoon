import pygame
class Building(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.position = position
        self.level = 1
        self.image = None
        self.rect = None

    def upgrade(self):
        self.level += 1
        # Implement upgrade logic common to all buildings




