"""Relational Media Cluster Manager."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from trustlens.marketplace.models import (
    ClusterMember,
    MediaCluster,
    VerificationStatus,
)
from trustlens.marketplace.orm_models import (
    MarketplaceClusterMemberORM,
    MarketplaceMediaClusterORM,
)


class RelationalClusterManager:
    """Manages relational media clusters and member linkages in SQLite."""

    def __init__(self, session: Session):
        self.session = session

    def get_cluster_for_media(self, media_id: str) -> Optional[str]:
        """Find existing cluster ID for a media asset."""
        stmt = select(MarketplaceClusterMemberORM.cluster_id).where(
            MarketplaceClusterMemberORM.media_id == media_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def add_match_to_clusters(
        self,
        media_a: str,
        media_b: str,
        listing_a: str,
        listing_b: str,
        timestamp: Optional[datetime] = None,
    ) -> str:
        """
        Incrementally assign matching media assets to a relational cluster.
        If both belong to different clusters, merge them.
        Returns cluster_id.
        """
        now = timestamp or datetime.now(timezone.utc)
        cluster_a = self.get_cluster_for_media(media_a)
        cluster_b = self.get_cluster_for_media(media_b)

        target_cluster_id: str

        if not cluster_a and not cluster_b:
            # Create brand new cluster
            target_cluster_id = f"CLUST-{uuid.uuid4().hex[:10].upper()}"
            cluster_orm = MarketplaceMediaClusterORM(
                cluster_id=target_cluster_id,
                created_at=now,
                updated_at=now,
                match_count=1,
                verification_status="unverified",
            )
            self.session.add(cluster_orm)
            self.session.flush()

            # Add both members
            self.session.add(
                MarketplaceClusterMemberORM(
                    cluster_id=target_cluster_id,
                    media_id=media_a,
                    listing_id=listing_a,
                    first_seen_at=now,
                    last_seen_at=now,
                )
            )
            self.session.add(
                MarketplaceClusterMemberORM(
                    cluster_id=target_cluster_id,
                    media_id=media_b,
                    listing_id=listing_b,
                    first_seen_at=now,
                    last_seen_at=now,
                )
            )

        elif cluster_a and not cluster_b:
            # Attach B to cluster A
            target_cluster_id = cluster_a
            self._update_cluster_timestamp_and_count(target_cluster_id, now)
            self.session.add(
                MarketplaceClusterMemberORM(
                    cluster_id=target_cluster_id,
                    media_id=media_b,
                    listing_id=listing_b,
                    first_seen_at=now,
                    last_seen_at=now,
                )
            )

        elif not cluster_a and cluster_b:
            # Attach A to cluster B
            target_cluster_id = cluster_b
            self._update_cluster_timestamp_and_count(target_cluster_id, now)
            self.session.add(
                MarketplaceClusterMemberORM(
                    cluster_id=target_cluster_id,
                    media_id=media_a,
                    listing_id=listing_a,
                    first_seen_at=now,
                    last_seen_at=now,
                )
            )

        else:
            # Both belong to clusters
            if cluster_a == cluster_b:
                target_cluster_id = cluster_a
                self._update_cluster_timestamp_and_count(target_cluster_id, now)
            else:
                # Merge cluster B into cluster A
                target_cluster_id = cluster_a
                self._merge_clusters(source_cluster_id=cluster_b, target_cluster_id=cluster_a, now=now)

        self.session.flush()
        return target_cluster_id

    def _update_cluster_timestamp_and_count(self, cluster_id: str, now: datetime) -> None:
        cluster = self.session.get(MarketplaceMediaClusterORM, cluster_id)
        if cluster:
            cluster.updated_at = now
            cluster.match_count += 1

    def _merge_clusters(self, source_cluster_id: str, target_cluster_id: str, now: datetime) -> None:
        """Merge all members from source cluster into target cluster and remove source cluster."""
        stmt = select(MarketplaceClusterMemberORM).where(
            MarketplaceClusterMemberORM.cluster_id == source_cluster_id
        )
        members = self.session.execute(stmt).scalars().all()
        for m in members:
            m.cluster_id = target_cluster_id
            m.last_seen_at = now

        source_cluster = self.session.get(MarketplaceMediaClusterORM, source_cluster_id)
        target_cluster = self.session.get(MarketplaceMediaClusterORM, target_cluster_id)
        if target_cluster and source_cluster:
            target_cluster.match_count += source_cluster.match_count + 1
            target_cluster.updated_at = now
            self.session.delete(source_cluster)

    def get_cluster(self, cluster_id: str) -> Optional[MediaCluster]:
        """Fetch full cluster domain model with members."""
        orm = self.session.get(MarketplaceMediaClusterORM, cluster_id)
        if not orm:
            return None

        stmt = select(MarketplaceClusterMemberORM).where(
            MarketplaceClusterMemberORM.cluster_id == cluster_id
        )
        members_orm = self.session.execute(stmt).scalars().all()
        members = [
            ClusterMember(
                media_id=m.media_id,
                listing_id=m.listing_id,
                first_seen_at=m.first_seen_at,
                last_seen_at=m.last_seen_at,
            )
            for m in members_orm
        ]

        return MediaCluster(
            cluster_id=orm.cluster_id,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            match_count=orm.match_count,
            verification_status=VerificationStatus(orm.verification_status),
            members=members,
        )

    def get_all_clusters(self) -> List[MediaCluster]:
        """Return all clusters with members."""
        stmt = select(MarketplaceMediaClusterORM)
        clusters_orm = self.session.execute(stmt).scalars().all()
        result = []
        for c in clusters_orm:
            cluster_model = self.get_cluster(c.cluster_id)
            if cluster_model:
                result.append(cluster_model)
        return result
