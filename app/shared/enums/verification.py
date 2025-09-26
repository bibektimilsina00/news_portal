import enum


class VerificationStatus(str, enum.Enum):
    pending = "pending"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"


class VerificationType(str, enum.Enum):
    journalist = "journalist"
    organization = "organization"
    business = "business"
