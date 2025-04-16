import pygame
import random
from block import Block, Soil
from item import Item, ItemType, Plant
from character import Character

# 初始化 Pygame
pygame.init()

# 定义常量
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
HIGHLIGHT_COLOR = (255, 0, 0)

# 创建屏幕
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Stardew Valley")

# Create a character instance
player = Character("Player", WIDTH // 2, HEIGHT // 2)

# 定义小麦种子
wheat_seed = Item(2, "Wheat Seed", "A seed for planting wheat")
# 定义小麦产品
wheat_product = Item(5, "Wheat", "Mature wheat, can be sold or used")
# 定义小麦植物
wheat = Plant(4, "Wheat Plant", wheat_seed, 100, wheat_product, 5)

# 定义工具
hoe = Item(1, "Hoe", ItemType.TOOL, "Used to cultivate land")

# 添加物品到玩家背包
player.add_item(hoe)
player.add_item(wheat_seed)

# 创建土地块列表
blocks = []
for y in range(0, HEIGHT, TILE_SIZE):
    for x in range(0, WIDTH, TILE_SIZE):
        block = Soil((x, y))
        blocks.append(block)

# 游戏主循环
running = True
clock = pygame.time.Clock()
grow_timer = 0
is_inventory_open = False


def draw_player(screen, x, y):
    # 绘制头部，用圆形表示
    head_radius = TILE_SIZE // 4
    pygame.draw.circle(screen, (255, 204, 153), (x + TILE_SIZE // 2, y + head_radius), head_radius)

    # 绘制身体，用矩形表示
    body_height = TILE_SIZE // 2
    pygame.draw.rect(screen, (0, 0, 255), (x + TILE_SIZE // 4, y + 2 * head_radius, TILE_SIZE // 2, body_height))

    # 绘制手臂
    arm_length = TILE_SIZE // 3
    pygame.draw.line(screen, (255, 204, 153), (x + TILE_SIZE // 4, y + 2 * head_radius + body_height // 3),
                     (x + TILE_SIZE // 4 - arm_length, y + 2 * head_radius + body_height // 3), 3)
    pygame.draw.line(screen, (255, 204, 153), (x + 3 * TILE_SIZE // 4, y + 2 * head_radius + body_height // 3),
                     (x + 3 * TILE_SIZE // 4 + arm_length, y + 2 * head_radius + body_height // 3), 3)

    # 绘制腿部
    leg_length = TILE_SIZE // 3
    pygame.draw.line(screen, (0, 0, 0), (x + TILE_SIZE // 3, y + 2 * head_radius + body_height),
                     (x + TILE_SIZE // 3, y + 2 * head_radius + body_height + leg_length), 3)
    pygame.draw.line(screen, (0, 0, 0), (x + 2 * TILE_SIZE // 3, y + 2 * head_radius + body_height),
                     (x + 2 * TILE_SIZE // 3, y + 2 * head_radius + body_height + leg_length), 3)


while running:
    current_time = pygame.time.get_ticks()  # 每次循环获取当前时间
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 获取玩家当前所在的土地块
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
                    land_state = target_block.state
                    has_hoe = any(item.id == 1 for item in player.inventory)
                    has_wheat_seed = any(item.id == 2 for item in player.inventory)

                    if land_state == 0:  # 土地未开垦
                        if has_hoe:
                            target_block.cultivate()
                    elif land_state == 1 and target_block.plant is None:  # 开垦未播种
                        if has_wheat_seed:
                            target_block.plant_crop(wheat, current_time)
                            # 从背包移除种子
                            for item in player.inventory[:]:
                                if item.id == 2:
                                    player.inventory.remove(item)
                                    break
                    else:
                        harvested = target_block.harvest()
                        if harvested:
                            player.add_item(harvested.product_item)
                            # 随机生成 1 - 2 个种子
                            seed_count = random.randint(harvested.seed_harvested_min, harvested.seed_harvested_max)
                            for _ in range(seed_count):
                                player.add_item(harvested.seed)
                            print(f"Harvested {harvested} and {seed_count} {harvested.seed}")
            elif event.key == pygame.K_e:
                is_inventory_open = not is_inventory_open

    # 处理按键事件，使用 WASD 控制移动
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player.x > 0:
        player.x -= MOVE_SPEED
    if keys[pygame.K_d] and player.x < WIDTH - TILE_SIZE:
        player.x += MOVE_SPEED
    if keys[pygame.K_w] and player.y > 0:
        player.y -= MOVE_SPEED
    if keys[pygame.K_s] and player.y < HEIGHT - TILE_SIZE:
        player.y += MOVE_SPEED

    # 植物生长逻辑
    for block in blocks:
        if isinstance(block, Soil):
            block.grow(current_time)  # 传入当前时间

    # 绘制背景
    screen.fill(WHITE)

    # 绘制土地块
    for block in blocks:
        block.draw(screen)

    # Draw the player
    draw_player(screen, player.x, player.y)

    # 高亮显示玩家当前所在的土地块
    player_tile_x = player.x // TILE_SIZE * TILE_SIZE
    player_tile_y = player.y // TILE_SIZE * TILE_SIZE
    for block in blocks:
        if block.position == (player_tile_x, player_tile_y):
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (player_tile_x, player_tile_y, TILE_SIZE, TILE_SIZE), 3)

    # 显示背包界面
    if is_inventory_open:
        pygame.draw.rect(screen, INVENTORY_BG_COLOR, (WIDTH - INVENTORY_WIDTH - 10, 10, INVENTORY_WIDTH, INVENTORY_HEIGHT))
        inventory_y = 20
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_item = None
        for item in player.inventory:
            color = BLACK
            if item.type == ItemType.TOOL:
                color = (0, 0, 255)
            elif item.type == ItemType.SEED:
                color = (0, 128, 0)
            elif item.type == ItemType.PRODUCT:
                color = (139, 69, 19)
            item_text = FONT.render(item.name, True, color)
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

    # 显示按键提示
    controls_text = FONT.render("W: Up, A: Left, S: Down, D: Right, SPACE: Interact, E: Inventory", True, BLACK)
    screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, HEIGHT - 30))

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

# 退出 Pygame
pygame.quit()