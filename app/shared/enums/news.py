import enum


class NewsStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SCHEDULED = "scheduled"


class NewsPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BREAKING = "breaking"


class FactCheckStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FALSE = "false"
    MISLEADING = "misleading"
    PARTIALLY_TRUE = "partially_true"
    UNVERIFIABLE = "unverifiable"


class FactCheckPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
