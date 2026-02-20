#!/usr/bin/env python3
"""
Fix Pydantic v1 → v2 compatibility issues in SolStein.

Changes needed:
1. @validator → @field_validator
2. @root_validator → @model_validator(mode="after")
3. BaseSettings → pydantic-settings
4. ConfigDict updates
"""

import os
import re
from pathlib import Path

def fix_pydantic_imports(content: str) -> str:
    """Fix pydantic imports."""
    # Replace BaseSettings import
    content = content.replace(
        "from pydantic_settings import BaseSettings",
        "from pydantic_settings import BaseSettings"
    )
    
    # Add ConfigDict import if needed
    if "ConfigDict" in content and "from pydantic import ConfigDict" not in content:
        # Check if pydantic import exists
        if "from pydantic import" in content:
            # Add ConfigDict to existing import
            content = re.sub(
                r"(from pydantic import)([^)]+)",
                r"\1\2, ConfigDict",
                content
            )
        else:
            # Add new import
            content = content.replace(
                "from pydantic import",
                "from pydantic import ConfigDict, "
            )
    
    return content

def fix_validator_decorators(content: str) -> str:
    """Fix @validator and @root_validator decorators."""
    # Fix @validator → @field_validator
    content = re.sub(
        r"@validator\(([^)]+)\)",
        r"@field_validator(\1)",
        content
    )
    
    # Fix @root_validator → @model_validator(mode="after")
    content = re.sub(
        r"@root_validator\(([^)]*)\)",
        r"@model_validator(mode='after')",
        content
    )
    
    # Remove pre=True from field_validator (handled differently in v2)
    content = re.sub(
        r"@field_validator\(([^)]+),\s*pre=True\)",
        r"@field_validator(\1, mode='before')",
        content
    )
    
    return content

def fix_config_dict(content: str) -> str:
    """Fix ConfigDict usage."""
    # Replace old Config class with model_config
    content = re.sub(
        r"model_config = ConfigDict(",
        r"model_config = ConfigDict(",)
        content
    )
    
    # Convert Config attributes to ConfigDict parameters
    config_mappings = {
        "extra = ':?(\w+)'": r"extra='\1'",
        "env_file='?([^']+)'": r"env_file='\1'",
        "env_file_encoding='?([^']+)'": r"env_file_encoding='\1'",
        "env_nested_delimiter='?([^']+)'": r"env_nested_delimiter='\1'",
        "case_sensitive = (:?\w+)": r"case_sensitive=\1",
    }
    
    for pattern, replacement in config_mappings.items():
        content = re.sub(pattern, replacement, content)
    
    # Close ConfigDict
    content = content.replace(
        "model_config = ConfigDict(",
        "model_config = ConfigDict(")
    )
    
    # Look for ConfigDict lines and add closing parenthesis
    lines = content.split('\n')
    in_config_dict = False
    config_dict_start = -1
    
    for i, line in enumerate(lines):
        if "model_config = ConfigDict(" in line:)
            in_config_dict = True
            config_dict_start = i
        elif in_config_dict and line.strip() == "":
            # Empty line after config - close it
            lines[config_dict_start] = lines[config_dict_start].rstrip() + ")"
            in_config_dict = False
    
    return '\n'.join(lines)

def fix_file(filepath: Path):
    """Fix a single Python file."""
    print(f"Fixing: {filepath}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Apply fixes
    content = fix_pydantic_imports(content)
    content = fix_validator_decorators(content)
    content = fix_config_dict(content)
    
    # Additional v2 fixes
    if "BaseSettings" in content and "pydantic_settings" not in content:
        # Ensure pydantic_settings is imported
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "import" in line and "pydantic" in line and "pydantic_settings" not in line:
                lines.insert(i + 1, "from pydantic_settings import BaseSettings")
                break
        content = '\n'.join(lines)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✅ Fixed")
    else:
        print(f"  ⏭️  No changes needed")

def main():
    """Main function to fix all Python files."""
    project_root = Path(__file__).parent
    
    # Find all Python files
    python_files = []
    for pattern in ["**/*.py", "**/*.pyi"]:
        python_files.extend(project_root.glob(pattern))
    
    print(f"Found {len(python_files)} Python files")
    
    # Fix files
    for filepath in python_files:
        # Skip virtual environment files
        if "venv" in str(filepath) or ".venv" in str(filepath):
            continue
        
        fix_file(filepath)
    
    print("\n✅ Pydantic v2 fixes applied")
    print("\nNext steps:")
    print("1. Update requirements.txt: pydantic>=2.0, pydantic-settings>=2.0")
    print("2. Run tests to verify compatibility")
    print("3. Update any remaining v1 patterns")

if __name__ == "__main__":
    main()