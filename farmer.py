import pygame
from farm import Farm, FarmGroup
from cookhouse import Cookhouse
from collections import deque
from restuarant import Restaurant

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
            
 
    def moveTowards(self, item, pathGrid):
        currentPos = tuple(self.position)
        targetPos = (item.position[0] + 20 // 2, item.position[1] + 20 // 2)
        
        # If we're already close enough, don't move
        if ((currentPos[0] - targetPos[0]) ** 2 + (currentPos[1] - targetPos[1]) ** 2) ** 0.5 <= 2:
            return
        
        # BFS to find the shortest path
        queue = deque([currentPos])
        visited = set()
        visited.add(currentPos)
        parent = {currentPos: None}
        targetFound = False
        finalPos = None

        # Define the base step size for the grid
        GRID_STEP = self.speed  # Use smallest possible step for pathfinding

        while queue and not targetFound:
            current = queue.popleft()
            
            # Check if we're close enough to target
            if ((current[0] - targetPos[0]) ** 2 + (current[1] - targetPos[1]) ** 2) ** 0.5 <= 15:
                targetFound = True
                finalPos = current
                break

            # Use single-unit steps for pathfinding
            neighbors = [
                (current[0], current[1] - GRID_STEP),  # up
                (current[0] + GRID_STEP, current[1]),  # right
                (current[0], current[1] + GRID_STEP),  # down
                (current[0] - GRID_STEP, current[1])   # left
            ]

            for neighbor in neighbors:
                neighbor = tuple(map(int, neighbor))
                if (neighbor in pathGrid and pathGrid[neighbor] and neighbor not in visited):
                    queue.append(neighbor)
                    visited.add(neighbor)
                    parent[neighbor] = current

        if targetFound:
            # Reconstruct path
            path = []
            current = finalPos
            while current is not None:
                path.append(current)
                current = parent[current]
            path.reverse()

            # Move towards next position using speed
            if len(path) > 1:
                nextPos = path[1]
                # Scale movement by the farmer's speed and multiplier
                moveDistance = self.speed  
                # Calculate direction and normalize movement to the next position
                directionX = nextPos[0] - currentPos[0]
                directionY = nextPos[1] - currentPos[1]
                distance = (directionX**2 + directionY**2) ** 0.5
                
                if distance > 0:
                    # Normalize the direction and multiply by speed and multiplier
                    normalizedX = directionX / distance * moveDistance
                    normalizedY = directionY / distance * moveDistance
                    
                    # Update position
                    self.position[0] += normalizedX
                    self.position[1] += normalizedY
                    self.rect.center = self.position
        else:
            print(f"No path found from {currentPos} to {targetPos}")
            # Optional: print some debug info about the pathGrid around current position
            print("Neighbors available:")
            for dx in [-GRID_STEP, 0, GRID_STEP]:
                for dy in [-GRID_STEP, 0, GRID_STEP]:
                    check_pos = (currentPos[0] + dx, currentPos[1] + dy)
                    if check_pos in pathGrid:
                        print(f"Position {check_pos}: {pathGrid[check_pos]}")

        

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
        return xDiff <= 15 and yDiff <= 15

    def draw(self, screen, cameraX, cameraY):
        screen.blit(self.image, (self.rect.x + cameraX, self.rect.y + cameraY))
        font = pygame.font.SysFont("arial", 14)
        cropText = font.render(f"Crops ({self.crops})", True, (255, 255, 255))  # White text
        textPos = (self.rect.x + cameraX, self.rect.y + cameraY - 15)
        screen.blit(cropText, textPos)


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
        return xDiff <= 15 and yDiff <= 15
    
    def isAtPlace(self, item):
        itemX = item.position[0] + 20 // 2
        itemY = item.position[1] + 20 // 2
        xDiff = abs(self.position[0] - itemX)
        yDiff = abs(self.position[1] - itemY)
        
        # Check if the farmer is within 20 pixels of the item
        return xDiff <= 15 and yDiff <= 15
    
    def dropCrops(self, cookhouse):
        if self.carryingCrops and isinstance(cookhouse, Cookhouse):
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

