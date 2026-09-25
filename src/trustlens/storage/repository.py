"""Database repository providing transactional persistence and statistics queries."""

from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from trustlens.models.case import Case
from trustlens.models.listing import CanonicalListing
from trustlens.models.seller import Seller
from trustlens.storage.orm_models import (
    CaseORM,
    ListingDuplicateORM,
    ListingORM,
    MediaORM,
    SellerORM,
)


class Repository:
    """Repository encapsulating all database interactions."""

    def __init__(self, session: Session):
        self.session = session

    # ---------------------------------------------------------
    # Case & Listing Persistence
    # ---------------------------------------------------------

    def save_case(self, case: Case) -> CaseORM:
        """Persist or update an investigation case."""
        orm = self.session.get(CaseORM, case.case_id)
        if not orm:
            orm = CaseORM(
                case_id=case.case_id,
                status=case.status.value,
                source=case.source,
                created_at=case.created_at,
                updated_at=case.updated_at,
                labels=case.labels,
                metadata_=case.metadata,
            )
            self.session.add(orm)
        else:
            orm.status = case.status.value
            orm.updated_at = case.updated_at
            orm.labels = case.labels
            orm.metadata_ = case.metadata
        return orm

    def save_seller(self, seller: Seller) -> SellerORM:
        """Persist or update a seller."""
        orm = self.session.get(SellerORM, seller.seller_id)
        if not orm:
            orm = SellerORM(
                seller_id=seller.seller_id,
                source=seller.source,
                source_seller_id=seller.source_seller_id,
                display_name=seller.display_name,
                account_age=seller.account_age,
                profile_location=seller.profile_location,
                verification_status=seller.verification_status,
                seller_type=seller.seller_type,
                listing_count=seller.listing_count,
                business_name_claim=seller.business_name_claim,
                gstin_claim=seller.gstin_claim,
                phone_present=seller.phone_present,
                phone_hash=seller.phone_hash,
                email_present=seller.email_present,
                email_hash=email_hash if (email_hash := seller.email_hash) else None,
                website_claim=seller.website_claim,
                collected_at=seller.collected_at,
                metadata_=seller.metadata,
            )
            self.session.add(orm)
        return orm

    def save_listing(self, listing: CanonicalListing) -> ListingORM:
        """Persist a canonical listing along with its case, seller, and media."""
        # Ensure Case exists
        case_orm = self.session.get(CaseORM, listing.case_id)
        if not case_orm:
            case_orm = CaseORM(
                case_id=listing.case_id,
                status="collecting",
                source=listing.source,
                created_at=listing.collected_at,
                updated_at=listing.collected_at,
                labels=["synthetic"] if listing.is_synthetic else [],
                metadata_={},
            )
            self.session.add(case_orm)

        # Handle Seller if present
        seller_id = None
        if listing.seller:
            seller_orm = self.save_seller(listing.seller)
            seller_id = seller_orm.seller_id

        # Persist Listing
        listing_orm = self.session.get(ListingORM, listing.listing_id)
        if not listing_orm:
            listing_orm = ListingORM(
                listing_id=listing.listing_id,
                case_id=listing.case_id,
                seller_id=seller_id,
                source=listing.source,
                source_listing_id=listing.source_listing_id,
                source_url=str(listing.source_url) if listing.source_url else None,
                raw_title=listing.raw_title,
                normalized_title=listing.normalized_title,
                raw_description=listing.raw_description,
                normalized_description=listing.normalized_description,
                category=listing.category,
                subcategory=listing.subcategory,
                brand=listing.brand,
                model=listing.model,
                raw_price=listing.raw_price,
                normalized_price=listing.normalized_price,
                raw_currency=listing.raw_currency,
                normalized_currency=listing.normalized_currency,
                condition=listing.condition.value,
                location_raw=listing.location_raw,
                location_city=listing.location_city,
                location_state=listing.location_state,
                posted_at=listing.posted_at,
                updated_at=listing.updated_at,
                collected_at=listing.collected_at,
                pipeline_version=listing.collection_metadata.pipeline_version,
                schema_version=listing.collection_metadata.schema_version,
                is_synthetic=listing.is_synthetic,
                extracted_claims=listing.extracted_claims,
                collection_metadata=listing.collection_metadata.model_dump(mode="json"),
            )
            self.session.add(listing_orm)

        # Persist Media items
        for m in listing.media:
            m_orm = self.session.get(MediaORM, m.media_id)
            if not m_orm:
                m_orm = MediaORM(
                    media_id=m.media_id,
                    listing_id=listing.listing_id,
                    media_type=m.media_type.value,
                    source_url=m.source_url,
                    local_path=m.local_path,
                    mime_type=m.mime_type,
                    file_size=m.file_size,
                    width=m.width,
                    height=m.height,
                    duration=m.duration,
                    sha256=m.sha256,
                    perceptual_hash=m.perceptual_hash,
                    collection_timestamp=m.collection_timestamp,
                    metadata_=m.metadata,
                )
                self.session.add(m_orm)

        self.session.commit()
        return listing_orm

    # ---------------------------------------------------------
    # Duplicate Detection Queries
    # ---------------------------------------------------------

    def find_duplicate(
        self,
        source: str,
        source_listing_id: Optional[str] = None,
        source_url: Optional[str] = None,
        normalized_title: Optional[str] = None,
        seller_phone_hash: Optional[str] = None,
        media_sha256_list: Optional[list[str]] = None,
    ) -> Optional[tuple[str, str, str]]:
        """Check for existing duplicate records.

        Returns (original_listing_id, duplicate_type, match_reason) if found.
        """
        # 1. Exact Source Listing ID match
        if source_listing_id:
            id_stmt = select(ListingORM.listing_id).where(
                ListingORM.source == source,
                ListingORM.source_listing_id == source_listing_id,
            )
            id_match = self.session.execute(id_stmt).scalars().first()
            if id_match:
                return (id_match, "exact", f"Matching source listing ID '{source_listing_id}'")

        # 2. Exact URL match
        if source_url:
            url_stmt = select(ListingORM.listing_id).where(ListingORM.source_url == source_url)
            url_match = self.session.execute(url_stmt).scalars().first()
            if url_match:
                return (url_match, "exact", f"Matching source URL '{source_url}'")

        # 3. Exact Media SHA-256 match
        if media_sha256_list:
            for sha in media_sha256_list:
                if sha:
                    media_stmt = select(MediaORM.listing_id).where(
                        MediaORM.sha256 == sha,
                        MediaORM.listing_id.is_not(None),
                    )
                    media_match = self.session.execute(media_stmt).scalars().first()
                    if media_match:
                        return (media_match, "exact", f"Matching media file SHA256 '{sha[:12]}...'")

        # 4. Same Title + Same Seller Phone Hash
        if normalized_title and seller_phone_hash:
            title_stmt = (
                select(ListingORM.listing_id)
                .join(SellerORM, ListingORM.seller_id == SellerORM.seller_id)
                .where(
                    ListingORM.normalized_title == normalized_title,
                    SellerORM.phone_hash == seller_phone_hash,
                )
            )
            title_match = self.session.execute(title_stmt).scalars().first()
            if title_match:
                return (title_match, "near", "Identical title posted by same seller phone")

        return None

    def record_duplicate(
        self,
        original_listing_id: str,
        duplicate_listing_id: str,
        duplicate_type: str,
        similarity_score: float,
        match_reason: str,
    ) -> ListingDuplicateORM:
        """Log a duplicate occurrence."""
        dup = ListingDuplicateORM(
            original_listing_id=original_listing_id,
            duplicate_listing_id=duplicate_listing_id,
            duplicate_type=duplicate_type,
            similarity_score=similarity_score,
            match_reason=match_reason,
        )
        self.session.add(dup)
        self.session.commit()
        return dup

    # ---------------------------------------------------------
    # Statistics Aggregation
    # ---------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        """Aggregate comprehensive database statistics for the CLI."""
        total_listings = (
            self.session.execute(select(func.count(ListingORM.listing_id))).scalar() or 0
        )

        # By category
        cat_counts = self.session.execute(
            select(ListingORM.category, func.count(ListingORM.listing_id)).group_by(
                ListingORM.category
            )
        ).all()
        by_category: dict[str, int] = {str(cat): int(count) for cat, count in cat_counts}

        # By source
        src_counts = self.session.execute(
            select(ListingORM.source, func.count(ListingORM.listing_id)).group_by(ListingORM.source)
        ).all()
        by_source: dict[str, int] = {str(src): int(count) for src, count in src_counts}

        # Media counts
        listings_with_images = (
            self.session.execute(
                select(func.count(func.distinct(MediaORM.listing_id))).where(
                    MediaORM.media_type == "image"
                )
            ).scalar()
            or 0
        )

        listings_with_videos = (
            self.session.execute(
                select(func.count(func.distinct(MediaORM.listing_id))).where(
                    MediaORM.media_type == "video"
                )
            ).scalar()
            or 0
        )

        # Missing fields
        missing_descriptions = (
            self.session.execute(
                select(func.count(ListingORM.listing_id)).where(
                    (ListingORM.raw_description.is_(None)) | (ListingORM.raw_description == "")
                )
            ).scalar()
            or 0
        )

        missing_prices = (
            self.session.execute(
                select(func.count(ListingORM.listing_id)).where(
                    ListingORM.normalized_price.is_(None)
                )
            ).scalar()
            or 0
        )

        # Duplicate counts
        duplicate_count = (
            self.session.execute(select(func.count(ListingDuplicateORM.id))).scalar() or 0
        )

        # Synthetic count
        synthetic_count = (
            self.session.execute(
                select(func.count(ListingORM.listing_id)).where(ListingORM.is_synthetic.is_(True))
            ).scalar()
            or 0
        )

        return {
            "total_listings": total_listings,
            "synthetic_listings": synthetic_count,
            "by_category": by_category,
            "by_source": by_source,
            "listings_with_images": listings_with_images,
            "listings_with_videos": listings_with_videos,
            "missing_descriptions": missing_descriptions,
            "missing_prices": missing_prices,
            "duplicate_count": duplicate_count,
        }
