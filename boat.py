import pygame

class Boat(pygame.sprite.Sprite):
    def __init__(self, startPos, dockType):
        super().__init__()
        self.position = startPos
        self.image = pygame.image.load(r"C:\Users\Study\PycharmProjects\NEA Images\d68usui-ef6c334e-11b7-4f75-88b9-ecd34c5d4bf0.png")
        self.image = pygame.transform.scale(self.image, (20, 60))
        self.rect = self.image.get_rect(center=startPos)
        self.speed = 2
        self.baseSpeed = 2
        self.active = True  # Track if the boat is still moving
        self.orientation = "movingDown"
        self.dockType = dockType
        self.returning = False
        self.speedSet = False

    def updateSpeed(self, speedMultiplier):
        self.speed = self.baseSpeed * speedMultiplier
    
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

        # Scale the image based on the zoom level
        scaledImage = pygame.transform.scale(self.image,
                                              (int(self.image.get_width()  ),
                                               int(self.image.get_height()  )))

        # Adjust the position of the object with zoom
        screen.blit(scaledImage, (self.rect.x  + cameraX, self.rect.y  + cameraY))

    def drawBattleShip(self, screen):
        if self.orientation == "movingRight":
            screen.blit(pygame.transform.rotate(self.image, 90), (self.position[0], self.position[1]))
        if self.orientation == "movingLeft":
            screen.blit(pygame.transform.rotate(self.image, -90), (self.position[0], self.position[1]))
        if self.orientation == "movingUp":
            screen.blit(pygame.transform.rotate(self.image, 180), (self.position[0], self.position[1]))
        if self.orientation == "movingDown":
            screen.blit(self.image, (self.position[0], self.position[1]))


    def move(self, x, y):
        self.position = (self.position[0] + x, self.position[1] + y)
        self.rect.topleft = self.position
