import sys

# Read the file
with open("src/solstein/connectors/registry.py", "r") as f:
    content = f.read()

# Remove the last two lines (logger.info and return)
lines = content.strip().split("\n")
content_without_end = "\n".join(lines[:-2])

# Add the new connectors
new_code = """
    # Additional code repositories
    try:
        bitbucket = BitbucketConnector()
        registry.register("bitbucket", bitbucket)
    except Exception as e:
        logger.warning(f"Failed to initialize Bitbucket: {e}")

    # Additional financial/regulatory
    try:
        opencorp = OpenCorporatesConnector()
        registry.register("opencorporates", opencorp)
    except Exception as e:
        logger.warning(f"Failed to initialize OpenCorporates: {e}")

    # Additional startup platforms
    try:
        betalist = BetaListConnector()
        registry.register("betalist", betalist)
    except Exception as e:
        logger.warning(f"Failed to initialize BetaList: {e}")

    # Additional infrastructure
    try:
        dns = DNSConnector()
        registry.register("dns", dns)
    except Exception as e:
        logger.warning(f"Failed to initialize DNS: {e}")

    logger.info(f"Initialized {len(registry.list_connectors())} connectors")
    return registry
"""

# Write back
with open("src/solstein/connectors/registry.py", "w") as f:
    f.write(content_without_end + new_code)

print("Registry updated with new connectors")
