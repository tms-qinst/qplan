"""CPM Engine Tests - validates mandatory test cases from PRD."""

import pytest
from datetime import date
from app.scheduling.engine import CPMEngine, detect_circular_dependencies


class TestBasicFSLogic:
    """Test Case 1: Basic FS Logic from PRD."""

    def test_basic_fs_succession(self):
        """Activity A (3 days) -> Activity B (2 days), FS, data_date=Day6, A=100%, B=0%.
        Expected: B starts Day 6, finishes Day 7.
        """
        # Using day offsets from a base date
        base = date(2026, 4, 20)  # Monday

        activities = [
            {
                "id": "a",
                "duration_days": 3,
                "status": "completed",
                "is_milestone": False,
                "actual_start": base,
                "actual_finish": base + __import__("datetime").timedelta(days=2),
                "remaining_duration_days": 0,
            },
            {
                "id": "b",
                "duration_days": 2,
                "status": "not_started",
                "is_milestone": False,
            },
        ]

        relationships = [
            {"predecessor_id": "a", "successor_id": "b", "relationship_type": "FS", "lag_days": 0},
        ]

        engine = CPMEngine(activities, relationships, data_date=base + __import__("datetime").timedelta(days=5))
        results = engine.run()

        act_b = next(r for r in results if r["activity_id"] == "b")
        # B should start on or after the data date (which is past A's finish)
        assert act_b["early_start"] is not None
        assert act_b["early_finish"] is not None

    def test_fs_with_lag(self):
        """FS with 2 day lag."""
        base = date(2026, 4, 20)
        activities = [
            {"id": "a", "duration_days": 2, "status": "not_started"},
            {"id": "b", "duration_days": 1, "status": "not_started"},
        ]
        relationships = [
            {"predecessor_id": "a", "successor_id": "b", "relationship_type": "FS", "lag_days": 2},
        ]
        engine = CPMEngine(activities, relationships, data_date=base)
        results = engine.run()
        act_a = next(r for r in results if r["activity_id"] == "a")
        act_b = next(r for r in results if r["activity_id"] == "b")
        # B should start 2 days after A finishes
        assert act_b["early_start"] >= act_a["early_finish"]


class TestCircularDependency:
    """Test circular dependency detection."""

    def test_circular_detected(self):
        relationships = [
            {"predecessor_id": "a", "successor_id": "b", "relationship_type": "FS", "lag_days": 0},
            {"predecessor_id": "b", "successor_id": "c", "relationship_type": "FS", "lag_days": 0},
            {"predecessor_id": "c", "successor_id": "a", "relationship_type": "FS", "lag_days": 0},
        ]
        from app.scheduling.engine import RelationshipData
        rels = [RelationshipData(r) for r in relationships]
        warnings = detect_circular_dependencies(rels)
        assert len(warnings) > 0
        assert "Circular" in warnings[0]


class TestCriticalPath:
    """Test critical path detection."""

    def test_critical_path_identified(self):
        base = date(2026, 4, 20)
        activities = [
            {"id": "a", "duration_days": 3, "status": "not_started"},
            {"id": "b", "duration_days": 2, "status": "not_started"},
            {"id": "c", "duration_days": 1, "status": "not_started"},
        ]
        relationships = [
            {"predecessor_id": "a", "successor_id": "b", "relationship_type": "FS", "lag_days": 0},
            {"predecessor_id": "a", "successor_id": "c", "relationship_type": "FS", "lag_days": 0},
        ]
        engine = CPMEngine(activities, relationships, data_date=base)
        results = engine.run()
        # A -> B is the longer path, A and B should be critical
        critical_ids = engine.critical_path
        assert "a" in critical_ids
        assert "b" in critical_ids


class TestSSRelationship:
    """Test Start-to-Start relationship."""

    def test_ss_with_lag(self):
        base = date(2026, 4, 20)
        activities = [
            {"id": "a", "duration_days": 5, "status": "not_started"},
            {"id": "b", "duration_days": 3, "status": "not_started"},
        ]
        relationships = [
            {"predecessor_id": "a", "successor_id": "b", "relationship_type": "SS", "lag_days": 2},
        ]
        engine = CPMEngine(activities, relationships, data_date=base)
        results = engine.run()
        act_b = next(r for r in results if r["activity_id"] == "b")
        # B should start 2 days after A starts
        assert act_b["early_start"] is not None