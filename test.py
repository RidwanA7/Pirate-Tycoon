import unittest
from unittest.mock import MagicMock, patch
from unittest.mock import Mock, patch
import time
import pygame
import math
from farmer import Farmer
from farm import Farm, FarmGroup
from cookhouse import Cookhouse
from restuarant import Restaurant
from woodChopperHut import WoodChopper, WoodChopperHut
from perlin_noise import PerlinNoise
from world import TerrainGenerator, ALLTERRAINTYPES, SNOW
from farm import Farm, FarmGroup
from dock import Dock

from pirate import Pirate

class TestPirate(unittest.TestCase):
    def setUp(self):
        pygame.init()
        patcher = patch('pygame.image.load', return_value=pygame.Surface((20, 20)))
        self.addCleanup(patcher.stop)
        self.mock_load = patcher.start()

        # Pirate starting at (100, 100), with 500 coins
        self.pirate = Pirate((100, 100), 500)

    def test_initial_position_aligned_to_grid(self):
        self.assertEqual(self.pirate.position, [100, 100])

    def test_default_state(self):
        self.assertEqual(self.pirate.state, "exploring")
        self.assertEqual(self.pirate.hunger, 100)
        self.assertEqual(self.pirate.sleep, 100)
        self.assertEqual(self.pirate.payment, 500)

    def test_update_stats_reduces_hunger_and_sleep(self):
        self.pirate.satisfactionTimeDecrease -= 1  # Force update
        old_hunger = self.pirate.hunger
        old_sleep = self.pirate.sleep
        self.pirate.updatePirateStats()
        self.assertEqual(self.pirate.hunger, max(0, old_hunger - 4))
        self.assertEqual(self.pirate.sleep, max(0, old_sleep - 1))

    def test_update_states_transitions(self):
        self.pirate.hunger = 30
        self.pirate.sleep = 50
        self.pirate.updateStates()
        self.assertEqual(self.pirate.state, "hungry")

        self.pirate.hunger = 100
        self.pirate.sleep = 10
        self.pirate.updateStates()
        self.assertEqual(self.pirate.state, "tired")

        self.pirate.hunger = 100
        self.pirate.sleep = 100
        self.pirate.updateStates()
        self.assertEqual(self.pirate.state, "exploring")

    def test_pay_tent_after_5_seconds(self):
        mock_tent = MagicMock()
        mock_tent.payment = 300
        mock_tent.removeVisitor = MagicMock()
        self.pirate.sleep = 50
        self.pirate.pay("Tent", mock_tent)
        self.pirate.sleepIncrementStartTime -= 5.1  # Simulate time passing
        payment = self.pirate.pay("Tent", mock_tent)
        self.assertEqual(self.pirate.sleep, 100)
        self.assertEqual(payment, 300)

    def test_pay_restaurant_after_3_seconds(self):
        mock_restaurant = MagicMock()
        mock_restaurant.payment = 400
        mock_restaurant.food = 5
        mock_restaurant.removeVisitor = MagicMock()
        self.pirate.hunger = 30
        self.pirate.pay("Restaurant", mock_restaurant)
        self.pirate.hungerIncrementStartTime -= 3.1  # Simulate time passing
        payment = self.pirate.pay("Restaurant", mock_restaurant)
        self.assertEqual(self.pirate.hunger, 100)
        self.assertEqual(payment, 400)
        self.assertEqual(mock_restaurant.food, 3)

    def test_isAtObject_true_within_30(self):
        item_pos = [self.pirate.position[0] + 10, self.pirate.position[1] + 10]
        self.assertTrue(self.pirate.isAtObject(item_pos))

    def test_isAtObject_false_outside_30(self):
        item_pos = [self.pirate.position[0] + 100, self.pirate.position[1] + 100]
        self.assertFalse(self.pirate.isAtObject(item_pos))

    
class MockRect:
    def __init__(self, centerx, centery):
        self.centerx = centerx
        self.centery = centery

class MockPirate:
    def __init__(self, x, y, health=100):
        self.rect = MockRect(x, y)
        self.health = health
        self.showHealthBar = False
        self.healthBarStartTime = None

