import enum


class AccountType(str, enum.Enum):
    personal = "personal"
    business = "business"
    journalist = "journalist"
    organization = "organization"
