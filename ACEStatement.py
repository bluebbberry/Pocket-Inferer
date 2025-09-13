from dataclasses import dataclass


@dataclass
class ACEStatement:
    """Represents an ACE statement with its type and content"""
    content: str
    statement_type: str  # 'fact', 'rule', 'query'

    def __str__(self):
        return self.content