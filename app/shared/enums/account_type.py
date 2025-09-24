import enum


class AccountType(str, enum.Enum):
    PERSONAL = "personal"
    BUSINESS = "business"
    JOURNALIST = "journalist"
    ORGANIZATION = "organization"
