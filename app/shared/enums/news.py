import enum


class NewsStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"
    scheduled = "scheduled"


class NewsPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    breaking = "breaking"


class FactCheckStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    false = "false"
    misleading = "misleading"
    partially_true = "partially_true"
    unverifiable = "unverifiable"


class FactCheckPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"
