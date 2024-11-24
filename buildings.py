import pygame
class Building(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.position = position
        self.level = 1
        self.image = None
        self.rect = None
        self.visibleUpgradeBox = True
        self.upgradeCost = 30

    def toggleUpgrade(self, mousePos):
        # If dock is clicked, show the upgrade box
        if self.rect.collidepoint(mousePos):
            self.visibleUpgradeBox = not self.visibleUpgradeBox

    def drawUpgrade(self, screen, cameraX, cameraY):
        # Draw the upgradebox if visible
        if self.visibleUpgradeBox:
            pygame.draw.rect(screen, (200, 200, 200), (self.rect.x - 25 + cameraX, self.rect.y - 30 + cameraY, 200, 25))
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"Upgrade {self.upgradeCost}$", True, (0, 0, 0))
            screen.blit(text, (self.rect.x -25 + cameraX, self.rect.y - 30 + cameraY))

    def upgradeBoxClicked(self, mousePos, gold):
        if self.visibleUpgradeBox:
            upgradeBoxRect = pygame.Rect(self.rect.x - 25, self.rect.y - 30, 200, 25)
        return gold

    def upgrade(self):
        self.level += 1
        # Implement upgrade logic common to all buildings




