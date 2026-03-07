import sys

# Read the file
with open("src/solstein/connectors/registry.py", "r") as f:
    lines = f.readlines()

# Keep only up to line 214 (before the duplicate code)
clean_lines = lines[:214]

# Add the new initialization code
new_code = """
    # Additional news connectors
    try:
        newsapi = NewsAPIConnector()
        registry.register("newsapi", newsapi)
    except Exception as e:
        logger.warning(f"Failed to initialize NewsAPI: {e}")

    # Domain/WHOIS connectors
    try:
        whois = WHOISConnector()
        registry.register("whois", whois)
    except Exception as e:
        logger.warning(f"Failed to initialize WHOIS: {e}")

    # Additional review platforms
    try:
        glassdoor = GlassdoorConnector()
        registry.register("glassdoor", glassdoor)
    except Exception as e:
        logger.warning(f"Failed to initialize Glassdoor: {e}")

    try:
        trustpilot = TrustpilotConnector()
        registry.register("trustpilot", trustpilot)
    except Exception as e:
        logger.warning(f"Failed to initialize Trustpilot: {e}")

    logger.info(f"Initialized {len(registry.list_connectors())} connectors")
    return registry
"""

clean_lines.append(new_code)

# Write back
with open("src/solstein/connectors/registry.py", "w") as f:
    f.writelines(clean_lines)

print("Registry file cleaned and updated")
