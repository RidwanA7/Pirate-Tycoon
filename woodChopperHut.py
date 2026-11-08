import pygame
from buildings import Building
import math
import random
from enemy import *

class WoodChopper():

    assignedTrees = set()  # Shared set to track trees currently being chopped

    def __init__(self, position, trees, hutPos, hut, landPositions):
        self.image = pygame.image.load(r"C:\Users\Study\Pirate Tycoon\images\woodChopper.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(center=position)
        self.speed = 1
        self.trees = trees
        self.hut = hutPos
        self.hutObject = hut
        self.landPositions = landPositions  # Store land_positions as an instance attribute
        self.targetTree = self.findNearestTree(trees)
        self.state = "movingToTree"

    def findNearestTree(self, trees):
        availableTrees = [tree for tree in trees if tree not in WoodChopper.assignedTrees and tree in self.landPositions]
        if not availableTrees:
            return None

        tree = min(availableTrees, key=lambda tree: math.dist(self.rect.center, tree))
        WoodChopper.assignedTrees.add(tree)  # Mark this tree as being chopped
    
        return tree

    def move(self):
        """Move the woodchopper along the calculated path towards the target."""
        if self.state == "movingToTree" and self.targetTree:
            targetX, targetY = self.targetTree
        else:
            targetX, targetY = self.hut  # Return to the hut after cutting the tree

        if not hasattr(self, "path") or not self.path:
            startPos = (self.rect.x//20 * 20, self.rect.y//20 * 20)
            self.path = calculatePath(startPos, (targetX, targetY), self.landPositions, self.trees, 20)
        if self.path:
            moveAlongPath(self, self.path, 20)
            nextX, nextY = self.path[0]
            if abs(self.rect.x - nextX) < self.speed and abs(self.rect.y - nextY) < self.speed:
                dx, dy = targetX - self.rect.x, targetY - self.rect.y
                distance = math.dist(self.rect.center, (targetX, targetY))
                self.path.pop(0)
        
        dx, dy = targetX - self.rect.x, targetY - self.rect.y
        distance = math.sqrt(dx**2 + dy**2)
        if not self.path or (self.rect.x, self.rect.y) == (targetX, targetY) or distance <= 60:  # Reached destination
            if self.state == "movingToTree":
                self.destroyTree()
                self.path = None 
          #  self.path = None  # Reset path for next movement

    def destroyTree(self):
        """Remove the tree from the list and return to the hut."""
        if self.targetTree in self.trees:
            self.trees.remove(self.targetTree)
        self.targetTree = None
        self.state = "returningToHut"
        self.path = None

    def update(self):
        """Update movement logic."""
        if self.state == "returningToHut" and math.dist(self.rect.center, self.hut) <= 60:
            self.hutObject.increaseWood()  # Increase wood count when returning
            self.targetTree = self.findNearestTree(self.trees)  # Find a new tree when back at the hut
            if self.targetTree:
                self.state = "movingToTree"
                self.path = None
            else:
                self.state = "idle"
        if self.state == "idle":
            self.targetTree = self.findNearestTree(self.trees)
            if self.targetTree:
                self.state = "movingToTree"
                self.path = None
        self.move()

def generateTrees(landPositions, numTrees):
    treePositions = set()
    while len(treePositions) < numTrees:
        treePos = random.choice(landPositions)  # Pick a random land tile
        treePositions.add(treePos)
    return list(treePositions)  # Convert to list before returning

class WoodChopperHut(Building):
    def __init__(self, position, price, trees, landPositions):
        super().__init__(position, price)
        self.image = pygame.image.load(r"C:\Users\Study\Pirate Tycoon\images\woodChopperHut.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(topleft=position)
        self.label = "woodChopperHut"
        self.hutPos = position
        self.woodCount = 0
        self.font = pygame.font.Font(None, 24)  # Font for displaying wood count
        self.landPositions = landPositions

        # Spawn two woodchoppers at the hut, passing land positions
        self.woodchoppers = [WoodChopper(position, trees, self.hutPos, self, landPositions) for _ in range(1)]

    def increaseWood(self):
        """Increase wood count when a chopper returns with wood."""
        self.woodCount += 1  # Increase wood count when a chopper returns

    def update(self):
        """Update woodchoppers' movement."""
        for chopper in self.woodchoppers:
            chopper.update()

    def draw(self, screen, cameraX, cameraY):
        """Draw the hut and woodchoppers."""
        screen.blit(self.image,(self.rect.x + cameraX, self.rect.y + cameraY))
        # Draw wood count above the hut
        woodText = self.font.render(f"Wood: {self.woodCount}", True, (255, 255, 255))
        screen.blit(woodText, (self.rect.x + cameraX, self.rect.y + cameraY - 20))

        for chopper in self.woodchoppers:
            screen.blit(chopper.image, (chopper.rect.x + cameraX, chopper.rect.y + cameraY))
