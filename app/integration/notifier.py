"""Send messages to users, for example password-reset links and verification codes.

LogNotifier is for development only. It writes the message to the log and keeps it in memory.
For production, write a class with the same send method (email or SMS provider) and call set_notifier at start-up.
"""

import logging
from dataclasses import dataclass
from typing import Protocol

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Message:
    user_id: int
    channel: str  # "email" or "sms"
    address: str  # Email address or phone number
    subject: str
    body: str
    token: str  # The secret in the message. Only tests and the development log use this field.


class Notifier(Protocol):
    def send(self, message: Message) -> None: ...


class LogNotifier:
    def __init__(self):
        self.outbox: list[Message] = []  # Sent messages, for tests

    def send(self, message: Message) -> None:
        self.outbox.append(message)
        logger.warning(
            "DEVELOPMENT NOTIFIER. Message to user %s by %s (%s): %s %s",
            message.user_id, message.channel, message.address, message.subject, message.body,
        )


_notifier: Notifier = LogNotifier()


def get_notifier() -> Notifier:
    return _notifier


def set_notifier(notifier: Notifier) -> None:
    global _notifier
    _notifier = notifier
