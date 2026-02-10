import enum


class Intent(enum.Enum):
    SPEED = "speed"
    QUALITY = "quality"
    PRIVATE = "private"
    NSFW = "nsfw"
    CODING = "coding"
    FINANCE = "finance"
    CREATE_AGENT = "create_agent"
