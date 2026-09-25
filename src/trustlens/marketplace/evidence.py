"""Evidence relationships generator linking listings via shared assets or text reuse."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from trustlens.marketplace.models import (
    ListingRelationship,
    RelationshipType,
    VerificationStatus,
)
from trustlens.marketplace.orm_models import MarketplaceListingRelationshipORM


class EvidenceRelationshipManager:
    """Creates and persists unverified evidence relationships between marketplace listings."""

    def __init__(self, session: Session):
        self.session = session

    def record_relationship(
        self,
        listing_a: str,
        listing_b: str,
        relationship_type: RelationshipType,
        evidence_data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> ListingRelationship:
        """
        Record an observable relationship between two listings.
        Idempotent: prevents duplicate relationship pairs.
        """
        # Sort listing pair to maintain canonical ordering
        l1, l2 = sorted([listing_a, listing_b])
        now = timestamp or datetime.now(timezone.utc)

        # Check existing
        stmt = select(MarketplaceListingRelationshipORM).where(
            MarketplaceListingRelationshipORM.listing_a == l1,
            MarketplaceListingRelationshipORM.listing_b == l2,
            MarketplaceListingRelationshipORM.relationship_type == relationship_type.value,
        )
        existing = self.session.execute(stmt).scalar_one_or_none()
        if existing:
            return ListingRelationship(
                relationship_id=existing.relationship_id,
                listing_a=existing.listing_a,
                listing_b=existing.listing_b,
                relationship_type=RelationshipType(existing.relationship_type),
                evidence_data=existing.evidence_data,
                similarity_status=existing.similarity_status,
                verification_status=VerificationStatus(existing.verification_status),
                created_at=existing.created_at,
            )

        rel_id = f"REL-{uuid.uuid4().hex[:12].upper()}"
        orm = MarketplaceListingRelationshipORM(
            relationship_id=rel_id,
            listing_a=l1,
            listing_b=l2,
            relationship_type=relationship_type.value,
            evidence_data=evidence_data,
            similarity_status="candidate_match",
            verification_status="unverified",
            created_at=now,
        )
        self.session.add(orm)
        self.session.flush()

        return ListingRelationship(
            relationship_id=rel_id,
            listing_a=l1,
            listing_b=l2,
            relationship_type=relationship_type,
            evidence_data=evidence_data,
            similarity_status="candidate_match",
            verification_status=VerificationStatus.UNVERIFIED,
            created_at=now,
        )

    def get_relationships_for_listing(self, listing_id: str) -> List[ListingRelationship]:
        """Fetch all recorded relationships for a given listing."""
        stmt = select(MarketplaceListingRelationshipORM).where(
            (MarketplaceListingRelationshipORM.listing_a == listing_id)
            | (MarketplaceListingRelationshipORM.listing_b == listing_id)
        )
        records = self.session.execute(stmt).scalars().all()
        return [
            ListingRelationship(
                relationship_id=r.relationship_id,
                listing_a=r.listing_a,
                listing_b=r.listing_b,
                relationship_type=RelationshipType(r.relationship_type),
                evidence_data=r.evidence_data,
                similarity_status=r.similarity_status,
                verification_status=VerificationStatus(r.verification_status),
                created_at=r.created_at,
            )
            for r in records
        ]