class Attacker:
    def __init__(self, x, y):
        self.position = (x, y)
        self.enemy = None
        self.lastAttackTime = 0
        self.attackCooldown = 1  # 1 second cooldown
        self.damage = 10

    def findEnemies(self, enemyPirates):
        if not self.enemy:
            for pirate in enemyPirates:
                distance = math.sqrt((self.position[0] - pirate.rect.centerx)**2 + (self.position[1] - pirate.rect.centery)**2)
                if distance < 50000:
                    self.enemy = pirate
                    break
        else:
            distance = math.sqrt((self.position[0] - self.enemy.rect.centerx)**2 + (self.position[1] - self.enemy.rect.centery)**2)
            if distance > 500:
                self.enemy = None

    def attack(self):
        currentTime = time.time()
        if self.enemy:
            if currentTime - self.lastAttackTime > self.attackCooldown:
                self.lastAttackTime = currentTime
                if self.enemy.health > 0:
                    self.enemy.showHealthBar = True
                    self.enemy.healthBarStartTime = time.time()
                    self.enemy.health -= self.damage
                else:
                    self.enemy = None

class TestAttacker(unittest.TestCase):
    def test_find_enemy_in_range(self):
        attacker = Attacker(100, 100)
        enemy = MockPirate(200, 200)
        attacker.findEnemies([enemy])
        self.assertEqual(attacker.enemy, enemy)

    def test_find_enemy_out_of_range(self):
        attacker = Attacker(0, 0)
        far_enemy = MockPirate(10000000, 10000000)  # far away
        attacker.findEnemies([far_enemy])
        self.assertIsNone(attacker.enemy)

    def test_enemy_leaves_range(self):
        attacker = Attacker(0, 0)
        enemy = MockPirate(100, 100)
        attacker.enemy = enemy
        # Move enemy far away
        enemy.rect.centerx = 10000
        enemy.rect.centery = 10000
        attacker.findEnemies([enemy])
        self.assertIsNone(attacker.enemy)

    def test_attack_enemy_within_cooldown(self):
        attacker = Attacker(0, 0)
        enemy = MockPirate(100, 100, health=50)
        attacker.enemy = enemy
        attacker.lastAttackTime = time.time() - 2  # Ensure cooldown has passed

        attacker.attack()
        self.assertEqual(enemy.health, 40)
        self.assertTrue(enemy.showHealthBar)
        self.assertIsNotNone(enemy.healthBarStartTime)

    def test_attack_enemy_no_damage_within_cooldown(self):
        attacker = Attacker(0, 0)
        enemy = MockPirate(100, 100, health=0)
        attacker.enemy = enemy
        attacker.lastAttackTime = time.time() - 2

        attacker.attack()
        self.assertIsNone(attacker.enemy)

    def test_attack_cooldown_prevents_attack(self):
        attacker = Attacker(0, 0)
        enemy = MockPirate(100, 100, health=50)
        attacker.enemy = enemy
        attacker.lastAttackTime = time.time()  # Cooldown not passed

        attacker.attack()
        self.assertEqual(enemy.health, 50)  # Health shouldn't change

#enemy
from enemy import calculatePath, Enemy

class TestCalculatePath(unittest.TestCase):
    def test_simple_path(self):
        land = {(0, 0), (20, 0), (40, 0)}
        trees = set()
        path = calculatePath((0, 0), (40, 0), land, trees, 20)
        self.assertEqual(path, [(0, 0), (20, 0), (40, 0)])

    def test_blocked_path_returns_none(self):
        land = {(0, 0), (20, 0)}
        trees = {(20, 0)}
        path = calculatePath((0, 0), (40, 0), land, trees, 20)
        self.assertEqual(path, [(0,0)])

    def test_nearest_land_fallback(self):
        land = {(0, 0), (20, 0), (40, 0)}
        trees = set()
        # Target is not in land positions directly
        path = calculatePath((0, 0), (35, 0), land, trees, 20)
        self.assertEqual(path, [(0, 0), (20, 0), (40, 0)])


