import pygame
import time
import random
from farmer import Farmer
from path import Path, Land
import math

#new

class Node:
    def __init__(self, pos, g_cost=float('inf'), h_cost=0):
        self.pos = pos
        self.g_cost = g_cost  # Cost from start to this node
        self.h_cost = h_cost  # Estimated cost from this node to end
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = None

def calculate_path(start_pos, target_pos, landPositions, treePositions, gridSize):
    def get_neighbors(pos):
        x, y = pos
        neighbors = [
            (x + gridSize, y),  # right
            (x - gridSize, y),  # left
            (x, y + gridSize),  # down
            (x, y - gridSize)   # up
        ]
        return [n for n in neighbors if n in landPositions and n not in treePositions]
    
    def heuristic(pos, target):
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])
    
    def find_nearest_land(pos):
        """Find the closest land position to the given pos."""
        if pos in landPositions and pos not in treePositions:
            return pos  # Target is already valid

        # Find nearest valid land tile
        nearest_land = min((p for p in landPositions if p not in treePositions), key=lambda p: heuristic(pos, p))
        return nearest_land
    
    start_grid = (start_pos[0], start_pos[1])
    target_grid = find_nearest_land((target_pos[0], target_pos[1]))  # Ensure valid target
    
    start_node = Node(start_grid, g_cost=0, h_cost=heuristic(start_grid, target_grid))
    
    open_set = {start_grid: start_node}
    closed_set = set()
    
    while open_set:
        current_pos = min(open_set, key=lambda pos: open_set[pos].f_cost)
        current = open_set.pop(current_pos)
        
        if current.pos == target_grid:
            path = []
            while current:
                path.append(current.pos)
                current = current.parent
            return path[::-1]
        
        closed_set.add(current_pos)
        
        for neighbor_pos in get_neighbors(current_pos):
            if neighbor_pos in closed_set:
                continue
                
            g_cost = current.g_cost + gridSize
            
            if neighbor_pos not in open_set:
                neighbor = Node(neighbor_pos)
                open_set[neighbor_pos] = neighbor
            else:
                neighbor = open_set[neighbor_pos]
                if g_cost >= neighbor.g_cost:
                    continue
            
            neighbor.parent = current
            neighbor.g_cost = g_cost
            neighbor.h_cost = heuristic(neighbor_pos, target_grid)
            neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
    
    return None

