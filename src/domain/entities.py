from dataclasses import dataclass
from enum import Enum


class MediaType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    STEM = "stem"


class OutputCategory(str, Enum):
    CAPTURE = "captured"
    TRIM = "trimmed"
    STEM_VOCALS = "stem-vocals"
    STEM_FULL4 = "stem-full4"
    STEM_EXTENDED6 = "stem-extended6"
    RENDER = "rendered"


@dataclass(frozen=True)
class OutputRequest:
    media_type: MediaType
    category: OutputCategory
    project_name: str
    extension: str

    @property
    def prefix(self) -> str:
        return self.media_type.value

    @property
    def suffix(self) -> str:
        return self.category.value
