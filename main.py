import pygame
import random
from block import Block, Soil
from item import Item, ItemType, ItemID, Plant, Season, create_crops
from character import Character

# 初始化 Pygame
pygame.init()

# 定义常量
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MOVE_SPEED = 3
FONT = pygame.font.Font(None, 24)
SMALL_FONT = pygame.font.Font(None, 20)
TITLE_FONT = pygame.font.Font(None, 32)
INVENTORY_WIDTH = 250
INVENTORY_HEIGHT = 350
INVENTORY_BG_COLOR = (220, 220, 220)
TIP_BG_COLOR = (255, 255, 200)
HIGHLIGHT_COLOR = (255, 0, 0)
SHOP_BG_COLOR = (200, 200, 180)
HUD_BG_COLOR = (50, 50, 50, 180)
NOTIFICATION_BG_COLOR = (0, 0, 0)  # 通知背景颜色（黑色，将使用透明表面）
NOTIFICATION_BG_ALPHA = 180  # 通知背景透明度
DEFAULT_SELL_PRICE = 10

# 时间常量（毫秒）
SEASON_DURATION = 120 * 1000  # 120秒换季
DAY_DURATION = 30 * 1000  # 30秒一天

# 季节颜色
SEASON_COLORS = {
    Season.SPRING: (144, 238, 144),  # 浅绿色
    Season.SUMMER: (255, 255, 200),  # 淡黄色
    Season.AUTUMN: (255, 200, 150),  # 橙色
    Season.WINTER: (220, 240, 255),  # 淡蓝色
}

# 创建屏幕
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🌾 Planting Game - 农场物语")

# 创建所有作物
all_crops = create_crops()

# Create a character instance
player = Character("Farmer", WIDTH // 2, HEIGHT // 2, gold=200)

# 定义工具
hoe = Item(ItemID.HOE, "Hoe", ItemType.TOOL, "Used to cultivate land", stackable=False)
watering_can = Item(ItemID.WATERING_CAN, "Watering Can", ItemType.TOOL, "Used to water plants", stackable=False)

# 添加物品到玩家背包
player.add_item(hoe)
player.add_item(watering_can)
player.add_item(all_crops['wheat']['seed'])
player.add_item(all_crops['wheat']['seed'])
player.add_item(all_crops['wheat']['seed'])

# 创建土地块列表
blocks = []
for y in range(0, HEIGHT, TILE_SIZE):
    for x in range(0, WIDTH, TILE_SIZE):
        block = Soil((x, y))
        blocks.append(block)

# 游戏状态
class GameState:
    PLAYING = "playing"
    INVENTORY = "inventory"
    SHOP = "shop"

# 商店物品列表
def get_shop_items():
    items = []
    for crop_name, crop_data in all_crops.items():
        items.append(crop_data['seed'])
    return items

# 游戏变量
running = True
clock = pygame.time.Clock()
game_state = GameState.PLAYING
current_season = Season.SPRING
season_timer = 0
day_count = 1
day_timer = 0
shop_scroll = 0
notification_text = ""
notification_timer = 0

# 季节列表
SEASONS = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]
current_season_index = 0


def get_plant_for_seed(seed):
    """根据种子获取对应的植物"""
    for crop_name, crop_data in all_crops.items():
        if crop_data['seed'].id == seed.id:
            return crop_data['plant']
    return None


def show_notification(text):
    """显示通知消息"""
    global notification_text, notification_timer
    notification_text = text
    notification_timer = 2000  # 显示2秒


