import pygame
from farm import Farm, FarmGroup
from cookhouse import Cookhouse

class Farmer(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.position = position
        self.image = pygame.image.load(r"C:\Users\Study\Pirate Tycoon\images\farmer.png")
        self.image = pygame.transform.scale(self.image, (10, 10))
        self.rect = self.image.get_rect(center=self.position)
        self.speed = 2
        self.carryingCrops = False
        self.label = "Farmer"
        self.crops = 0

    def moveTowards(self, farm, pathGrid):
        currentPos = self.position
        targetPos = farm.position
        x_diff = targetPos[0] - currentPos[0]
        y_diff = targetPos[1] - currentPos[1]
        x_step = y_step = 0

        if x_diff > 0:
            x_step = 1
            nextPos = (currentPos[0] + x_step, currentPos[1])
            if pathGrid.get(nextPos, False):
                self.position = nextPos
                self.rect.center = self.position
            elif y_diff > 0:
                y_step = 1
                nextPos = (currentPos[0], currentPos[1] + y_step)
                print("moving up", nextPos)
                if pathGrid.get(nextPos, False):
                    self.position = nextPos
                    self.rect.center = self.position
            elif y_diff < 0:
                y_step = -1
                nextPos = (currentPos[0], currentPos[1] + y_step)
                print("moving down", nextPos)
                if pathGrid.get(nextPos, False):
                    self.position = nextPos
                    self.rect.center = self.position

        elif x_diff < 0:
            x_step = -1
            nextPos = (currentPos[0] + x_step, currentPos[1])
            if pathGrid.get(nextPos, False):
                self.position = nextPos
                self.rect.center = self.position
            elif y_diff < 0:
                y_step = -1
                nextPos = (currentPos[0], currentPos[1] + y_step)
                if pathGrid.get(nextPos, False):
                    self.position = nextPos
                    self.rect.center = self.position
            elif y_diff > 0:
                y_step = 1
                nextPos = (currentPos[0], currentPos[1] + y_step)
                if pathGrid.get(nextPos, False):
                    self.position = nextPos
                    self.rect.center = self.position
        
            
    
    def isAtFarm(self, farm):
            # Calculate the distance between the farmer and the farm
        x_diff = abs(self.position[0] - farm.position[0])
        y_diff = abs(self.position[1] - farm.position[1])
        
        # Check if the farmer is within 20 pixels of the farm
        return x_diff <= 20 and y_diff <= 20

    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))
        font = pygame.font.SysFont("arial", 14)
        crop_text = font.render(f"Crops ({self.crops})", True, (255, 255, 255))  # White text
        text_pos = (self.rect.x + cameraX, self.rect.y + cameraY - 15)
        screen.blit(crop_text, text_pos)


    def getCrops(self, farmGroup):
        if isinstance(farmGroup, FarmGroup):  # Ensure farmGroup is a valid instance
            self.carryingCrops = True
            self.crops += farmGroup.cropCount
            farmGroup.cropCount = 0  # Reset the farm's crop count
        else:
            print("Invalid farm group provided.")   

    def isAtCookhouse(self, cookhouse):
        # Calculate the distance between the farmer and the cookhouse
        x_diff = abs(self.position[0] - cookhouse.position[0])
        y_diff = abs(self.position[1] - cookhouse.position[1])

        # Check if the farmer is within 20 pixels of the cookhouse
        return x_diff <= 20 and y_diff <= 20
    
    def dropCrops(self, cookhouse):
        if self.carryingCrops and isinstance(cookhouse, Cookhouse):
            self.carryingCrops = False
            cookhouse.crops += self.crops
            self.crops = 0
        else:
            print("Invalid cookhouse provided.")