"""Database queries for alerts."""

from app.model.alert import Alert
from app.repository.base import BaseRepository
from app.repository.scope import OwnerScope


class AlertRepository(BaseRepository[Alert]):
    model = Alert
    search_fields = (Alert.title, Alert.message, Alert.dedupe_key)
    sort_fields = ("id", "scheduled_for", "sent_at", "created_at")

    def owner_condition(self, scope: OwnerScope):
        return scope.matches(Alert.user_id)

    def filter_condition(self, name, value):
        if name == "unread":
            return Alert.read_at.is_(None) if value else Alert.read_at.is_not(None)
        return super().filter_condition(name, value)
