from .constants import *
from .exceptions import SkyblockParserException
from .renderer import render

def format_stat(stat):
    formatted_stat = "{:.2f}".format(stat).rstrip('0').rstrip('.')
    if stat > 0:
        return f"§a+{formatted_stat}"
    else:
        return f"§a{formatted_stat}"
    
rarity_colors = {
    "COMMON": "f",
    "UNCOMMON": "a",
    "RARE": "9",
    "EPIC": "5",
    "LEGENDARY": "6",
    "MYTHIC": "d"
}

class Pet:
    def __init__(self, data, menu:bool=True):

        self.lore = []
        self.uuid = None
        self.active = False

        if not menu:
            
            item_name = data.get("display", {}).get("Name", "")
            item_lore = data.get("display", {}).get("Lore", [])

            lore = [item_name, *item_lore]
            for line in lore:
                if "§r §e" in line:
                    line = line.split(" §r ")[1]
                line = line.replace("§", "&")
                self.lore.append(line)


        if self.uuid is None:
            self.uuid = data.get("uuid", "")

        self.type = data.get("type", "")
        self.exp = data.get("exp", 0)

        if self.active is None:
            self.active = data.get("active", False)

        self.tier = data.get("tier", 0)
        self.rarity_color = rarity_colors.get(self.tier, "")

        if self.rarity_color == "":
            pass


        self.held_item = data.get("heldItem", "")

        if self.held_item in rarity_upgrading_pet_items:
            if self.type not in ignores_tierboost:
                current_tier = pet_tiers.index(self.tier)
                if current_tier == len(pet_tiers)-1:
                    self.tier = pet_tiers[current_tier]
                else:
                    self.tier = pet_tiers[current_tier+1]

        self.candy_used = data.get("candyUsed", 0)
        self.skin = data.get("skin", "")

        self.max_level = 100
        if self.type in special_pet_levels:
            self.max_level = special_pet_levels[self.type]

        self.calculate_level()
        self.create_lore()

    def calculate_level(self):

        if self.type == "BINGO":
            pet_offset = 0
        else:
            pet_offset = rarity_offset[self.tier]

        new_pet_levels = pet_levels[pet_offset:]
        new_pet_levels = new_pet_levels[:self.max_level-1]

        total_pet_xp = 0

        for i in new_pet_levels:
            total_pet_xp += i
            if total_pet_xp >= self.exp:
                level = new_pet_levels.index(i)+1
                break
        else:
            level = 100
            if self.type in special_pet_levels:
                level = special_pet_levels[self.type]

        self.level = level
        self.max_xp = sum(new_pet_levels)


    def create_lore(self):
        if self.lore is not []:
            return
            
    def render(self):
        return render(self.lore)