def move_along_path(self, path, gridSize):
    if not path or len(path) < 2:
        return
    
    next_pos = path[0]
    
    dx = next_pos[0] - self.rect.x
    dy = next_pos[1] - self.rect.y
    
    if abs(dx) > self.speed:
        self.rect.x += self.speed if dx > 0 else -self.speed
    else:
        self.rect.x = next_pos[0]
        
    if abs(dy) > self.speed:
        self.rect.y += self.speed if dy > 0 else -self.speed
    else:
        self.rect.y = next_pos[1]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()  # Initialise the sprite base class
        self.speed = 1
        self.image = pygame.image.load(r'C:\Users\Study\Pirate Tycoon\images\farmer.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect(center=position)
        self.attackCooldown = 3
        self.damage = 40
        self.lastAttackTime = 0
        self.foundTarget = False
        self.targetPos = None
        self.target = None
        self.changeDirectionTime = 0
        self.maxHealth = 100
        self.health = 100
        self.showHealthBar = False
        self.healthBarStartTime = 0
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def findClosestObject(self, placedItems):
        closestDistance = float('inf')
        for placedItem in placedItems:
            object = placedItem["item"]
            if not isinstance(object, Farmer) and not isinstance(object, Path) and not isinstance(object, Land):
                if not object.beingAttacked:
                    distance = ((self.rect.x - object.rect.x) ** 2 + (self.rect.y - object.rect.y) ** 2) ** 0.5
                    if distance < closestDistance:
                        closestDistance = distance
                        targetObject = object
                        self.targetPos = object.rect.x, object.rect.y
                        self.foundTarget = True

        if self.foundTarget:
            self.target = targetObject
            targetObject.beingAttacked = True

    def findClosestPirate(self, boatAndPirates):
        closestDistance = float('inf')
        for boat, pirate in boatAndPirates:
            if pirate is not None:
                distance = ((self.rect.x - pirate.rect.centerx) ** 2 + (self.rect.y - pirate.rect.centery) ** 2) ** 0.5
                if not pirate.beingAttacked:
                    if distance < closestDistance:
                        closestDistance = distance
                        targetObject = pirate
                        self.targetPos = pirate.rect.centerx, pirate.rect.centery
                        self.foundTarget = True
            if self.foundTarget:
                self.target = targetObject
                self.target.beingAttacked = True
                    
    def moveTowards(self, landPositions, treePositions, gridSize=20):
        if self.target:
            centerx, centery = self.target.rect.center
            self.targetPos = (centerx//gridSize * gridSize, centery//gridSize * gridSize)  # Update dynamically
            
            currentTime = time.time()

            if not hasattr(self, 'path') or not self.path or \
            self.targetPos != getattr(self, 'last_target', None):
                if currentTime - getattr(self, 'lastTime', 0) > 1:
                    self.lastTime = currentTime
                    start_pos = (self.rect.x//gridSize * gridSize, self.rect.y//gridSize * gridSize)
                    self.path = calculate_path(start_pos, self.targetPos, landPositions, treePositions, gridSize)
                    self.last_target = self.targetPos
                
            if self.path:
                current_waypoint = self.path[0]
                if (abs(self.rect.x - current_waypoint[0]) < 4 and 
                    abs(self.rect.y - current_waypoint[1]) < 4):
                    self.path.pop(0)
                
                move_along_path(self, self.path, gridSize)
    
    def atTarget(self):
        targetX, targetY = self.target.rect.x, self.target.rect.y
        distance = math.sqrt((self.rect.x - targetX) ** 2 + (self.rect.y - targetY)**2)
        if distance <= 30:
            return True
        return False
    
    def attack(self):
        # Attack the target
        currentTime = time.time()
        if currentTime - self.lastAttackTime > self.attackCooldown:
            self.lastAttackTime = currentTime
            self.target.showHealthBar = True
            self.target.healthBarStartTime = time.time()
            self.target.health -= self.damage
        if self.target.health <= 0:
            self.target = None
            self.foundTarget = False

    def drawHealthBar(self, screen, cameraX, cameraY):
         # Calculate health bar width
        bar_width = self.rect.width
        bar_height = 5
        health_ratio = self.health / self.maxHealth
        health_bar_width = int(bar_width * health_ratio)

        # Define health bar positions
        bar_x = self.rect.x + cameraX
        bar_y = self.rect.y - bar_height - 2 + cameraY # Position it above the building

        # Draw background bar (red)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # Draw health bar (green)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_bar_width, bar_height))

        # Hide health bar after 2 seconds
        current_time = time.time()
        if current_time - self.healthBarStartTime > 2:
            self.showHealthBar = False
    
    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))
        # Draw the health bar if it should be displayed
        if self.showHealthBar:
            self.drawHealthBar(screen, cameraX, cameraY)

    def moveAround(self, landPositions, treePositions, gridSize=20):
       # Calculate the next position
        new_position = [self.rect.x + self.direction[0] * self.speed, 
                        self.rect.y + self.direction[1] * self.speed]

        gridPosition = (new_position[0] // gridSize * gridSize, new_position[1] // gridSize * gridSize)

        # Only move if the new position is on land
        if tuple(gridPosition) in landPositions and gridPosition not in treePositions:
            self.rect.x, self.rect.y = new_position[0], new_position[1]
        # Randomly change direction occasionally
        if random.random() < 0.02:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]) 

class EnemyCaptain(Enemy):
    def __init__(self, position):
        super().__init__(position)
        self.image = pygame.image.load(r'C:\Users\Study\Pirate Tycoon\images\captain.png')
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.attackCooldown = 2
        self.damage = 50
        self.maxHealth = 150
        self.health = 150
        self.speed = 1
