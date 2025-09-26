import enum


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class VerificationType(str, enum.Enum):
    JOURNALIST = "journalist"
    ORGANIZATION = "organization"
    BUSINESS = "business"
