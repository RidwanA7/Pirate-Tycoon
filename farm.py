import pygame
from buildings import Building

class Farm(Building):
    def __init__(self, position, price):
        super().__init__(position, price)
        self.image = pygame.image.load(r"C:\Users\Study\Pirate Tycoon\images\farm.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(topleft=position)
        self.position = position
        self.cropCount = 0
        self.nearbyFarms = 0
        self.label = "Farm"
        self.lastCropTime = pygame.time.get_ticks()
        self.group = None

    def increaseCropCount(self):
        currentTime = pygame.time.get_ticks()  # Get the current time in milliseconds
        if currentTime - self.lastCropTime >= 1000:  # Check if 1 second has passed
            self.cropCount += 1
            self.lastCropTime = currentTime  # Update the last crop time

class FarmGroup:
    def __init__(self):
        self.farms = []  # List of farms in this group
        self.coordinates = []
        self.cropCount = 0  # Shared crop count
        self.lastCropTime = pygame.time.get_ticks()  # Time tracker for crop generation
        self.label = "FarmGroup"
        self.baseSpeed = 1
        self.speed = 1

    def addFarm(self, farm):
        if farm not in self.farms:
            self.farms.append(farm)
            self.coordinates.append((farm.rect.centerx, farm.rect.centery))
            farm.group = self  # Link the farm to this group
    
    def getCoordinates(self):
        return self.coordinates

    def generateCrops(self, speedMultiplier):
        currentTime = pygame.time.get_ticks()
        adjustedSpeed = self.baseSpeed * speedMultiplier  # Adjust crop generation speed by multiplier
        if currentTime - self.lastCropTime >= 1000 / adjustedSpeed:  # Generate crops every second
            self.cropCount += len(self.farms)
            self.lastCropTime = currentTime

    def drawCropCount(self, screen, font, cameraX, cameraY):
        if self.farms:
            # Display crop count at the center of the group
            centerX = sum(farm.rect.x for farm in self.farms) / len(self.farms)
            centerY = sum(farm.rect.y for farm in self.farms) / len(self.farms)
            text = f"Farm ({self.cropCount})"
            textSurface = font.render(text, True, (255, 255, 255))
            textRect = textSurface.get_rect(center=(centerX + cameraX, centerY + cameraY - 20))
            screen.blit(textSurface, textRect)


    


