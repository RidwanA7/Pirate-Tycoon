import pygame
from buildings import Building
class Cookhouse(Building):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load(r"C:\Users\Study\Pirate Tycoon\images\cookhouse.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(topleft=position)
        self.position = position
        self.label = "Cookhouse"
        self.crops = 0  # Total food stored

    def drawFoodCount(self, screen, cameraX, cameraY):
        font = pygame.font.SysFont(None, 20)
        food_text = font.render(f"Food ({self.crops})", True, (255, 255, 255))
        screen.blit(food_text, (self.rect.x + cameraX, self.rect.y + cameraY - 20))

