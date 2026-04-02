# Read the file
with open("src/solstein/connectors/registry.py") as f:
    content = f.read()

# Remove the last two lines (logger.info and return)
lines = content.strip().split("\n")
content_without_end = "\n".join(lines[:-2])

# Add the new connectors
new_code = """
    try:
        trustpilot = TrustpilotConnector()
        registry.register("trustpilot", trustpilot)
    except Exception as e:
        logger.warning(f"Failed to initialize Trustpilot: {e}")

    # Podcast connectors
    try:
        podcastindex = PodcastIndexConnector()
        registry.register("podcastindex", podcastindex)
    except Exception as e:
        logger.warning(f"Failed to initialize Podcast Index: {e}")

    # Startup platforms
    try:
        angellist = AngelListConnector()
        registry.register("angellist", angellist)
    except Exception as e:
        logger.warning(f"Failed to initialize AngelList: {e}")

    try:
        f6s = F6SConnector()
        registry.register("f6s", f6s)
    except Exception as e:
        logger.warning(f"Failed to initialize F6S: {e}")

    # Additional review platforms
    try:
        capterra = CapterraConnector()
        registry.register("capterra", capterra)
    except Exception as e:
        logger.warning(f"Failed to initialize Capterra: {e}")

    logger.info(f"Initialized {len(registry.list_connectors())} connectors")
    return registry
"""

# Write back
with open("src/solstein/connectors/registry.py", "w") as f:
    f.write(content_without_end + new_code)

print("Registry updated with new connectors")
