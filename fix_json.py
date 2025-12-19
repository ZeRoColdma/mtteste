import json
import re

# Read the file
with open("seeds.json", "r", encoding="utf-8") as f:
    content = f.read()

# Remove trailing commas before closing braces/brackets
# This regex finds ", }" or ", ]" and replaces with " }" or " ]"
content = re.sub(r",(\s*[}\]])", r"\1", content)

# Try to parse it
try:
    data = json.loads(content)
    print(f"✓ JSON is valid! Found {len(data)} records.")

    # Write back the cleaned version
    with open("seeds.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✓ File has been cleaned and reformatted.")

except json.JSONDecodeError as e:
    print(f"✗ JSON Error: {e}")
    print(f"  Line {e.lineno}, Column {e.colno}")
    print(f"  Position {e.pos}")

    # Show context around the error
    lines = content.split("\n")
    if e.lineno:
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        print("\nContext:")
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1}: {lines[i]}")
