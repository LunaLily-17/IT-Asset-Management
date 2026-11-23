from dataclasses import dataclass, asdict

@dataclass
class User:
    user_id: int
    username: str
    full_name: str
    email: str
    role: str
    active: bool = True

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
