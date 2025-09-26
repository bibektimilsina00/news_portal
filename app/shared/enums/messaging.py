import enum


class MessageType(str, enum.Enum):
    text = "text"
    image = "image"
    video = "video"
    audio = "audio"
    file = "file"
    voice = "voice"
    location = "location"
    contact = "contact"
    system = "system"


class MessageStatus(str, enum.Enum):
    sending = "sending"
    sent = "sent"
    delivered = "delivered"
    read = "read"
    failed = "failed"


class ParticipantRole(str, enum.Enum):
    member = "member"
    admin = "admin"
    owner = "owner"


class ParticipantStatus(str, enum.Enum):
    active = "active"
    muted = "muted"
    banned = "banned"
    left = "left"


class ConversationType(str, enum.Enum):
    direct = "direct"
    group = "group"
    channel = "channel"


class ConversationStatus(str, enum.Enum):
    active = "active"
    archived = "archived"
    deleted = "deleted"