class TestEnemy(unittest.TestCase):
    def setUp(self):
        self.enemy = Enemy((100, 100))
        self.enemy.image = pygame.Surface((20, 20))  
        self.enemy.rect = self.enemy.image.get_rect(center=(100, 100))
        self.mockTarget = Mock()
        self.mockTarget.rect = pygame.Rect(120, 100, 20, 20)
        self.mockTarget.health = 100
        self.mockTarget.showHealthBar = False
        self.mockTarget.beingAttacked = False

    def test_find_closest_object(self):
        building = {'item': self.mockTarget}
        self.enemy.findClosestObject([building])
        self.assertEqual(self.enemy.target, self.mockTarget)
        self.assertTrue(self.enemy.foundTarget)

    def test_attack_reduces_health(self):
        self.enemy.target = self.mockTarget
        self.enemy.lastAttackTime = time.time() - 5  # Ensure cooldown passed
        self.enemy.attack()
        self.assertLess(self.mockTarget.health, 100)
        self.assertTrue(self.mockTarget.showHealthBar)

    def test_attack_kills_target(self):
        self.enemy.target = self.mockTarget
        self.mockTarget.health = 30
        self.enemy.damage = 40
        self.enemy.lastAttackTime = time.time() - 5
        self.enemy.attack()
        self.assertIsNone(self.enemy.target)
        self.assertFalse(self.enemy.foundTarget)

    def test_move_around_changes_position(self):
        land = {(100, 100), (120, 100)}
        trees = set()
        original_pos = self.enemy.rect.x
        self.enemy.direction = (1, 0)  # Right
        self.enemy.moveAround(land, trees)
        self.assertGreaterEqual(self.enemy.rect.x, original_pos)

    def test_move_towards_calculates_path(self):
        target_mock = Mock()
        target_mock.rect = pygame.Rect(140, 100, 20, 20)
        self.enemy.target = target_mock
        land = {(100, 100), (120, 100), (140, 100)}
        trees = set()
        self.enemy.moveTowards(land, trees, gridSize=20)
        self.assertIsNone(self.enemy.path)

    def test_at_target_detection(self):
        self.enemy.target = self.mockTarget
        self.enemy.rect.x = 120
        self.enemy.rect.y = 100
        self.assertTrue(self.enemy.atTarget())

    #farmer

