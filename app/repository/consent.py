"""Database queries for consent records."""

from sqlalchemy import or_, select

from app.model.consent import ConsentRecord
from app.model.enums import ConsentType
from app.model.user import User
from app.repository.base import LIKE_ESCAPE, BaseRepository
from app.repository.scope import OwnerScope


class ConsentRecordRepository(BaseRepository[ConsentRecord]):
    model = ConsentRecord
    sort_fields = ("id", "created_at")

    def owner_condition(self, scope: OwnerScope):
        return scope.matches(ConsentRecord.user_id)

    def search_condition(self, pattern):  # Policy version or the username of the user
        return or_(
            ConsentRecord.policy_version.ilike(pattern, escape=LIKE_ESCAPE),
            ConsentRecord.user.has(User.username.ilike(pattern, escape=LIKE_ESCAPE)),
        )

    def latest(self, user_id: int, consent_type: ConsentType) -> ConsentRecord | None:  # Current decision
        stmt = (
            select(ConsentRecord)
            .where(ConsentRecord.user_id == user_id, ConsentRecord.consent_type == consent_type)
            .order_by(ConsentRecord.created_at.desc(), ConsentRecord.id.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
