import pygame
import time
from farm import Farm, FarmGroup
from cookhouse import Cookhouse
from collections import deque
from restuarant import Restaurant

#new

class Farmer(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.position = position
        self.image = pygame.image.load(r"C:\Users\Study\Pirate Tycoon\images\farmer.png")
        self.image = pygame.transform.scale(self.image, (10, 10))
        self.rect = self.image.get_rect(center=self.position)
        self.speed = 1
        self.baseSpeed = 1
        self.carryingCrops = False
        self.carryingFood = False
        self.label = "Farmer"
        self.crops = 0
        self.role = None

        self.path = None  # Stores the computed path
        self.pathIndex = 0  # Tracks position in path
        self.reversePath = False  # Tracks if the farmer is going back

        self.health = 50
        self.maxHealth = 50
        self.showHealthBar = False
        self.healthBarStartTime = 0

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
    
    def checkBuildingAtEnd(self, pathGrid, placedItems):
        position = tuple(self.position)
        queue = deque([position])
        visited = set([position])  # Initialize with starting position
        
        def isWithinRange(pos1, pos2, threshold=15):
            dx = pos1[0] - pos2[0]
            dy = pos1[1] - pos2[1]
            return (dx**2 + dy**2)**0.5 <= threshold
        
        while queue:
            current = queue.popleft()
            
            # Check if the current position is near a placed building
            for item in placedItems:
                buildingPosition = (
                    item["item"].position[0] + 20 // 2,
                    item["item"].position[1] + 20 // 2
                )
                if isWithinRange(current, buildingPosition):
                    if isinstance(item["item"], Farm):
                        return "farm"
                    elif isinstance(item["item"], Restaurant):
                        return "restaurant"
            
            # Get neighbors
            neighbors = [
                (current[0], current[1] - 1),  # up
                (current[0] + 1, current[1]),  # right
                (current[0], current[1] + 1),  # down
                (current[0] - 1, current[1])   # left
            ]
            
            # Check each neighbor
            for neighbor in neighbors:
                # Only add neighbor if it's in the pathGrid, is walkable, and hasn't been visited
                if (neighbor in pathGrid and 
                    pathGrid[neighbor] and 
                    neighbor not in visited):
                    queue.append(neighbor)
                    visited.add(neighbor)
                    
            # Optional: Add debug print statements
            #print(f"Current position: {current}")
            #print(f"Queue size: {len(queue)}")
            #print(f"Visited positions: {len(visited)}")
            
        return None

    def assignFarmerRole(self, pathGrid, placedItems):
        buildingType = self.checkBuildingAtEnd(pathGrid, placedItems)
        if buildingType == "farm":
            self.role = "farmToCookhouse"
        elif buildingType == "restaurant":
            self.role = "cookhouseToRestaurant"
        else:
            self.role = None  # No valid role found; farmer won't move

    def findPath(self, start, target, pathGrid):
        """Finds the shortest path using BFS."""
        queue = deque([start])
        visited = set()
        visited.add(start)
        parent = {start: None}

        GRID_STEP = self.speed
        targetFound = False
        finalPos = None

        while queue and not targetFound:
            current = queue.popleft()

            if ((current[0] - target[0]) ** 2 + (current[1] - target[1]) ** 2) ** 0.5 <= 15:
                targetFound = True
                finalPos = current
                break

            neighbors = [
                (current[0], current[1] - GRID_STEP),  # Up
                (current[0] + GRID_STEP, current[1]),  # Right
                (current[0], current[1] + GRID_STEP),  # Down
                (current[0] - GRID_STEP, current[1])   # Left
            ]

            for neighbor in neighbors:
                neighbor = tuple(map(int, neighbor))
                if neighbor in pathGrid and pathGrid[neighbor] and neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    parent[neighbor] = current

        if targetFound:
            path = []
            current = finalPos
            while current is not None:
                path.append(current)
                current = parent[current]
            path.reverse()
            return path[1:]  # Exclude the current position
        return None  # No path found

    def moveTo(self, nextPos):
        currentPos = self.position
        moveDistance = self.speed

        directionX = nextPos[0] - currentPos[0]
        directionY = nextPos[1] - currentPos[1]
        distance = (directionX**2 + directionY**2) ** 0.5

        if distance > 0:
            normalizedX = directionX / distance * moveDistance
            normalizedY = directionY / distance * moveDistance

            self.position[0] += normalizedX
            self.position[1] += normalizedY
            self.rect.center = self.position


    def moveTowards(self, item, pathGrid):
        currentPos = tuple(self.position)
        targetPos = (item.position[0] + 20 // 2, item.position[1] + 20 // 2)
        
        # If we're already close enough, don't move
        if ((currentPos[0] - targetPos[0]) ** 2 + (currentPos[1] - targetPos[1]) ** 2) ** 0.5 <= 17:
            self.currentPath = None
            return

        if not hasattr(self, 'currentPath') or self.currentPath is None or self.targetPos != targetPos:
            self.currentPath = self.findPath(currentPos, targetPos, pathGrid)
            self.targetPos = targetPos  # Store the target position

         #If a path exists, follow it:
        if self.currentPath and len(self.currentPath) > 1:
            nextPos = self.currentPath.pop(0)  # Get the next position in the path
            self.moveTo(nextPos)
        else:
            print(f"No path found from {currentPos} to {targetPos}")
        

    def calculateDistance(self, target):
        return ((self.position[0] - target.position[0]) ** 2 + (self.position[1] - target.position[1]) ** 2) ** 0.5

    def hasAPath(self, target, pathGrid, gridSize=20):
        start = (self.position[0] // gridSize * gridSize, self.position[1] // gridSize * gridSize)
        end = (target.position[0] // gridSize * gridSize, target.position[1] // gridSize * gridSize)

         # Check if start is within 20 pixels of end
        if ((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2) ** 0.5 <= 20:
            return True

        queue = deque([start])
        visited = set()
        visited.add(start)

        while queue:
            current = queue.popleft()

            if ((current[0] - end[0]) ** 2 + (current[1] - end[1]) ** 2) ** 0.5 <= 20:
                return True

            # Get neighbors (up, down, left, right)
            neighbors = [
                (current[0] + gridSize, current[1]),
                (current[0] - gridSize, current[1]),
                (current[0], current[1] + gridSize),
                (current[0], current[1] - gridSize)
            ]
          
            for neighbor in neighbors:
                if neighbor in pathGrid and pathGrid[neighbor] and neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)

        return False

    def isAtFarm(self, farm):
        farmX = farm.position[0] + 20 // 2
        farmY = farm.position[1] + 20 // 2
        xDiff = abs(self.position[0] - farmX)
        yDiff = abs(self.position[1] - farmY)
        
        # Check if the farmer is within 20 pixels of the farm
        return xDiff <= 17 and yDiff <= 17

    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))
        font = pygame.font.SysFont("arial", 14)
        cropText = font.render(f"Crops ({self.crops})", True, (255, 255, 255))  # White text
        textPos = (self.rect.x + cameraX, self.rect.y + cameraY - 15)
        screen.blit(cropText, textPos)

         # Draw the health bar if it should be displayed
        if self.showHealthBar:
            self.drawHealthBar(screen, cameraX, cameraY)


    def getCrops(self, farmGroup):
        if isinstance(farmGroup, FarmGroup):  # Ensure farmGroup is a valid instance
            self.carryingCrops = True
            self.crops += farmGroup.cropCount
            farmGroup.cropCount = 0  # Reset the farm's crop count
        else:
            print("Invalid farm group provided.")   

    def isAtCookhouse(self, cookhouse):
        # Calculate the distance between the farmer and the cookhouse
        cookhouseX = cookhouse.position[0] + 20 // 2
        cookhouseY = cookhouse.position[1] + 20 // 2
        xDiff = abs(self.position[0] - cookhouseX)
        yDiff = abs(self.position[1] - cookhouseY)

        # Check if the farmer is within 20 pixels of the cookhouse
        return xDiff <= 17 and yDiff <= 17
    
    def isAtPlace(self, item):
        itemX = item.position[0] + 20 // 2
        itemY = item.position[1] + 20 // 2
        xDiff = abs(self.position[0] - itemX)
        yDiff = abs(self.position[1] - itemY)
        
        # Check if the farmer is within 20 pixels of the item
        return xDiff <= 17 and yDiff <= 17
    
    def dropCrops(self, cookhouse):
        if self.carryingCrops and isinstance(cookhouse, Cookhouse):
            if cookhouse.crops + self.crops > cookhouse.capacity:
                cookhouse.crops = cookhouse.capacity
                return
            self.carryingCrops = False
            cookhouse.crops += self.crops
            self.crops = 0
        else:
            print("Invalid cookhouse provided.")
        
    def getFood(self, cookhouse):
        if isinstance(cookhouse, Cookhouse):
            self.carryingFood = True
            self.crops += cookhouse.crops
            cookhouse.crops = 0
    
    def dropFood(self, restaurant):
        if self.carryingFood and isinstance(restaurant, Restaurant):
            self.carryingFood = False
            restaurant.food += self.crops
            self.crops = 0
        else:
            print("Invalid restaurant provided.")

