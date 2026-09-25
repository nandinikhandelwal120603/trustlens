"""Unit tests for relational media clustering and transitive merging."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from trustlens.marketplace.cluster import RelationalClusterManager
from trustlens.storage.database import Base


def create_in_memory_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_clustering_pair_creation():
    session = create_in_memory_session()
    mgr = RelationalClusterManager(session)

    # Match between M1 and M2
    c_id = mgr.add_match_to_clusters(media_a="M1", media_b="M2", listing_a="L1", listing_b="L2")
    assert c_id.startswith("CLUST-")

    cluster = mgr.get_cluster(c_id)
    assert cluster is not None
    assert len(cluster.members) == 2
    assert {m.media_id for m in cluster.members} == {"M1", "M2"}
    assert {m.listing_id for m in cluster.members} == {"L1", "L2"}


def test_clustering_transitive_expansion():
    session = create_in_memory_session()
    mgr = RelationalClusterManager(session)

    # M1 matches M2
    c_id1 = mgr.add_match_to_clusters(media_a="M1", media_b="M2", listing_a="L1", listing_b="L2")
    # Later, M3 matches M1
    c_id2 = mgr.add_match_to_clusters(media_a="M3", media_b="M1", listing_a="L3", listing_b="L1")

    assert c_id1 == c_id2
    cluster = mgr.get_cluster(c_id1)
    assert cluster is not None
    assert len(cluster.members) == 3
    assert {m.media_id for m in cluster.members} == {"M1", "M2", "M3"}


def test_clustering_merge():
    session = create_in_memory_session()
    mgr = RelationalClusterManager(session)

    # Cluster 1: M1 - M2
    c1 = mgr.add_match_to_clusters(media_a="M1", media_b="M2", listing_a="L1", listing_b="L2")
    # Cluster 2: M3 - M4
    c2 = mgr.add_match_to_clusters(media_a="M3", media_b="M4", listing_a="L3", listing_b="L4")
    assert c1 != c2

    # Now bridge M2 - M3 -> Merges clusters
    merged_cid = mgr.add_match_to_clusters(media_a="M2", media_b="M3", listing_a="L2", listing_b="L3")
    assert merged_cid == c1

    cluster = mgr.get_cluster(merged_cid)
    assert cluster is not None
    assert len(cluster.members) == 4
    assert {m.media_id for m in cluster.members} == {"M1", "M2", "M3", "M4"}

    # Old cluster c2 should be cleaned up
    assert mgr.get_cluster(c2) is None
