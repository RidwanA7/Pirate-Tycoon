import pygame
from buildings import Building

class Restaurant(Building):
    def __init__(self, position, price):
        super().__init__(position, price)
        self.image = pygame.image.load(r"C:\Users\Study\PycharmProjects\NEA Images\istockphoto-1320815200-612x612.jpg")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(topleft=position)
        self.label = "Restaurant"
        self.food = 10  # Total food stored
        self.payment = 800
        self.capacity = 2
        self.upgradeCost = 300000
        self.price = price

    def drawFoodCount(self, screen, cameraX, cameraY):
        font = pygame.font.SysFont(None, 20)
        foodText = font.render(f"Food ({self.food})", True, (255, 255, 255))
        screen.blit(foodText, (self.rect.x + cameraX, self.rect.y + cameraY - 20))

    def applyUpgrade(self):
        if self.level == 2:
            self.payment = 1000
            self.capacity = 5
            self.upgradeCost = 600000
        elif self.level == 3:
            self.payment = 2000
            self.capacity = 10
            self.upgradeCost *= 2
        else:
            self.payment *= 2
            self.capacity *= 2
            self.upgradeCost *= 2
