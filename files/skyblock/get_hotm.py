async def get_hotm_data(profile):
    """Retrieve Heart of the Mountain data from the profile."""
    await profile.get_mining_stats()  # Ensure you call this to populate mining_data
    hotm_data = profile.mining_data.get("hotm", {})

    hotm_level = hotm_data.get("level", 0)
    
    # Get powder amounts correctly
    hotm_level = hotm_data.get("level", 0)
    mithril_powder = hotm_data.get("powder", {}).get("mithril", {}).get("available", 0)
    gemstone_powder = hotm_data.get("powder", {}).get("gemstone", {}).get("available", 0)
    
    return hotm_level, mithril_powder, gemstone_powder
