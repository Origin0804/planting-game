import pygame
import random

# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LAND_COLOR = (139, 69, 19)  # Land color
CULTIVATED_COLOR = (160, 82, 45)  # Cultivated land color
PLANT_COLOR = (0, 128, 0)  # Plant color
MOVE_SPEED = 2
FONT = pygame.font.Font(None, 24)
INVENTORY_WIDTH = 200
INVENTORY_HEIGHT = 300
INVENTORY_BG_COLOR = (220, 220, 220)
TIP_BG_COLOR = (255, 255, 200)
HIGHLIGHT_COLOR = (255, 0, 0)  # Color for highlighting the land

# Define the Block class
class Block:
    def __init__(self, position, state=0):
        """
        Initialize a Block instance
        :param position: The position of the land block, format: (x, y)
        :param state: The state of the land block, default is 0
        """
        self.position = position
        self.state = state

    def change_state(self, new_state):
        """
        Change the state of the land block
        :param new_state: The new state value
        """
        self.state = new_state

    def draw(self, screen):
        """
        Draw the land block on the screen
        :param screen: The game screen object
        """
        x, y = self.position
        if self.state == 0:
            pygame.draw.rect(screen, LAND_COLOR, (x, y, TILE_SIZE, TILE_SIZE), 1)
        elif self.state == 1:
            pygame.draw.rect(screen, CULTIVATED_COLOR, (x, y, TILE_SIZE, TILE_SIZE))


# Define the Soil class
class Soil(Block):
    def __init__(self, position, state=0, plant=0):
        """
        Initialize a Soil instance
        :param position: The position of the land, format: (x, y)
        :param state: The state of the land, 0 for uncultivated, 1 for cultivated, default is 0
        :param plant: The planted crop, 0 for no plant
        """
        super().__init__(position, state)
        self.plant = plant
        self.growth_stage = 0  # Plant growth stage

    def plant_crop(self, new_plant):
        """
        Plant a crop on the land
        :param new_plant: The crop to be planted
        """
        if self.state == 1 and self.plant == 0:
            self.plant = new_plant
            self.growth_stage = 0

    def grow(self):
        """
        The plant grows
        """
        if self.plant != 0:
            self.growth_stage += 1
            if self.growth_stage >= 5:  # Assume the plant matures after 5 growth stages
                self.growth_stage = 5

    def harvest(self):
        """
        Harvest the crop on the land
        :return: The harvested crop, 0 if no crop
        """
        if self.plant != 0 and self.growth_stage == 5:
            harvested_plant = self.plant
            self.plant = 0
            self.growth_stage = 0
            return harvested_plant
        return 0

    def draw(self, screen):
        super().draw(screen)
        if self.plant != 0:
            x, y = self.position
            plant_size = TILE_SIZE * (self.growth_stage / 5)
            pygame.draw.rect(screen, PLANT_COLOR, (x + (TILE_SIZE - plant_size) // 2,
                                                   y + (TILE_SIZE - plant_size) // 2,
                                                   plant_size, plant_size))


# Define the Item class
class Item:
    def __init__(self, item_id, name, description=""):
        """
        Initialize an Item instance
        :param item_id: The unique ID of the item
        :param name: The name of the item
        :param description: The description of the item, default is an empty string
        """
        self.id = item_id
        self.name = name
        self.description = description


# Define the Character class
class Character:
    def __init__(self, name, x, y):
        """
        Initialize a Character instance
        :param name: The name of the character
        :param x: The initial x-coordinate of the character
        :param y: The initial y-coordinate of the character
        """
        self.name = name
        self.x = x
        self.y = y
        self.inventory = []  # Item list

    def add_item(self, item):
        """
        Add an item to the character's inventory
        :param item: The item instance to be added
        """
        self.inventory.append(item)

    def remove_item(self, item_id):
        """
        Remove an item with the specified ID from the character's inventory
        :param item_id: The ID of the item to be removed
        :return: The removed item if successful, None otherwise
        """
        for item in self.inventory:
            if item.id == item_id:
                self.inventory.remove(item)
                return item
        return None

    def get_inventory(self):
        """
        Get the character's inventory
        :return: The character's inventory list
        """
        return self.inventory


# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Stardew Valley")