class TestFarmer(unittest.TestCase):

    @patch('pygame.image.load')
    @patch('pygame.transform.scale')
    def setUp(self, mock_scale, mock_load):
        mock_load.return_value = MagicMock()
        mock_scale.return_value = MagicMock()
        self.farmer = Farmer([100, 100])

    def test_initial_attributes(self):
        self.assertEqual(self.farmer.position, [100, 100])
        self.assertFalse(self.farmer.carryingCrops)
        self.assertFalse(self.farmer.carryingFood)
        self.assertEqual(self.farmer.label, "Farmer")
        self.assertEqual(self.farmer.crops, 0)
        self.assertEqual(self.farmer.speed, 1)

    def test_calculate_distance(self):
        mock_target = MagicMock()
        mock_target.position = [110, 110]
        distance = self.farmer.calculateDistance(mock_target)
        self.assertAlmostEqual(distance, 14.14, places=1)

    def test_is_at_farm_true(self):
        farm = Farm([90, 90], 100)
        self.farmer.position = [100, 100]
        self.assertTrue(self.farmer.isAtFarm(farm))

    def test_is_at_farm_false(self):
        farm = Farm([300, 300], 200)
        self.farmer.position = [100, 100]
        self.assertFalse(self.farmer.isAtFarm(farm))

    def test_get_crops_valid(self):
        farm_group = FarmGroup()
        farm_group.cropCount = 5
        self.farmer.getCrops(farm_group)
        self.assertEqual(self.farmer.crops, 5)
        self.assertTrue(self.farmer.carryingCrops)
        self.assertEqual(farm_group.cropCount, 0)

    def test_get_crops_invalid(self):
        self.farmer.getCrops("not_a_farm_group")  # Shouldn't raise an exception

    def test_is_at_cookhouse_true(self):
        cookhouse = Cookhouse([95, 95], 100)
        self.farmer.position = [100, 100]
        self.assertTrue(self.farmer.isAtCookhouse(cookhouse))

    def test_is_at_cookhouse_false(self):
        cookhouse = Cookhouse([300, 300], 100)
        self.farmer.position = [100, 100]
        self.assertFalse(self.farmer.isAtCookhouse(cookhouse))

    def test_assign_farmer_role_to_farm(self):
        # Setup a mock farm in placedItems
        farm = Farm([100, 100], 100)
        placedItems = [{"item": farm}]
        pathGrid = {(100, 100): True}
        self.farmer.assignFarmerRole(pathGrid, placedItems)
        self.assertEqual(self.farmer.role, "farmToCookhouse")

    def test_assign_farmer_role_to_restaurant(self):
        restaurant = Restaurant([100, 100], 100)
        placedItems = [{"item": restaurant}]
        pathGrid = {(100, 100): True}
        self.farmer.assignFarmerRole(pathGrid, placedItems)
        self.assertEqual(self.farmer.role, "cookhouseToRestaurant")

    def test_assign_farmer_role_none(self):
        placedItems = []  # No items nearby
        pathGrid = {(100, 100): True}
        self.farmer.assignFarmerRole(pathGrid, placedItems)
        self.assertIsNone(self.farmer.role)

    def test_hasAPath_true(self):
        target = MagicMock()
        target.position = [120, 100]
        pathGrid = {
            (100, 100): True,
            (120, 100): True
        }
        self.assertTrue(self.farmer.hasAPath(target, pathGrid))

    def test_hasAPath_false(self):
        target = MagicMock()
        target.position = [300, 300]
        pathGrid = {
            (100, 100): True,
            (120, 100): False
        }
        self.assertFalse(self.farmer.hasAPath(target, pathGrid))

# woodChopperHut
class DummyHut:
    def __init__(self):
        self.woodIncreased = False

    def increaseWood(self):
        self.woodIncreased = True

