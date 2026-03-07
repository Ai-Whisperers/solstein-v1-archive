# Read the file
with open("src/solstein/connectors/registry.py", "r") as f:
    lines = f.readlines()

# Keep only up to line 117 (before the duplicate code)
clean_lines = lines[:117]

# Add the new initialization code
new_code = """
    # Additional product connectors
    try:
        stackoverflow = StackOverflowConnector()
        registry.register("stackoverflow", stackoverflow)
    except Exception as e:
        logger.warning(f"Failed to initialize Stack Overflow: {e}")

    try:
        npm = NPMConnector()
        registry.register("npm", npm)
    except Exception as e:
        logger.warning(f"Failed to initialize npm: {e}")

    try:
        pypi = PyPIConnector()
        registry.register("pypi", pypi)
    except Exception as e:
        logger.warning(f"Failed to initialize PyPI: {e}")

    try:
        appstore = AppStoreConnector()
        registry.register("appstore", appstore)
    except Exception as e:
        logger.warning(f"Failed to initialize App Store: {e}")

    try:
        googleplay = GooglePlayConnector()
        registry.register("googleplay", googleplay)
    except Exception as e:
        logger.warning(f"Failed to initialize Google Play: {e}")

    # Additional social connectors
    try:
        youtube = YouTubeConnector()
        registry.register("youtube", youtube)
    except Exception as e:
        logger.warning(f"Failed to initialize YouTube: {e}")

    try:
        linkedin = LinkedInConnector()
        registry.register("linkedin", linkedin)
    except Exception as e:
        logger.warning(f"Failed to initialize LinkedIn: {e}")

    # Additional financial connectors
    try:
        crunchbase = CrunchbaseConnector()
        registry.register("crunchbase", crunchbase)
    except Exception as e:
        logger.warning(f"Failed to initialize Crunchbase: {e}")

    # Additional government connectors
    try:
        wayback = WaybackMachineConnector()
        registry.register("wayback", wayback)
    except Exception as e:
        logger.warning(f"Failed to initialize Wayback: {e}")

    logger.info(f"Initialized {len(registry.list_connectors())} connectors")
    return registry
"""

clean_lines.append(new_code)

# Write back
with open("src/solstein/connectors/registry.py", "w") as f:
    f.writelines(clean_lines)

print("Registry file cleaned and updated")
