import requests

# Download official PEP 8
url = "https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst"
response = requests.get(url)

# Save to data folder
with open("data/pep8_rules.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("✅ PEP 8 rules downloaded successfully!")