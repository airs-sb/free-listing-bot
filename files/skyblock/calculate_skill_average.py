from lilyweight.constants import srw, level60skill, overflow_skill_multipliers, skill_overall
effective_xp = lambda xp, factor: xp ** factor

def get_skill_weight(skill_level_dict: dict, skill_experience_dict: dict) -> tuple[float, float]:
    """Calculates the skill weight of the player."""
    try:
        skill_average = sum(skill_level_dict.values()) / len(skill_level_dict)  # Calculate the average skill level
    except ZeroDivisionError:
        skill_average = 0

    n = 12 * ((skill_average / 60) ** 2.44780217148309)

    r2 = 1.4142135623730950

    temp = []

    for skill, level in skill_level_dict.items():
        skill_weights = srw[skill]
        int_level = int(level)  # Ensure level is an integer
        temp.append(
            (n * skill_weights[int_level] * skill_weights[-1])  # avg mult * skill mult * type mult
            +
            (skill_weights[-1] * (int_level / 60) ** r2)  # type mult * skill ratio mult
        )

    skill_rating = (sum(temp) * skill_overall)

    overflow_rating = 0
    for skill_type, xp in skill_experience_dict.items():
        if xp > level60skill:
            factor = overflow_skill_multipliers[skill_type]["factor"]
            effective_over = effective_xp(xp - level60skill, factor)
            rating = effective_over / level60skill
            overflow_mult = overflow_skill_multipliers[skill_type]["overflow_multiplier"]
            t = rating * overflow_mult
            if t > 0:
                overflow_rating += (skill_overall * rating * overflow_mult)

    return skill_rating, overflow_rating

def get_skill_data(profile):
    """Fetch skills data from the profile and return levels and experience."""
    skills = profile.skill_data
    skill_levels = {}
    skill_experience = {}

            # Populate skill levels and experience
    for skill_name in srw.keys():
        skill_data = skills.get(skill_name, {})
        skill_levels[skill_name] = skill_data.get("level", 0)
        skill_experience[skill_name] = skill_data.get("experience", 0)

            # Calculate skill average based on actual levels
    skill_average = sum(skill_levels.values()) / len(skill_levels) if skill_levels else 0


    return skill_levels, skill_experience, skill_average


