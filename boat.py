import pygame
import os

class Boat(pygame.sprite.Sprite):
    def __init__(self, startPos, dockType):
        super().__init__()
        self.position = startPos
        currentDir = os.path.dirname(__file__)
        imagePath = os.path.join(currentDir, "images", "boat.png")
        self.image = pygame.image.load(imagePath)
        self.image = pygame.transform.scale(self.image, (20, 60))
        self.rect = self.image.get_rect(center=startPos)
        self.speed = 2
        self.baseSpeed = 2
        self.active = True  # Track if the boat is still moving
        self.orientation = "movingDown"
        self.dockType = dockType
        self.returning = False
        self.speedSet = False

    def updateSpeed(self):
        self.speed = self.baseSpeed
    
    def isAtTarget(self, targetPos, tolerance=10):
        # Returns True if the boat is within the tolerance distance from the target position
        if abs(self.rect.x - targetPos[0]) <= tolerance and abs(self.rect.y - targetPos[1]) <= tolerance:
            return True
        return False

    def moveTowards(self, targetPos):
        if self.active:
            directionX = targetPos[0] - self.rect.x
            directionY = targetPos[1] - self.rect.y
            distance = (directionX ** 2 + directionY ** 2) ** 0.5

            # Normalize direction and move the boat towards the target position, using the boat's speed
            if distance > self.speed:
                # Normalize direction and move the boat towards the target position
                self.rect.x += directionX / distance * self.speed
                self.rect.y += directionY / distance * self.speed
            else:
                # Move the boat directly to the target position and stop moving
                self.rect.x = targetPos[0]
                self.rect.y = targetPos[1]
                self.active = False  # Stop moving when at the target position

    def draw(self, screen, cameraX, cameraY):

        # Scale the image
        scaledImage = pygame.transform.scale(self.image,
                                              (int(self.image.get_width()  ),
                                               int(self.image.get_height()  )))

        # Adjust the position of the object
        screen.blit(scaledImage, (self.rect.x  + cameraX, self.rect.y  + cameraY))

    def move(self, x, y):
        self.position = (self.position[0] + x, self.position[1] + y)
        self.rect.topleft = self.position
