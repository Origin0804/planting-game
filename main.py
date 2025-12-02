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
GOLD_COLOR = (255, 215, 0)
MOVE_SPEED = 2
FONT = pygame.font.Font(None, 24)
TITLE_FONT = pygame.font.Font(None, 32)
INVENTORY_WIDTH = 200
INVENTORY_HEIGHT = 300
SHOP_WIDTH = 250
SHOP_HEIGHT = 200
INVENTORY_BG_COLOR = (220, 220, 220)
SHOP_BG_COLOR = (200, 230, 200)
TIP_BG_COLOR = (255, 255, 200)
HIGHLIGHT_COLOR = (255, 0, 0)

# 创建屏幕
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Stardew Valley v1.1")

# Create a character instance
player = Character("Player", WIDTH // 2, HEIGHT // 2)

# 定义小麦种子
wheat_seed = Item(2, "Wheat Seed", ItemType.SEED, "A seed for planting wheat")
# 定义小麦产品
wheat_product = Item(5, "Wheat", ItemType.PRODUCT, "Mature wheat, sells for 15 coins")
# 定义小麦植物
wheat = Plant(4, "Wheat Plant", wheat_seed, 100, wheat_product, 5)

# 定义番茄种子
tomato_seed = Item(6, "Tomato Seed", ItemType.SEED, "A seed for planting tomatoes")
# 定义番茄产品
tomato_product = Item(7, "Tomato", ItemType.PRODUCT, "Fresh tomato, sells for 25 coins")
# 定义番茄植物
tomato = Plant(8, "Tomato Plant", tomato_seed, 150, tomato_product, 6)

# 定义玉米种子
corn_seed = Item(9, "Corn Seed", ItemType.SEED, "A seed for planting corn")
# 定义玉米产品
corn_product = Item(10, "Corn", ItemType.PRODUCT, "Golden corn, sells for 35 coins")
# 定义玉米植物
corn = Plant(11, "Corn Plant", corn_seed, 200, corn_product, 7)

# 定义工具
hoe = Item(1, "Hoe", ItemType.TOOL, "Used to cultivate land")

# 商店物品价格
SHOP_ITEMS = {
    "Wheat Seed": {"item": wheat_seed, "price": 10, "plant": wheat},
    "Tomato Seed": {"item": tomato_seed, "price": 20, "plant": tomato},
    "Corn Seed": {"item": corn_seed, "price": 30, "plant": corn},
}

# 产品售价
SELL_PRICES = {
    5: 15,   # Wheat
    7: 25,   # Tomato
    10: 35,  # Corn
}

# 添加物品到玩家背包
player.add_item(hoe)
player.add_item(wheat_seed)
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
is_shop_open = False
selected_seed_type = "Wheat Seed"  # 当前选中的种子类型


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


def count_inventory_items(inventory):
    """统计背包中每种物品的数量"""
    item_counts = {}
    for item in inventory:
        key = (item.id, item.name)
        if key not in item_counts:
            item_counts[key] = {"item": item, "count": 0}
        item_counts[key]["count"] += 1
    return item_counts


while running:
    current_time = pygame.time.get_ticks()  # 每次循环获取当前时间
    mouse_x, mouse_y = pygame.mouse.get_pos()  # 获取鼠标位置（每帧只获取一次）
    
    # 预计算物品计数（用于商店和背包显示）
    item_counts = count_inventory_items(player.inventory)
    
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
                    
                    # 检查背包中的所有种子类型
                    available_seeds = {}
                    for seed_name, seed_info in SHOP_ITEMS.items():
                        seed_item = seed_info["item"]
                        if any(item.id == seed_item.id for item in player.inventory):
                            available_seeds[seed_name] = seed_info

                    if land_state == 0:  # 土地未开垦
                        if has_hoe:
                            target_block.cultivate()
                    elif land_state == 1 and target_block.plant is None:  # 开垦未播种
                        # 使用当前选中的种子类型
                        if selected_seed_type in available_seeds:
                            seed_info = available_seeds[selected_seed_type]
                            target_block.plant_crop(seed_info["plant"], current_time)
                            # 从背包移除种子
                            for item in player.inventory[:]:
                                if item.id == seed_info["item"].id:
                                    player.inventory.remove(item)
                                    break
                            print(f"Planted {selected_seed_type}")
                    else:
                        harvested = target_block.harvest()
                        if harvested:
                            player.add_item(harvested.product_item)
                            # 获得金币
                            if harvested.product_item.id in SELL_PRICES:
                                coins_earned = SELL_PRICES[harvested.product_item.id]
                                player.add_coins(coins_earned)
                                print(f"Earned {coins_earned} coins!")
                            # 随机生成 1 - 2 个种子
                            seed_count = random.randint(harvested.seed_harvested_min, harvested.seed_harvested_max)
                            for _ in range(seed_count):
                                player.add_item(harvested.seed)
                            print(f"Harvested {harvested.name} and {seed_count} seeds")
            elif event.key == pygame.K_e:
                is_inventory_open = not is_inventory_open
                if is_inventory_open:
                    is_shop_open = False
            elif event.key == pygame.K_b:
                is_shop_open = not is_shop_open
                if is_shop_open:
                    is_inventory_open = False
            elif event.key == pygame.K_1:
                selected_seed_type = "Wheat Seed"
                print(f"Selected: {selected_seed_type}")
            elif event.key == pygame.K_2:
                selected_seed_type = "Tomato Seed"
                print(f"Selected: {selected_seed_type}")
            elif event.key == pygame.K_3:
                selected_seed_type = "Corn Seed"
                print(f"Selected: {selected_seed_type}")
        elif event.type == pygame.MOUSEBUTTONDOWN and is_shop_open:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # 检查点击是否在商店区域
            shop_x = 10
            shop_y = 50
            item_y = shop_y + 30
            for seed_name, seed_info in SHOP_ITEMS.items():
                item_rect = pygame.Rect(shop_x, item_y, SHOP_WIDTH - 20, 25)
                if item_rect.collidepoint(mouse_x, mouse_y):
                    # 购买种子
                    price = seed_info["price"]
                    if player.spend_coins(price):
                        # 创建新的种子实例
                        new_seed = Item(seed_info["item"].id, seed_info["item"].name, 
                                      seed_info["item"].type, seed_info["item"].description)
                        player.add_item(new_seed)
                        print(f"Bought {seed_name} for {price} coins")
                    else:
                        print(f"Not enough coins to buy {seed_name}")
                item_y += 30

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

    # 显示金币数量
    coins_text = TITLE_FONT.render(f"Coins: {player.coins}", True, GOLD_COLOR)
    pygame.draw.rect(screen, (50, 50, 50), (5, 5, coins_text.get_width() + 10, coins_text.get_height() + 6))
    screen.blit(coins_text, (10, 8))

    # 显示当前选中的种子类型
    seed_text = FONT.render(f"Selected: {selected_seed_type} (1-3 to change)", True, BLACK)
    pygame.draw.rect(screen, TIP_BG_COLOR, (5, 35, seed_text.get_width() + 10, seed_text.get_height() + 4))
    screen.blit(seed_text, (10, 37))

    # 显示商店界面
    if is_shop_open:
        shop_x = 10
        shop_y = 50
        pygame.draw.rect(screen, SHOP_BG_COLOR, (shop_x, shop_y, SHOP_WIDTH, SHOP_HEIGHT))
        pygame.draw.rect(screen, BLACK, (shop_x, shop_y, SHOP_WIDTH, SHOP_HEIGHT), 2)
        
        title_text = TITLE_FONT.render("SHOP (Click to buy)", True, BLACK)
        screen.blit(title_text, (shop_x + 10, shop_y + 5))
        
        item_y = shop_y + 30
        for seed_name, seed_info in SHOP_ITEMS.items():
            price = seed_info["price"]
            item_rect = pygame.Rect(shop_x + 5, item_y, SHOP_WIDTH - 10, 25)
            
            # 高亮悬停的物品
            if item_rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(screen, (180, 210, 180), item_rect)
            
            color = (0, 128, 0) if player.coins >= price else (128, 128, 128)
            item_text = FONT.render(f"{seed_name}: {price} coins", True, color)
            screen.blit(item_text, (shop_x + 10, item_y + 3))
            item_y += 30
        
        # 显示种子数量（使用预计算的物品计数）
        item_y += 10
        count_title = FONT.render("Your seeds:", True, BLACK)
        screen.blit(count_title, (shop_x + 10, item_y))
        item_y += 20
        for seed_name, seed_info in SHOP_ITEMS.items():
            seed_id = seed_info["item"].id
            count = sum(data["count"] for (item_id, _), data in item_counts.items() if item_id == seed_id)
            count_text = FONT.render(f"  {seed_name}: {count}", True, BLACK)
            screen.blit(count_text, (shop_x + 10, item_y))
            item_y += 18

    # 显示背包界面
    if is_inventory_open:
        pygame.draw.rect(screen, INVENTORY_BG_COLOR, (WIDTH - INVENTORY_WIDTH - 10, 10, INVENTORY_WIDTH, INVENTORY_HEIGHT))
        pygame.draw.rect(screen, BLACK, (WIDTH - INVENTORY_WIDTH - 10, 10, INVENTORY_WIDTH, INVENTORY_HEIGHT), 2)
        
        title_text = TITLE_FONT.render("INVENTORY", True, BLACK)
        screen.blit(title_text, (WIDTH - INVENTORY_WIDTH, 15))
        
        inventory_y = 45
        hovered_item = None
        
        # 使用预计算的物品计数
        for key, data in item_counts.items():
            item = data["item"]
            count = data["count"]
            color = BLACK
            if item.type == ItemType.TOOL:
                color = (0, 0, 255)
            elif item.type == ItemType.SEED:
                color = (0, 128, 0)
            elif item.type == ItemType.PRODUCT:
                color = (139, 69, 19)
            
            display_text = f"{item.name}"
            if count > 1:
                display_text += f" x{count}"
            
            item_text = FONT.render(display_text, True, color)
            item_rect = item_text.get_rect(topleft=(WIDTH - INVENTORY_WIDTH, inventory_y))
            screen.blit(item_text, item_rect)
            if item_rect.collidepoint(mouse_x, mouse_y):
                hovered_item = item
            inventory_y += 25

        if hovered_item:
            desc_text = FONT.render(hovered_item.description, True, BLACK)
            desc_rect = desc_text.get_rect(topleft=(WIDTH - INVENTORY_WIDTH, inventory_y + 10))
            pygame.draw.rect(screen, TIP_BG_COLOR, desc_rect.inflate(10, 5))
            screen.blit(desc_text, desc_rect)

    # 显示按键提示
    controls_text = FONT.render("WASD: Move | SPACE: Interact | E: Inventory | B: Shop | 1-3: Select Seed", True, BLACK)
    screen.blit(controls_text, (WIDTH - controls_text.get_width() - 10, HEIGHT - 30))

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

# 退出 Pygame
pygame.quit()