def format_slayers(slayers):
    """Format slayer levels into a string."""
    return "/".join(f"{int(slayer.get('level', 0))}" for slayer in slayers.values())
