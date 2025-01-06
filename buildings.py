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

    def drawUpgrade(self, screen, cameraX, cameraY, zoomLevel):
        # Draw the upgrade box if visible
        if self.visibleUpgradeBox:
            # Adjust position and dimensions for zoom
            adjustedX = self.rect.x * zoomLevel - 25 * zoomLevel
            adjustedY = self.rect.y * zoomLevel - 30 * zoomLevel
            boxWidth = int(40 * zoomLevel)
            boxHeight = int(10 * zoomLevel)

            # Draw the scaled upgrade box
            pygame.draw.rect(screen, (200, 200, 200), (adjustedX + cameraX, adjustedY + cameraY, boxWidth, boxHeight))

            # Adjust font size for zoom
            fontSize = int(8 * zoomLevel)
            font = pygame.font.SysFont(None, fontSize)

            # Render and position text
            text = font.render(f"Upgrade {self.upgradeCost}$", True, (0, 0, 0))
            textX = adjustedX + 5 * zoomLevel  # Adjust text padding for zoom
            textY = adjustedY + 5 * zoomLevel
            screen.blit(text, (textX + cameraX, textY + cameraY))

    def upgradeBoxClicked(self, mousePos, gold):
        if self.visibleUpgradeBox:
            upgradeBoxRect = pygame.Rect(self.rect.x - 25, self.rect.y - 30, 200, 25)
        return gold

    def upgrade(self):
        self.level += 1
        pass




