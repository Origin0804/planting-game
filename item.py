# 定义物品类型类
class ItemType:
    TOOL = 1
    SEED = 2
    PLANT = 3
    PRODUCT = 4


# 定义物品ID常量
class ItemID:
    # 工具
    HOE = 1
    WATERING_CAN = 3
    
    # 小麦相关
    WHEAT_SEED = 2
    WHEAT_PLANT = 4
    WHEAT_PRODUCT = 5
    
    # 番茄相关
    TOMATO_SEED = 10
    TOMATO_PRODUCT = 11
    TOMATO_PLANT = 12
    
    # 玉米相关
    CORN_SEED = 20
    CORN_PRODUCT = 21
    CORN_PLANT = 22
    
    # 南瓜相关
    PUMPKIN_SEED = 30
    PUMPKIN_PRODUCT = 31
    PUMPKIN_PLANT = 32
    
    # 胡萝卜相关
    CARROT_SEED = 40
    CARROT_PRODUCT = 41
    CARROT_PLANT = 42


# 定义季节枚举
class Season:
    SPRING = "Spring"
    SUMMER = "Summer"
    AUTUMN = "Autumn"
    WINTER = "Winter"
    ALL = "All"

# 定义物品类
class Item:
    def __init__(self, item_id, name, item_type, description="", price=0, sell_price=0, stackable=True):
        """
        初始化一个 Item 实例
        :param item_id: 物品的唯一 ID
        :param name: 物品的名称
        :param item_type: 物品的类型
        :param description: 物品的描述，默认值为空字符串
        :param price: 购买价格
        :param sell_price: 出售价格
        :param stackable: 是否可堆叠
        """
        self.id = item_id
        self.name = name
        self.type = item_type
        self.description = description
        self.price = price
        self.sell_price = sell_price
        self.stackable = stackable

# 定义植物类
class Plant(Item):
    def __init__(self, item_id, name, seed, growth_time, product_item, max_stages=5, 
                 seed_harvested_max=2, seed_harvested_min=1, season=Season.ALL, 
                 color=(0, 128, 0), water_boost=1.5):
        """
        初始化一个 Plant 实例
        :param item_id: 植物的唯一 ID
        :param name: 植物的名称
        :param growth_time: 生长所需时间，单位为毫秒
        :param product_item: 收获的物品实例
        :param max_stages: 最大生长阶段数，默认值为 5
        :param seed_harvested_max: 最大收获种子数，默认值为 2
        :param seed_harvested_min: 最小收获种子数，默认值为 1
        :param season: 适合种植的季节
        :param color: 植物显示颜色
        :param water_boost: 浇水后生长速度倍数
        """
        super().__init__(item_id, name, ItemType.PLANT, f"Growth time: {growth_time // 1000} seconds")
        self.seed = seed
        self.growth_time = growth_time  # 生长所需时间，单位毫秒
        self.max_stages = max_stages
        self.product_item = product_item  # 关联收获物
        self.seed_harvested_max = seed_harvested_max
        self.seed_harvested_min = seed_harvested_min
        self.season = season
        self.color = color
        self.water_boost = water_boost


# 预定义所有作物
def create_crops():
    """创建所有作物定义"""
    crops = {}
    
    # 小麦 - 春季作物
    wheat_seed = Item(ItemID.WHEAT_SEED, "Wheat Seed", ItemType.SEED, "A seed for planting wheat", price=10, sell_price=5)
    wheat_product = Item(ItemID.WHEAT_PRODUCT, "Wheat", ItemType.PRODUCT, "Mature wheat, can be sold or used", sell_price=25)
    wheat = Plant(ItemID.WHEAT_PLANT, "Wheat Plant", wheat_seed, 100, wheat_product, 5, 2, 1, 
                  Season.SPRING, (218, 165, 32))  # 金黄色
    crops['wheat'] = {'seed': wheat_seed, 'product': wheat_product, 'plant': wheat}
    
    # 番茄 - 夏季作物
    tomato_seed = Item(ItemID.TOMATO_SEED, "Tomato Seed", ItemType.SEED, "A seed for planting tomato", price=20, sell_price=10)
    tomato_product = Item(ItemID.TOMATO_PRODUCT, "Tomato", ItemType.PRODUCT, "Fresh red tomato", sell_price=35)
    tomato = Plant(ItemID.TOMATO_PLANT, "Tomato Plant", tomato_seed, 150, tomato_product, 6, 3, 1, 
                   Season.SUMMER, (255, 99, 71))  # 番茄红色
    crops['tomato'] = {'seed': tomato_seed, 'product': tomato_product, 'plant': tomato}
    
    # 玉米 - 夏季作物
    corn_seed = Item(ItemID.CORN_SEED, "Corn Seed", ItemType.SEED, "A seed for planting corn", price=25, sell_price=12)
    corn_product = Item(ItemID.CORN_PRODUCT, "Corn", ItemType.PRODUCT, "Golden corn cob", sell_price=45)
    corn = Plant(ItemID.CORN_PLANT, "Corn Plant", corn_seed, 200, corn_product, 7, 2, 1, 
                 Season.SUMMER, (255, 215, 0))  # 金色
    crops['corn'] = {'seed': corn_seed, 'product': corn_product, 'plant': corn}
    
    # 南瓜 - 秋季作物
    pumpkin_seed = Item(ItemID.PUMPKIN_SEED, "Pumpkin Seed", ItemType.SEED, "A seed for planting pumpkin", price=50, sell_price=25)
    pumpkin_product = Item(ItemID.PUMPKIN_PRODUCT, "Pumpkin", ItemType.PRODUCT, "Large orange pumpkin", sell_price=100)
    pumpkin = Plant(ItemID.PUMPKIN_PLANT, "Pumpkin Plant", pumpkin_seed, 300, pumpkin_product, 8, 1, 1, 
                    Season.AUTUMN, (255, 140, 0))  # 橙色
    crops['pumpkin'] = {'seed': pumpkin_seed, 'product': pumpkin_product, 'plant': pumpkin}
    
    # 胡萝卜 - 秋季作物
    carrot_seed = Item(ItemID.CARROT_SEED, "Carrot Seed", ItemType.SEED, "A seed for planting carrot", price=15, sell_price=7)
    carrot_product = Item(ItemID.CARROT_PRODUCT, "Carrot", ItemType.PRODUCT, "Fresh orange carrot", sell_price=30)
    carrot = Plant(ItemID.CARROT_PLANT, "Carrot Plant", carrot_seed, 120, carrot_product, 5, 2, 1, 
                   Season.AUTUMN, (255, 127, 80))  # 珊瑚色
    crops['carrot'] = {'seed': carrot_seed, 'product': carrot_product, 'plant': carrot}
    
    return crops