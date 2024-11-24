import pygame
from buildings import Building

class Tent(Building):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load(r"C:\Users\Study\PycharmProjects\NEA Images\pixel-art-camp-tent-picnic_150088-1055.jpg")
        self.image = pygame.transform.scale(self.image, (70, 50))
        self.rect = self.image.get_rect(topleft=position)
        self.label = "Tent"
        self.visibleUpgradeBox = True
        self.sleepPoints = 0

    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))
        label_surface = pygame.font.SysFont(None, 36).render(self.label, True, (255, 255, 255))
        label_rect = label_surface.get_rect(center=(self.rect.centerx + cameraX, self.rect.centery + cameraY - 10))
        screen.blit(label_surface, label_rect)

    def upgradeBoxClicked(self, mousePos, gold):
        if self.visibleUpgradeBox:
            upgradeBoxRect = pygame.Rect(self.rect.x - 25, self.rect.y - 30, 200, 25)
            if upgradeBoxRect.collidepoint(mousePos) and gold >= self.upgradeCost:
                self.sleepPoints += 10
                gold -= self.upgradeCost
                self.upgradeCost += 100
        return gold

    def update(self):
        pass