def draw_player(screen, x, y, direction):
    """绘制玩家角色，根据朝向变化"""
    # 绘制头部，用圆形表示
    head_radius = TILE_SIZE // 4
    head_x = x + TILE_SIZE // 2
    head_y = y + head_radius
    pygame.draw.circle(screen, (255, 204, 153), (head_x, head_y), head_radius)
    
    # 绘制眼睛（根据朝向）
    eye_size = 3
    if direction == "up":
        # 背对着，不画眼睛
        pass
    elif direction == "down":
        pygame.draw.circle(screen, BLACK, (head_x - 4, head_y - 2), eye_size)
        pygame.draw.circle(screen, BLACK, (head_x + 4, head_y - 2), eye_size)
    elif direction == "left":
        pygame.draw.circle(screen, BLACK, (head_x - 5, head_y - 2), eye_size)
    elif direction == "right":
        pygame.draw.circle(screen, BLACK, (head_x + 5, head_y - 2), eye_size)

    # 绘制身体，用矩形表示
    body_height = TILE_SIZE // 2
    pygame.draw.rect(screen, (0, 100, 200), (x + TILE_SIZE // 4, y + 2 * head_radius, TILE_SIZE // 2, body_height))

    # 绘制手臂（根据朝向调整）
    arm_length = TILE_SIZE // 3
    arm_y = y + 2 * head_radius + body_height // 3
    
    if direction == "left":
        # 左手在前
        pygame.draw.line(screen, (255, 204, 153), (x + TILE_SIZE // 4, arm_y),
                        (x + TILE_SIZE // 4 - arm_length - 3, arm_y), 3)
        pygame.draw.line(screen, (255, 204, 153), (x + 3 * TILE_SIZE // 4, arm_y),
                        (x + 3 * TILE_SIZE // 4 + arm_length - 5, arm_y - 5), 3)
    elif direction == "right":
        # 右手在前
        pygame.draw.line(screen, (255, 204, 153), (x + TILE_SIZE // 4, arm_y),
                        (x + TILE_SIZE // 4 - arm_length + 5, arm_y - 5), 3)
        pygame.draw.line(screen, (255, 204, 153), (x + 3 * TILE_SIZE // 4, arm_y),
                        (x + 3 * TILE_SIZE // 4 + arm_length + 3, arm_y), 3)
    else:
        pygame.draw.line(screen, (255, 204, 153), (x + TILE_SIZE // 4, arm_y),
                        (x + TILE_SIZE // 4 - arm_length, arm_y), 3)
        pygame.draw.line(screen, (255, 204, 153), (x + 3 * TILE_SIZE // 4, arm_y),
                        (x + 3 * TILE_SIZE // 4 + arm_length, arm_y), 3)

    # 绘制腿部
    leg_length = TILE_SIZE // 3
    leg_y = y + 2 * head_radius + body_height
    pygame.draw.line(screen, (50, 50, 50), (x + TILE_SIZE // 3, leg_y),
                    (x + TILE_SIZE // 3, leg_y + leg_length), 3)
    pygame.draw.line(screen, (50, 50, 50), (x + 2 * TILE_SIZE // 3, leg_y),
                    (x + 2 * TILE_SIZE // 3, leg_y + leg_length), 3)


def draw_hud(screen):
    """绘制 HUD（平视显示器）"""
    # 绘制顶部 HUD 背景
    hud_surface = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
    hud_surface.fill((50, 50, 50, 200))
    screen.blit(hud_surface, (0, 0))
    
    # 金币显示
    gold_text = FONT.render(f"💰 Gold: {player.gold}", True, (255, 215, 0))
    screen.blit(gold_text, (10, 10))
    
    # 季节和天数显示
    season_text = FONT.render(f"🌿 {current_season} | Day {day_count}", True, WHITE)
    screen.blit(season_text, (WIDTH // 2 - season_text.get_width() // 2, 10))
    
    # 当前选择的种子
    selected_seed = player.get_selected_seed()
    if selected_seed:
        seed_text = FONT.render(f"🌱 Selected: {selected_seed.name}", True, (100, 255, 100))
        screen.blit(seed_text, (WIDTH - seed_text.get_width() - 10, 10))


def draw_inventory(screen):
    """绘制背包界面"""
    # 背景
    inv_x = WIDTH // 2 - INVENTORY_WIDTH // 2
    inv_y = HEIGHT // 2 - INVENTORY_HEIGHT // 2
    pygame.draw.rect(screen, INVENTORY_BG_COLOR, (inv_x, inv_y, INVENTORY_WIDTH, INVENTORY_HEIGHT))
    pygame.draw.rect(screen, BLACK, (inv_x, inv_y, INVENTORY_WIDTH, INVENTORY_HEIGHT), 2)
    
    # 标题
    title = TITLE_FONT.render("📦 Inventory", True, BLACK)
    screen.blit(title, (inv_x + INVENTORY_WIDTH // 2 - title.get_width() // 2, inv_y + 10))
    
    # 金币显示
    gold_text = FONT.render(f"💰 Gold: {player.gold}", True, (139, 69, 19))
    screen.blit(gold_text, (inv_x + 10, inv_y + 45))
    
    # 物品列表
    item_y = inv_y + 75
    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered_item = None
    
    for inv_item in player.inventory:
        item = inv_item['item']
        count = inv_item['count']
        
        # 物品颜色根据类型变化
        color = BLACK
        if item.type == ItemType.TOOL:
            color = (70, 130, 180)  # 钢蓝色
        elif item.type == ItemType.SEED:
            color = (34, 139, 34)  # 森林绿
        elif item.type == ItemType.PRODUCT:
            color = (139, 69, 19)  # 棕色
        
        # 显示物品名称和数量
        item_text = f"{item.name} x{count}"
        text_surface = FONT.render(item_text, True, color)
        text_rect = text_surface.get_rect(topleft=(inv_x + 15, item_y))
        screen.blit(text_surface, text_rect)
        
        # 检查悬停
        if text_rect.collidepoint(mouse_x, mouse_y):
            hovered_item = item
        
        item_y += 28
        if item_y > inv_y + INVENTORY_HEIGHT - 60:
            break
    
    # 显示悬停物品的描述和价格
    if hovered_item:
        desc = hovered_item.description
        if hasattr(hovered_item, 'sell_price') and hovered_item.sell_price > 0:
            desc += f" (Sell: {hovered_item.sell_price}g)"
        desc_text = SMALL_FONT.render(desc, True, BLACK)
        desc_rect = desc_text.get_rect(topleft=(inv_x + 10, inv_y + INVENTORY_HEIGHT - 50))
        pygame.draw.rect(screen, TIP_BG_COLOR, desc_rect.inflate(10, 5))
        screen.blit(desc_text, desc_rect)
    
    # 操作提示
    hint_text = SMALL_FONT.render("Press E to close | Q to sell selected", True, (100, 100, 100))
    screen.blit(hint_text, (inv_x + 10, inv_y + INVENTORY_HEIGHT - 25))


def draw_shop(screen):
    """绘制商店界面"""
    shop_width = 300
    shop_height = 400
    shop_x = WIDTH // 2 - shop_width // 2
    shop_y = HEIGHT // 2 - shop_height // 2
    
    # 背景
    pygame.draw.rect(screen, SHOP_BG_COLOR, (shop_x, shop_y, shop_width, shop_height))
    pygame.draw.rect(screen, BLACK, (shop_x, shop_y, shop_width, shop_height), 2)
    
    # 标题
    title = TITLE_FONT.render("🏪 Seed Shop", True, BLACK)
    screen.blit(title, (shop_x + shop_width // 2 - title.get_width() // 2, shop_y + 10))
    
    # 金币显示
    gold_text = FONT.render(f"💰 Your Gold: {player.gold}", True, (139, 69, 19))
    screen.blit(gold_text, (shop_x + 10, shop_y + 45))
    
    # 商品列表
    item_y = shop_y + 80
    mouse_x, mouse_y = pygame.mouse.get_pos()
    shop_items = get_shop_items()
    
    for i, item in enumerate(shop_items):
        # 显示季节适用性
        plant = get_plant_for_seed(item)
        season_text = ""
        if plant:
            season_text = f" [{plant.season}]"
        
        item_text = f"{item.name}{season_text} - {item.price}g"
        
        # 检查是否可购买
        can_buy = player.gold >= item.price
        color = (34, 139, 34) if can_buy else (150, 150, 150)
        
        text_surface = FONT.render(item_text, True, color)
        text_rect = text_surface.get_rect(topleft=(shop_x + 15, item_y))
        screen.blit(text_surface, text_rect)
        
        # 购买按钮
        if can_buy:
            buy_rect = pygame.Rect(shop_x + shop_width - 60, item_y - 2, 50, 22)
            pygame.draw.rect(screen, (100, 200, 100), buy_rect)
            pygame.draw.rect(screen, BLACK, buy_rect, 1)
            buy_text = SMALL_FONT.render("Buy", True, BLACK)
            screen.blit(buy_text, (buy_rect.centerx - buy_text.get_width() // 2, 
                                   buy_rect.centery - buy_text.get_height() // 2))
        
        item_y += 35
    
    # 操作提示
    hint_text = SMALL_FONT.render("Press B to close | Click 'Buy' to purchase", True, (100, 100, 100))
    screen.blit(hint_text, (shop_x + 10, shop_y + shop_height - 25))


def handle_shop_click(mouse_pos):
    """处理商店点击事件"""
    global notification_text, notification_timer
    
    shop_width = 300
    shop_height = 400
    shop_x = WIDTH // 2 - shop_width // 2
    shop_y = HEIGHT // 2 - shop_height // 2
    
    shop_items = get_shop_items()
    item_y = shop_y + 80
    
    for item in shop_items:
        buy_rect = pygame.Rect(shop_x + shop_width - 60, item_y - 2, 50, 22)
        if buy_rect.collidepoint(mouse_pos):
            if player.spend_gold(item.price):
                player.add_item(item)
                show_notification(f"Bought {item.name}!")
                return True
            else:
                show_notification("Not enough gold!")
                return False
        item_y += 35
    return False


def draw_notification(screen):
    """绘制通知消息"""
    if notification_timer > 0 and notification_text:
        notif_surface = FONT.render(notification_text, True, WHITE)
        notif_rect = notif_surface.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        
        # 使用透明表面绘制背景
        bg_rect = notif_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((*NOTIFICATION_BG_COLOR, NOTIFICATION_BG_ALPHA))
        screen.blit(bg_surface, bg_rect.topleft)
        pygame.draw.rect(screen, (100, 200, 100), bg_rect, 2)
        screen.blit(notif_surface, notif_rect)


def draw_controls_hint(screen):
    """绘制控制提示"""
    controls = [
        "WASD: Move",
        "SPACE: Interact",
        "R: Water",
        "TAB: Cycle Seeds",
        "E: Inventory",
        "B: Shop"
    ]
    hint_text = " | ".join(controls)
    text_surface = SMALL_FONT.render(hint_text, True, BLACK)
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT - 25))


# 游戏主循环
while running:
    current_time = pygame.time.get_ticks()
    delta_time = clock.get_rawtime()
    
    # 更新季节
    season_timer += delta_time
    if season_timer >= SEASON_DURATION:
        season_timer = 0
        current_season_index = (current_season_index + 1) % len(SEASONS)
        current_season = SEASONS[current_season_index]
        show_notification(f"Season changed to {current_season}!")
    
    # 更新天数
    day_timer += delta_time
    if day_timer >= DAY_DURATION:
        day_timer = 0
        day_count += 1
    
    # 更新通知计时器
    if notification_timer > 0:
        notification_timer -= delta_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == GameState.SHOP:
                handle_shop_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                if game_state == GameState.PLAYING:
                    game_state = GameState.INVENTORY
                elif game_state == GameState.INVENTORY:
                    game_state = GameState.PLAYING
            elif event.key == pygame.K_b:
                if game_state == GameState.PLAYING:
                    game_state = GameState.SHOP
                elif game_state == GameState.SHOP:
                    game_state = GameState.PLAYING
            elif event.key == pygame.K_TAB:
                # 切换种子选择
                new_seed = player.cycle_seed()
                if new_seed:
                    show_notification(f"Selected: {new_seed.name}")
            elif event.key == pygame.K_q and game_state == GameState.INVENTORY:
                # 出售物品 - 出售所有产品
                sold_count = 0
                sold_gold = 0
                for inv_item in player.inventory[:]:
                    item = inv_item['item']
                    if item.type == ItemType.PRODUCT:
                        sell_price = getattr(item, 'sell_price', DEFAULT_SELL_PRICE)
                        sold_gold += sell_price * inv_item['count']
                        sold_count += inv_item['count']
                        player.inventory.remove(inv_item)
                if sold_count > 0:
                    player.gold += sold_gold
                    show_notification(f"Sold {sold_count} items for {sold_gold}g!")
                else:
                    show_notification("No products to sell!")
            
            elif event.key == pygame.K_SPACE and game_state == GameState.PLAYING:
                # 获取玩家当前所在的土地块
                player_tile_x = player.x // TILE_SIZE * TILE_SIZE
                player_tile_y = player.y // TILE_SIZE * TILE_SIZE
                target_block = None
                
                for block in blocks:
                    if block.position == (player_tile_x, player_tile_y):
                        target_block = block
                        break
                
                if target_block:
                    land_state = target_block.state
                    has_hoe = player.has_item(ItemID.HOE)
                    
                    if land_state == 0:  # 土地未开垦
                        if has_hoe:
                            target_block.cultivate()
                            show_notification("Land cultivated!")
                    elif land_state == 1 and target_block.plant is None:  # 开垦未播种
                        # 使用当前选择的种子
                        selected_seed = player.get_selected_seed()
                        if selected_seed:
                            # 检查季节
                            plant = get_plant_for_seed(selected_seed)
                            if plant and (plant.season == current_season or plant.season == Season.ALL):
                                if player.remove_item(selected_seed.id):
                                    target_block.plant_crop(plant, current_time)
                                    show_notification(f"Planted {plant.name}!")
                            else:
                                show_notification(f"This seed grows in {plant.season}!")
                        else:
                            show_notification("No seeds selected!")
                    elif target_block.plant is not None:
                        if target_block.growth_stage == target_block.plant.max_stages:
                            # 收获
                            harvested = target_block.harvest()
                            if harvested:
                                player.add_item(harvested.product_item)
                                seed_count = random.randint(harvested.seed_harvested_min, harvested.seed_harvested_max)
                                for _ in range(seed_count):
                                    player.add_item(harvested.seed)
                                show_notification(f"Harvested {harvested.product_item.name}!")
            
            elif event.key == pygame.K_r and game_state == GameState.PLAYING:
                # 浇水
                if player.has_item(ItemID.WATERING_CAN):
                    player_tile_x = player.x // TILE_SIZE * TILE_SIZE
                    player_tile_y = player.y // TILE_SIZE * TILE_SIZE
                    
                    for block in blocks:
                        if block.position == (player_tile_x, player_tile_y):
                            if block.water(current_time):
                                show_notification("Watered!")
                            else:
                                show_notification("Already watered or not cultivated!")
                            break
                else:
                    show_notification("You need a watering can!")

    # 处理按键事件，使用 WASD 控制移动
    if game_state == GameState.PLAYING:
        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_a] and player.x > 0:
            player.x -= MOVE_SPEED
            player.direction = "left"
            moved = True
        if keys[pygame.K_d] and player.x < WIDTH - TILE_SIZE:
            player.x += MOVE_SPEED
            player.direction = "right"
            moved = True
        if keys[pygame.K_w] and player.y > TILE_SIZE:  # 留出 HUD 空间
            player.y -= MOVE_SPEED
            player.direction = "up"
            moved = True
        if keys[pygame.K_s] and player.y < HEIGHT - TILE_SIZE:
            player.y += MOVE_SPEED
            player.direction = "down"
            moved = True

    # 植物生长逻辑
    for block in blocks:
        if isinstance(block, Soil):
            block.grow(current_time)

    # 绘制背景（根据季节变化）
    bg_color = SEASON_COLORS.get(current_season, WHITE)
    screen.fill(bg_color)

    # 绘制土地块
    for block in blocks:
        block.draw(screen)

    # Draw the player
    draw_player(screen, player.x, player.y, player.direction)

    # 高亮显示玩家当前所在的土地块
    if game_state == GameState.PLAYING:
        player_tile_x = player.x // TILE_SIZE * TILE_SIZE
        player_tile_y = player.y // TILE_SIZE * TILE_SIZE
        for block in blocks:
            if block.position == (player_tile_x, player_tile_y):
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, (player_tile_x, player_tile_y, TILE_SIZE, TILE_SIZE), 3)

    # 绘制 HUD
    draw_hud(screen)

    # 绘制界面
    if game_state == GameState.INVENTORY:
        draw_inventory(screen)
    elif game_state == GameState.SHOP:
        draw_shop(screen)
    
    # 绘制通知
    draw_notification(screen)
    
    # 绘制控制提示
    draw_controls_hint(screen)

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)

# 退出 Pygame
pygame.quit()
