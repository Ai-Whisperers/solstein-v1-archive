import sys

# Read the file
with open("src/solstein/connectors/registry.py", "r") as f:
    content = f.read()

# Remove the last two lines (logger.info and return)
lines = content.strip().split("\n")
content_without_end = "\n".join(lines[:-2])

# Add the new connectors
new_code = """
    # Social media
    try:
        twitter = TwitterConnector()
        registry.register("twitter", twitter)
    except Exception as e:
        logger.warning(f"Failed to initialize Twitter: {e}")

    # Regulatory/Government
    try:
        sec = SECEdgarConnector()
        registry.register("sec_edgar", sec)
    except Exception as e:
        logger.warning(f"Failed to initialize SEC EDGAR: {e}")

    logger.info(f"Initialized {len(registry.list_connectors())} connectors")
    return registry
"""

# Write back
with open("src/solstein/connectors/registry.py", "w") as f:
    f.write(content_without_end + new_code)

print("Registry updated with Twitter and SEC EDGAR")
