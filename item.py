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
