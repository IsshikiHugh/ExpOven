from typing import Optional
from oven.backends.api import BackendInfoBase

class BarkBackendInfo(BackendInfoBase):
    def __init__(
        self,
        content: str,
        title: Optional[str] = None,
        sound: Optional[str] = None,
        icon: Optional[str] = None,
        group: Optional[str] = None,
        level: Optional[str] = None,
        url: Optional[str] = None,
        badge: Optional[int] = None,
        auto_copy: bool = True,
        copy_text: Optional[str] = None
    ):
        """
        Container for Bark notification information.
        
        Args:
            content: Main notification text (required)
            title: Notification title
            sound: Sound to play (e.g., 'alarm')
            icon: URL for notification icon
            group: Group identifier
            level: Priority ('active', 'timeSensitive', 'passive')
            url: URL to open on click
            badge: Badge number to display
            auto_copy: Auto-copy content to clipboard
            copy_text: Custom copy text
        """
        self.content = content
        self.title = title
        self.sound = sound
        self.icon = icon
        self.group = group
        self.level = level
        self.url = url
        self.badge = badge
        self.auto_copy = auto_copy
        self.copy_text = copy_text

    def get_title(self) -> str:
        return self.title or ''

    def get_content(self) -> str:
        return self.content

    def format_information(self) -> str:
        return (
            f"Bark Notification:\n"
            f"Title: {self.title}\n"
            f"Content: {self.content}\n"
            f"Settings: sound={self.sound}, group={self.group}"
        )