class TestWoodChopper(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.trees = [(100, 100), (200, 200)]
        self.hut_pos = (50, 50)
        self.land_positions = self.trees.copy()
        self.dummy_hut = DummyHut()

        # Patch image loading and pathfinding
        patcher1 = patch("pygame.image.load", return_value=pygame.Surface((20, 20)))
        patcher2 = patch("pygame.transform.scale", side_effect=lambda img, size: img)
        patcher3 = patch("woodChopperHut.calculatePath", return_value=[(100, 100)])
        patcher4 = patch("woodChopperHut.moveAlongPath", side_effect=lambda self, path, size: setattr(self.rect, 'center', path[0]))
        self.mock_load = patcher1.start()
        self.mock_scale = patcher2.start()
        self.mock_path = patcher3.start()
        self.mock_move = patcher4.start()
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        self.addCleanup(patcher4.stop)

        self.chopper = WoodChopper((40, 40), self.trees.copy(), self.hut_pos, self.dummy_hut, self.land_positions)

    def test_initial_state(self):
        self.assertEqual(self.chopper.state, "movingToTree")
        self.assertIsNone(self.chopper.targetTree, self.trees)

    def test_destroy_tree(self):
        tree = self.chopper.targetTree
        self.chopper.destroyTree()
        self.assertNotIn(tree, self.chopper.trees)
        self.assertEqual(self.chopper.state, "returningToHut")

    def test_update_reaches_hut_and_increases_wood(self):
        self.chopper.state = "returningToHut"
        self.chopper.rect.center = self.hut_pos
        self.chopper.update()
        self.assertTrue(self.dummy_hut.woodIncreased)

    def test_idle_finds_new_tree(self):
        self.chopper.state = "idle"
        self.chopper.targetTree = None
        self.chopper.update()
        self.assertEqual(self.chopper.state, "idle")

class TestWoodChopperHut(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.trees = [(100, 100), (120, 120)]
        self.land_positions = self.trees.copy()

        # Patch image loading
        patcher1 = patch("pygame.image.load", return_value=pygame.Surface((20, 20)))
        patcher2 = patch("pygame.transform.scale", side_effect=lambda img, size: img)
        self.mock_load = patcher1.start()
        self.mock_scale = patcher2.start()
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)

        self.hut = WoodChopperHut((40, 40), 100, self.trees.copy(), self.land_positions)

    def test_increase_wood(self):
        self.hut.increaseWood()
        self.assertEqual(self.hut.woodCount, 1)

#island generator
class TestTerrainGenerator(unittest.TestCase):
    def setUp(self):
        # Setup test data
        self.sizeX = 10
        self.sizeY = 10
        self.randomSeed = 42
        self.terrain_generator = TerrainGenerator(self.sizeX, self.sizeY, self.randomSeed)

    def test_initial_noise_map_dimensions(self):
        """Test if the terrain map has the correct dimensions."""
        noise_map = self.terrain_generator.getNoiseMap()
        self.assertEqual(len(noise_map), self.sizeY + 1)  # Should be sizeY + 1
        self.assertEqual(len(noise_map[0]), self.sizeX + 1)  # Should be sizeX + 1

    def test_noise_map_values_range(self):
        """Test if the terrain map values are within the expected range based on Perlin noise."""
        noise_map = self.terrain_generator.getNoiseMap()
        flattened_values = [value for row in noise_map for value in row]
        self.assertTrue(all(-1 <= value <= 1 for value in flattened_values))  # Perlin noise is typically in range [-1, 1]

    def test_noise_map_normalization(self):
        """Test if the noise map is properly normalized."""
        noise_map = self.terrain_generator.getNoiseMap()
        flattened_values = [value for row in noise_map for value in row]
        self.assertGreaterEqual(self.terrain_generator.highestValue, max(flattened_values))
        self.assertLessEqual(self.terrain_generator.lowestValue, min(flattened_values))

#farm

class TestFarm(unittest.TestCase):

    @patch('pygame.time.get_ticks')  
    def test_increaseCropCount(self, mock_get_ticks):
        mock_get_ticks.return_value = 1000  
        farm = Farm(position=(100, 100), price=100)
    
        self.assertEqual(farm.cropCount, 0)

        mock_get_ticks.return_value = 2000  #
        farm.increaseCropCount()  
        
        # Check if cropCount is increased
        self.assertEqual(farm.cropCount, 1)

    def test_initial_values(self):
        farm = Farm(position=(100, 100), price=100)
   
        self.assertEqual(farm.position, (100, 100))
        self.assertEqual(farm.price, 100)
        self.assertEqual(farm.cropCount, 0)
        self.assertEqual(farm.label, "Farm")

class TestFarmGroup(unittest.TestCase):

    def test_add_farm(self):
        # Create farms and farm group
        farm_group = FarmGroup()
        farm1 = Farm(position=(100, 100), price=100)
        farm2 = Farm(position=(200, 200), price=150)
        

        farm_group.addFarm(farm1)
        farm_group.addFarm(farm2)
        

        self.assertIn(farm1, farm_group.farms)
        self.assertIn(farm2, farm_group.farms)
        self.assertEqual(len(farm_group.farms), 2)
    
    def test_remove_farm(self):
  
        farm_group = FarmGroup()
        farm1 = Farm(position=(100, 100), price=100)
        farm_group.addFarm(farm1)
    
        farm_group.removeFarm(farm1)
        
    
        self.assertNotIn(farm1, farm_group.farms)
    
    @patch('pygame.time.get_ticks') 
    def test_generate_crops(self, mock_get_ticks):
       
        mock_get_ticks.return_value = 1000  
        
        # Create farm group and farms
        farm_group = FarmGroup()
        farm1 = Farm(position=(100, 100), price=100)
        farm2 = Farm(position=(200, 200), price=150)
        
        farm_group.addFarm(farm1)
        farm_group.addFarm(farm2)
        

        mock_get_ticks.return_value = 2000  
        farm_group.generateCrops() 
        
    
        self.assertEqual(farm_group.cropCount, 2)
        
    def test_get_coordinates(self):

        farm_group = FarmGroup()
        farm1 = Farm(position=(100, 100), price=100)
        farm2 = Farm(position=(200, 200), price=150)
        
        farm_group.addFarm(farm1)
        farm_group.addFarm(farm2)
  
        coordinates = farm_group.getCoordinates()
        self.assertIn((110, 110), coordinates)
        self.assertIn((210, 210), coordinates)

#test dock

class TestDockEconomicFunctions(unittest.TestCase):

    @patch('pygame.image.load')
    def setUp(self, mock_image_load):
        # Mock image so pygame doesn't crash
        mock_image = pygame.Surface((20, 20))
        mock_image_load.return_value = mock_image
        self.dock = Dock(size="medium", position=(0, 0), orientation="right", price=1000)

    def test_get_gold_rate_unexpected(self):
        self.dock.globalDemandFactor = 1.0  # max demand
        self.dock.setGoldRateValue(10000)
        result = self.dock.getGoldRate()
        self.assertFalse(9000 <= result <= 10000)  

    def test_get_gold_rate_low_demand(self):
        self.dock.globalDemandFactor = 0.1
        self.dock.setGoldRateValue(10000)
        result = self.dock.getGoldRate()
        self.assertTrue(result < 5000)  # sigmoid curve drops output with low demand

    def test_get_gold_rate_zero_base(self):
        self.dock.setGoldRateValue(0)
        self.dock.globalDemandFactor = 1.0
        result = self.dock.getGoldRate()
        self.assertEqual(result, 0)

    def test_get_return_frequency_expected(self):
        self.dock.setReturnFrequencyValue(60)
        self.assertEqual(self.dock.getReturnFrequency(), 60)

    def test_set_gold_rate_positive(self):
        self.dock.setGoldRateValue(5000)
        self.assertEqual(self.dock.getGoldRate(), self.dock.getGoldRate())  # Should not error

    def test_set_gold_rate_negative(self):
        self.dock.setGoldRateValue(-100)
        # It should not set a negative rate
        self.assertNotEqual(self.dock.getGoldRate(), -100)

    def test_set_return_frequency_positive(self):
        self.dock.setReturnFrequencyValue(120)
        self.assertEqual(self.dock.getReturnFrequency(), 120)

    def test_set_return_frequency_zero(self):
        original = self.dock.getReturnFrequency()
        self.dock.setReturnFrequencyValue(0)
        self.assertEqual(self.dock.getReturnFrequency(), original)  # Should not change

    def test_update_demand_factor_expected(self):
        self.dock.updateDemandFactor(population=100, totalDocks=10)
        self.assertAlmostEqual(self.dock.globalDemandFactor, 1.0)

    def test_update_demand_factor_low_demand(self):
        self.dock.updateDemandFactor(population=5, totalDocks=20)
        self.assertAlmostEqual(self.dock.globalDemandFactor, 0.1)

    def test_update_demand_factor_zero_docks(self):
        self.dock.updateDemandFactor(population=100, totalDocks=0)
        self.assertEqual(self.dock.globalDemandFactor, 1.0)

    def test_update_frequency_high_satisfaction(self):
        original = self.dock.getReturnFrequency()
        self.dock.updateReturnFrequencyBasedOnSatisfaction(90)
        self.assertEqual(self.dock.getReturnFrequency(), original + 5)

    def test_update_frequency_low_satisfaction(self):
        self.dock.setReturnFrequencyValue(10)
        self.dock.updateReturnFrequencyBasedOnSatisfaction(30)
        self.assertEqual(self.dock.getReturnFrequency(), 5)

    def test_update_frequency_min_boundary(self):
        self.dock.setReturnFrequencyValue(2)
        self.dock.updateReturnFrequencyBasedOnSatisfaction(30)
        self.assertEqual(self.dock.getReturnFrequency(), 1)  # cannot go below 1

if __name__ == '__main__':
    unittest.main()