# Load the character image
player_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
player_image.fill((255, 0, 0))  # Red square represents the character

# Create a character instance
player = Character("Player", WIDTH // 2, HEIGHT // 2)

# Add items to the player's inventory
hoe = Item(1, "Hoe", "A tool for cultivating land")
seed = Item(2, "Seed", "A seed for planting crops")
player.add_item(hoe)
player.add_item(seed)

# Create a list of land blocks
blocks = []
for y in range(0, HEIGHT, TILE_SIZE):
    for x in range(0, WIDTH, TILE_SIZE):
        block = Soil((x, y))
        blocks.append(block)

# Game main loop
running = True
clock = pygame.time.Clock()
grow_timer = 0  # Growth timer
is_inventory_open = False  # Inventory open flag

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Get the land block where the player is currently located
                player_tile_x = player.x // TILE_SIZE * TILE_SIZE
                player_tile_y = player.y // TILE_SIZE * TILE_SIZE
                for block in blocks:
                    if block.position == (player_tile_x, player_tile_y):
                        if any(item.id == 1 for item in player.inventory):  # Has a hoe
                            block.change_state(1)  # Cultivate the land
                        elif any(item.id == 2 for item in player.inventory) and block.state == 1:
                            block.plant_crop(seed)  # Plant a crop
                        elif block.plant != 0 and block.growth_stage == 5:
                            harvested = block.harvest()
                            if harvested:
                                player.add_item(harvested)
            elif event.key == pygame.K_e:
                is_inventory_open = not is_inventory_open

    # Handle key events, use WASD to control movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player.x > 0:
        player.x -= MOVE_SPEED
    if keys[pygame.K_d] and player.x < WIDTH - TILE_SIZE:
        player.x += MOVE_SPEED
    if keys[pygame.K_w] and player.y > 0:
        player.y -= MOVE_SPEED
    if keys[pygame.K_s] and player.y < HEIGHT - TILE_SIZE:
        player.y += MOVE_SPEED

    # Plant growth logic
    grow_timer += clock.get_rawtime()
    if grow_timer >= 5000:  # Grow once every 5 seconds
        for block in blocks:
            if isinstance(block, Soil):
                block.grow()
        grow_timer = 0

    # Draw the background
    screen.fill(WHITE)

    # Draw land blocks
    for block in blocks:
        block.draw(screen)

    # Implement 2.5D effect, simply rotate the character
    rotated_player = pygame.transform.rotate(player_image, 45)
    new_rect = rotated_player.get_rect(center=player_image.get_rect(topleft=(player.x, player.y)).center)
    screen.blit(rotated_player, new_rect.topleft)

    # Highlight the land block where the player is currently located
    player_tile_x = player.x // TILE_SIZE * TILE_SIZE
    player_tile_y = player.y // TILE_SIZE * TILE_SIZE
    for block in blocks:
        if block.position == (player_tile_x, player_tile_y):
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (player_tile_x, player_tile_y, TILE_SIZE, TILE_SIZE), 3)

    # Show the inventory interface
    if is_inventory_open:
        pygame.draw.rect(screen, INVENTORY_BG_COLOR, (WIDTH - INVENTORY_WIDTH - 10, 10, INVENTORY_WIDTH, INVENTORY_HEIGHT))
        inventory_y = 20
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_item = None
        for item in player.inventory:
            item_text = FONT.render(item.name, True, BLACK)
            item_rect = item_text.get_rect(topleft=(WIDTH - INVENTORY_WIDTH, inventory_y))
            screen.blit(item_text, item_rect)
            if item_rect.collidepoint(mouse_x, mouse_y):
                hovered_item = item
            inventory_y += 30

        if hovered_item:
            desc_text = FONT.render(hovered_item.description, True, BLACK)
            desc_rect = desc_text.get_rect(topleft=(WIDTH - INVENTORY_WIDTH, inventory_y))
            pygame.draw.rect(screen, TIP_BG_COLOR, desc_rect.inflate(10, 5))
            screen.blit(desc_text, desc_rect)

    # Show key prompts
    controls_text = FONT.render("W: Up, A: Left, S: Down, D: Right, SPACE: Interact, E: Inventory", True, BLACK)
    screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, HEIGHT - 30))

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
