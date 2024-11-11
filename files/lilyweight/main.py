import aiohttp

from .calcs.dungeon_comp_weight import get_dungeon_comp_weight
from .calcs.dungeon_xp_weight import get_cata_xp_weight
from .calcs.skill_weight import get_skill_weight
from .calcs.slayer_weight import get_slayer_weight
from .constants import used_skills
from .utils import get_level_from_XP, get_profile, get_player, get_xp_from_level, get_uuid


class LilyWeight:
    def __init__(self, api_key: str, session: aiohttp.ClientSession = None):
        self.api_key = api_key
        self.session = session

    @staticmethod
    def get_weight_raw(
            skill_level_dict: dict, skill_experience_dict: dict,
            cata_compl: dict, m_cata_compl: dict, cata_xp: float,
            zombie: float, spider: float, wolf: float, enderman: float, blaze: float
    ) -> dict:
        skill_weight, skill_overflow = get_skill_weight(skill_level_dict, skill_experience_dict)
        cata_weight, master_cata_weight = get_dungeon_comp_weight(cata_compl, m_cata_compl)
        cata_xp_weight = get_cata_xp_weight(cata_xp)
        slayer_weight = get_slayer_weight(zombie, spider, wolf, enderman, blaze)
        return {
            "total": skill_weight + skill_overflow + cata_weight + master_cata_weight + cata_xp_weight + slayer_weight,
            "skill_weight": {
                "base": skill_weight,
                "overflow": skill_overflow
            },
            "catacombs": {
                "completion": {
                    "base": cata_weight,
                    "master": master_cata_weight
                },
                "experience": cata_xp_weight
            },
            "slayer": slayer_weight
        }

    async def get_weight(self, uuid: str, profile: str = None) -> dict:
        """Calculates the dungeon completion weight of the player.

        Parameters
        -----------
        uuid: str
            The uuid of the player.

        profile: Optional[str]
            The profile name of the player. If not provided the profile with the latest save date will be used.

        Returns
        -------
        dict
            A dictionary containing weight

        Example
        -------
        >>> get_dungeon_comp_weight('bf8794f505124d7da30ae238a1efb4c2', 'Mango')
        """
        # Get the player profile data from the hypixel api
        if not self.session:
            self.session = aiohttp.ClientSession()

        profile = await get_profile(uuid, self.api_key, self.session, profile)

        # Slayers
        slayer_kwargs = {  # Loop through the slayer bosses and get the xp if they key exists else default value
            "zombie": 0, "spider": 0, "wolf": 0, "enderman": 0, "blaze": 0
        }
        if profile and profile.get("slayer_bosses"):
            for boss_type, boss_data in profile.get("slayer_bosses", {}).items():
                slayer_kwargs[boss_type] = boss_data.get("xp", 0)

        # Catacombs Completions
        # Get the catacombs weight of the player
        try:
            cata_completions = profile["dungeons"]["dungeon_types"]["catacombs"]["tier_completions"]
            # Try to get the catacombs completions
        except:
            # If the keys are not found set to default value
            cata_completions = {}
        try:
            m_cata_compl = profile["dungeons"]["dungeon_types"]["master_catacombs"]["tier_completions"]
        except:
            m_cata_compl = {}

        # Catacombs XP
        try:
            cata_xp = profile["dungeons"]["dungeon_types"]["catacombs"]["experience"]
        except:
            cata_xp = 0

        # Skills
        skill_experience_dict = {}
        skill_level_dict = {}
        if profile and profile.get("experience_skill_mining") is None:
            # Skill api is off
            player = await get_player(uuid, self.api_key, self.session)  # Get the player data from the hypixel api

            for skill_type, achv_name in used_skills.items():
                level = player["achievements"].get(achv_name, 0)  # Get the level of the skill from achievements
                skill_experience_dict[skill_type] = get_xp_from_level(level)  # Get the xp of the skill from the level
                skill_level_dict[skill_type] = level  # Add the skill level to the skill level dict
        else:
            # Loop through all the skills lily weight uses
            if profile:
                for skill_type in used_skills.keys():
                    experience = profile.get(f"experience_skill_{skill_type}", 0)  # Get the experience of the skill
                    skill_experience_dict[skill_type] = experience  # Add the experience to the experience skill dict
                    skill_level_dict[skill_type] = get_level_from_XP(experience)  # Add the skill level to the counter
        # print((skill_level_dict, skill_experience_dict, cata_completions, m_cata_compl, cata_xp, slayer_kwargs))
        return self.get_weight_raw(
            skill_level_dict, skill_experience_dict, cata_completions, m_cata_compl, cata_xp, **slayer_kwargs
        )

    async def get_weight_from_uuid(self, uuid: str, profile: str = None) -> dict:
        """Calculates the dungeon completion weight of the player.

        Parameters
        -----------
        uuid: str
            The uuid of the player.

        profile: Optional[str]
            The profile name of the player. If not provided the profile with the latest save date will be used.

        Returns
        -------
        dict
            A dictionary containing weight

        Example
        -------
        >>> get_dungeon_comp_weight('bf8794f505124d7da30ae238a1efb4c2', 'Mango')
        """
        return await self.get_weight(uuid, profile)

    async def get_weight_from_name(self, name: str, profile: str = None) -> dict:
        """Calculates the dungeon completion weight of the player.

        Parameters
        -----------
        name: str
            The name of the player.

        profile: Optional[str]
            The profile name of the player. If not provided the profile with the latest save date will be used.

        Returns
        -------
        dict
            A dictionary containing weight

        Example
        -------
        >>> get_dungeon_comp_weight('timnoot', 'Mango')
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        uuid = await get_uuid(name, self.session)
        return await self.get_weight(uuid, profile)
