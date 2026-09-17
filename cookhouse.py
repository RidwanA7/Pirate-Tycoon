import pygame
from buildings import Building
import os

class Cookhouse(Building):
    def __init__(self, position, price):
        super().__init__(position, price)
        currentDir = os.path.dirname(__file__)
        imagePath = os.path.join(currentDir, "images", "cookhouse.png")
        self.image = pygame.image.load(imagePath)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(topleft=position)
        self.position = position
        self.label = "Cookhouse"
        self.crops = 0  # Total food stored
        self.capacity = 5
        self.upgradeCost = 100000

    def drawFoodCount(self, screen, cameraX, cameraY):
        font = pygame.font.SysFont(None, 20)
        foodText = font.render(f"Crops ({self.crops})", True, (255, 255, 255))
        screen.blit(foodText, (self.rect.x + cameraX, self.rect.y + cameraY - 20))
    
    def applyUpgrade(self):
        if self.level == 2:
            self.capacity = 15
        elif self.level == 3:
            self.capacity = 30
        else:
            self.capacity *= 2


