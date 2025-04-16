# 定义物品类型类
class ItemType:
    TOOL = 1
    SEED = 2
    PLANT = 3
    PRODUCT = 4

# 定义物品类
class Item:
    def __init__(self, item_id, name, item_type, description=""):
        """
        初始化一个 Item 实例
        :param item_id: 物品的唯一 ID
        :param name: 物品的名称
        :param item_type: 物品的类型
        :param description: 物品的描述，默认值为空字符串
        """
        self.id = item_id
        self.name = name
        self.type = item_type
        self.description = description

# 定义植物类
class Plant(Item):
    def __init__(self, item_id, name, seed, growth_time, product_item, max_stages=5, seed_harvested_max=2, seed_harvested_min=1):
        """
        初始化一个 Plant 实例
        :param item_id: 植物的唯一 ID
        :param name: 植物的名称
        :param growth_time: 生长所需时间，单位为毫秒
        :param product_item: 收获的物品实例
        :param max_stages: 最大生长阶段数，默认值为 5
        :param seed_harvested_max: 最大收获种子数，默认值为 2
        :param seed_harvested_min: 最小收获种子数，默认值为 1
        """
        super().__init__(item_id, name, ItemType.PLANT, f"Growth time: {growth_time // 1000} seconds")
        self.seed = seed
        self.growth_time = growth_time  # 生长所需时间，单位毫秒
        self.max_stages = max_stages
        self.product_item = product_item  # 关联收获物
        self.seed_harvested_max = seed_harvested_max
        self.seed_harvested_min = seed_harvested_min