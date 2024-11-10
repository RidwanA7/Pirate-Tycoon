import time
import pygame
from buildings import Building
class Dock(Building):
    def __init__(self, size, position):
        super().__init__(position)
        self.image = pygame.image.load(r"C:\Users\Study\PycharmProjects\NEA Images\Wp3TJeiWRvK6ltBUFT4DdQ.jpg")
        self.image = pygame.transform.scale(self.image, (100, 50))
        self.rect = self.image.get_rect(topleft=position)
        self.size = size
        self.goldRate = self.setGoldRate()
        self.returnFrequency = self.setReturnFrequency()
        self.level = 1
        self.lastGenerated = time.time()
        self.visibleUpgradeBox = True
        self.upgradeCost = 30

    def setGoldRate(self):
        if self.size == 'small':
            return 100
        elif self.size == 'medium':
            return 200
        elif self.size == 'large':
            return 300

    def setReturnFrequency(self):
        if self.size == "small":
            return 5
        elif self.size == "medium":
            return 3
        elif self.size == "large":
            return 2

    def isTimeForReturn(self):
        currentTime = time.time()
        if currentTime - self.lastGenerated >= self.returnFrequency:
            self.lastGenerated = currentTime
            return True
        return False

    def drawUpgrade(self, screen, cameraX, cameraY):
        # Draw the upgradebox if visible
        if self.visibleUpgradeBox:
            pygame.draw.rect(screen, (200, 200, 200), (self.rect.x - 25 + cameraX, self.rect.y - 30 + cameraY, 200, 25))
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"Upgrade {self.upgradeCost}$", True, (0, 0, 0))
            screen.blit(text, (self.rect.x -25 + cameraX, self.rect.y - 30 + cameraY))

    def toggleUpgrade(self, mousePos):
        # If dock is clicked, show the upgrade box
        if self.rect.collidepoint(mousePos):
            self.visibleUpgradeBox = not self.visibleUpgradeBox

    def upgradeBoxClicked(self,mousePos, gold):
        if self.visibleUpgradeBox:
            upgradeBoxRect = pygame.Rect(self.rect.x - 25 , self.rect.y - 30, 200, 25)

            if upgradeBoxRect.collidepoint(mousePos) and gold >= self.upgradeCost:
                self.goldRate += 50
                if self.returnFrequency > 1:
                    self.returnFrequency -= 1
                gold -= self.upgradeCost
                self.upgradeCost += 100
        return gold
