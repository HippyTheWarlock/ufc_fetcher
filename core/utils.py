import re

def match_str(pattern: str, data: str, case_sensitive: bool = False) -> str:
    flag = 0 if case_sensitive else re.IGNORECASE
    match = re.search(pattern, data, flags=flag)
    return match.group(0) if match else ""
