"""Database queries for advisory requests, responses, explanations, and citations."""

from sqlalchemy import select

from app.model.advisory import (
    AdvisoryCitation,
    AdvisoryExplanation,
    AdvisoryRequest,
    AdvisoryResponse,
)
from app.repository.base import BaseRepository
from app.repository.scope import OwnerScope


def request_owned_by(scope: OwnerScope):  # The request is for the user or for an assigned farmer
    return scope.matches(AdvisoryRequest.farmer_id)


def response_owned_by(scope: OwnerScope):
    return AdvisoryResponse.request.has(request_owned_by(scope))


def explanation_owned_by(scope: OwnerScope):
    return AdvisoryExplanation.response.has(response_owned_by(scope))


class AdvisoryRequestRepository(BaseRepository[AdvisoryRequest]):
    model = AdvisoryRequest
    search_fields = (AdvisoryRequest.question, AdvisoryRequest.referral_reason)
    sort_fields = ("id", "created_at", "updated_at")

    def owner_condition(self, scope):
        return request_owned_by(scope)


class AdvisoryResponseRepository(BaseRepository[AdvisoryResponse]):
    model = AdvisoryResponse
    search_fields = (AdvisoryResponse.action, AdvisoryResponse.reason, AdvisoryResponse.suggested_timing)
    sort_fields = ("id", "created_at", "expires_at", "estimated_cost")

    def owner_condition(self, scope):
        return response_owned_by(scope)


class AdvisoryExplanationRepository(BaseRepository[AdvisoryExplanation]):
    model = AdvisoryExplanation
    search_fields = (AdvisoryExplanation.text, AdvisoryExplanation.model_name)
    sort_fields = ("id", "created_at")

    def owner_condition(self, scope):
        return explanation_owned_by(scope)

    def current_for(self, response_id: int, language: str) -> list[AdvisoryExplanation]:
        stmt = select(AdvisoryExplanation).where(
            AdvisoryExplanation.response_id == response_id,
            AdvisoryExplanation.language == language,
            AdvisoryExplanation.is_current.is_(True),
        )
        return list(self.db.scalars(stmt))


class AdvisoryCitationRepository(BaseRepository[AdvisoryCitation]):
    model = AdvisoryCitation
    sort_fields = ("id", "rank", "similarity_score")

    def owner_condition(self, scope):
        return AdvisoryCitation.explanation.has(explanation_owned_by(scope))
