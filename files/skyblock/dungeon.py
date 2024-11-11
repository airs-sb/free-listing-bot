from skyblockparser.levels import get_cata_lvl

def get_dungeon_level(profile):
    """Retrieve the Dungeon level from the profile."""
    return profile.dungeon_data.get('level', 0) if profile.dungeon_data else 0

def get_dungeon_experience(profile):
    """Retrieve the Dungeon experience from the profile."""
    return profile.dungeon_data.get('experience', 0) if profile.dungeon_data else 0

def get_catacombs_data(profile):
    """Retrieve Catacombs level and experience from the profile."""
    cata_exp = profile.dungeon_data.get('experience', 0) if profile.dungeon_data else 0
    catacombs_level = get_cata_lvl(cata_exp)
    return catacombs_level, cata_exp
