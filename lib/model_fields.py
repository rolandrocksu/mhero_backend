from typing import Optional

from django.db.models import IntegerChoices


class CustomIntegerChoices(IntegerChoices):
    @classmethod
    def from_label(cls, label: str) -> Optional['CustomIntegerChoices']:
        for k, v in cls.choices:
            if v == label:
                return cls(k)

    @classmethod
    def to_label(cls, choice: Optional['CustomIntegerChoices']) -> Optional[str]:
        if choice:
            return cls(choice).label
        return choice
