from enum import Enum

class NameEnum(Enum):
    @classmethod
    def get_name_enum(cls, name_str):
        # Try looking up by name
        try:
            return cls[name_str]
        except KeyError:
            pass
        # Next, try looking up by value
        for member in cls:
            if member.value == name_str:
                return member
        return None