import pygame
import random
from block import Block, Soil
from item import Item
from character import Character

# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MOVE_SPEED = 2
FONT = pygame.font.Font(None, 24)
INVENTORY_WIDTH = 200
INVENTORY_HEIGHT = 300
INVENTORY_BG_COLOR = (220, 220, 220)
TIP_BG_COLOR = (255, 255, 200)
HIGHLIGHT_COLOR = (255, 0, 0)  # Color for highlighting the land

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
                target_block = None
                # 精确查找玩家所在的土地块
                for block in blocks:
                    if block.position == (player_tile_x, player_tile_y):
                        target_block = block
                        break
                if target_block:
                    print(f"Found target block at position: {target_block.position}")
                    if any(item.id == 1 for item in player.inventory):  # Has a hoe
                        print(f"Cultivating land at {target_block.position}")
                        target_block.change_state(1)  # Cultivate the land
                    elif any(item.id == 2 for item in player.inventory) and target_block.state == 1:
                        target_block.plant_crop(seed)  # Plant a crop
                    elif target_block.plant != 0 and target_block.growth_stage == 5:
                        harvested = target_block.harvest()
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
