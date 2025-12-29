import re

regex = r"https://.*\.codemurf\.com|vscode-webview://.*"
pattern = re.compile(regex)

test_origins = [
    "https://dashboard.codemurf.com",
    "https://api.codemurf.com",
    "https://www.codemurf.com",
    "https://codemurf.com",
    "http://dashboard.codemurf.com",
    "vscode-webview://123456"
]

print(f"Testing regex: {regex}")
for origin in test_origins:
    match = pattern.fullmatch(origin)
    print(f"Origin: {origin} -> {'MATCH' if match else 'NO MATCH'}")
