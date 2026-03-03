import re

class ExtractRegexFormatter:
    @classmethod
    def extract_response(cls, text: str, regex: str) -> str | None:
        response_match = re.search(regex, text, re.DOTALL)
        return response_match.group(1).strip() if response_match else None