"""CPM Scheduling Engine.

This module implements the Critical Path Method (CPM) for project scheduling.
It performs forward pass, backward pass, float calculation, and critical path detection.

IMPORTANT: The scheduling engine must not load full ORM objects.
It uses flat dictionaries for computation.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


# ─── Data Structures ────────────────────────────────────

class ActivityData:
    """Lightweight data container for CPM computation."""

    __slots__ = [
        "id", "duration_days", "status", "is_milestone",
        "actual_start", "actual_finish", "remaining_duration_days",
        "percent_complete_method", "duration_percent_complete",
        "early_start", "early_finish",
        "late_start", "late_finish",
        "total_float", "free_float", "is_critical",
        "constraint_type", "constraint_date",
    ]

    def __init__(self, data: dict):
        self.id = data["id"]
        self.duration_days = float(data.get("duration_days") or 0)
        self.status = data.get("status", "not_started")
        self.is_milestone = data.get("is_milestone", False)
        self.actual_start = data.get("actual_start")
        self.actual_finish = data.get("actual_finish")
        self.remaining_duration_days = data.get("remaining_duration_days")
        if self.remaining_duration_days is not None:
            self.remaining_duration_days = float(self.remaining_duration_days)
        self.percent_complete_method = data.get("percent_complete_method", "Duration")
        self.duration_percent_complete = data.get("duration_percent_complete")
        self.constraint_type = data.get("constraint_type")
        self.constraint_date = data.get("constraint_date")
        # CPM results (filled during computation)
        self.early_start = None
        self.early_finish = None
        self.late_start = None
        self.late_finish = None
        self.total_float = None
        self.free_float = None
        self.is_critical = False


class RelationshipData:
    """Lightweight data container for dependency relationships."""

    __slots__ = ["predecessor_id", "successor_id", "relationship_type", "lag_days"]

    def __init__(self, data: dict):
        self.predecessor_id = data["predecessor_id"]
        self.successor_id = data["successor_id"]
        self.relationship_type = data["relationship_type"]
        self.lag_days = float(data.get("lag_days") or 0)


# ─── Calendar Helper ────────────────────────────────────

def add_working_days(
    start_date: date,
    days: float,
    working_days: List[int],
    holidays: Set[date],
) -> date:
    """Add working days to a start date, skipping non-working days and holidays.

    Args:
        start_date: The start date
        days: Number of working days to add (can be fractional)
        working_days: List of working day numbers (1=Mon, 7=Sun)
        holidays: Set of holiday dates

    Returns:
        The finish date after adding working days.
    """
    if days <= 0:
        return start_date

    current = start_date
    remaining = days

    # If start date is not a working day, move to next working day
    while current.isoweekday() not in working_days or current in holidays:
        current += timedelta(days=1)

    while remaining > 0:
        current += timedelta(days=1)
        if current.isoweekday() in working_days and current not in holidays:
            remaining -= 1

    return current


def next_working_day(
    d: date,
    working_days: List[int],
    holidays: Set[date],
) -> date:
    """Move to the next working day if the given date is non-working."""
    while d.isoweekday() not in working_days or d in holidays:
        d += timedelta(days=1)
    return d


def prev_working_day(
    d: date,
    working_days: List[int],
    holidays: Set[date],
) -> date:
    """Move to the previous working day if the given date is non-working."""
    while d.isoweekday() not in working_days or d in holidays:
        d -= timedelta(days=1)
    return d


# ─── Cycle Detection ────────────────────────────────────

def detect_circular_dependencies(
    relationships: List[RelationshipData],
) -> List[str]:
    """Detect circular dependencies using topological sort (Kahn's algorithm).

    Returns:
        List of warning messages for any cycles detected.
    """
    warnings = []
    graph = defaultdict(set)
    in_degree = defaultdict(int)
    all_nodes = set()

    for rel in relationships:
        graph[rel.predecessor_id].add(rel.successor_id)
        in_degree[rel.successor_id] += 1
        all_nodes.add(rel.predecessor_id)
        all_nodes.add(rel.successor_id)

    # Initialize in-degree for nodes with no predecessors
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0

    queue = deque([n for n in all_nodes if in_degree[n] == 0])
    processed = 0

    while queue:
        node = queue.popleft()
        processed += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if processed < len(all_nodes):
        cycle_nodes = all_nodes - set()
        remaining = {n for n in all_nodes if in_degree[n] > 0}
        warnings.append(
            f"Circular dependency detected involving {len(remaining)} activities: "
            f"{list(remaining)[:5]}..."
        )

    return warnings


# ─── Topological Sort ───────────────────────────────────

def topological_sort(
    activity_ids: Set[str],
    relationships: List[RelationshipData],
) -> List[str]:
    """Return activities in topological order for forward pass."""
    graph = defaultdict(set)
    in_degree = defaultdict(int)

    for aid in activity_ids:
        in_degree[aid] = 0

    for rel in relationships:
        if rel.predecessor_id in activity_ids and rel.successor_id in activity_ids:
            graph[rel.predecessor_id].add(rel.successor_id)
            in_degree[rel.successor_id] += 1

    queue = deque(sorted([n for n in activity_ids if in_degree[n] == 0]))
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in sorted(graph[node]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result


# ─── CPM Engine ─────────────────────────────────────────

class CPMEngine:
    """Critical Path Method scheduling engine.

    This engine performs:
    1. Forward pass (early dates)
    2. Backward pass (late dates)
    3. Float calculation
    4. Critical path detection
    5. Constraint handling
    6. Progress-aware recalculation
    """

    def __init__(
        self,
        activities: List[dict],
        relationships: List[dict],
        data_date: date,
        working_days: Optional[List[int]] = None,
        holidays: Optional[Set[date]] = None,
    ):
        self.data_date = data_date
        self.working_days = working_days or [1, 2, 3, 4, 5]
        self.holidays = holidays or set()

        # Parse activity data
        self.activities: Dict[str, ActivityData] = {}
        for a in activities:
            ad = ActivityData(a)
            self.activities[ad.id] = ad

        # Parse relationships
        self.relationships: List[RelationshipData] = [
            RelationshipData(r) for r in relationships
        ]

        # Build adjacency lists
        self.predecessors: Dict[str, List[RelationshipData]] = defaultdict(list)
        self.successors: Dict[str, List[RelationshipData]] = defaultdict(list)

        for rel in self.relationships:
            self.predecessors[rel.successor_id].append(rel)
            self.successors[rel.predecessor_id].append(rel)

        self.warnings: List[str] = []
        self.critical_path: List[str] = []

    def run(self) -> List[dict]:
        """Execute the full CPM calculation.

        Returns:
            List of activity results with CPM-calculated dates.
        """
        # Validate: detect circular dependencies
        cycle_warnings = detect_circular_dependencies(self.relationships)
        if cycle_warnings:
            self.warnings.extend(cycle_warnings)
            logger.warning("Circular dependencies detected: %s", cycle_warnings)
            return self._build_results()

        # Apply constraints first
        self._apply_constraints()

        # Forward pass
        self._forward_pass()

        # Backward pass
        self._backward_pass()

        # Calculate float and identify critical path
        self._calculate_float()

        return self._build_results()

    def _get_effective_duration(self, activity: ActivityData) -> float:
        """Get the effective duration for an activity considering progress."""
        # Milestones have zero duration
        if activity.is_milestone:
            return 0

        # Completed activities: duration is based on actual dates
        if activity.status == "completed" and activity.actual_start and activity.actual_finish:
            return 0  # Already finished, no remaining

        # In-progress activities: use remaining duration
        if activity.status == "in_progress":
            if activity.remaining_duration_days is not None:
                return activity.remaining_duration_days
            # Estimate remaining from percent complete
            pct = float(activity.duration_percent_complete or 0)
            if 0 < pct < 100:
                remaining = activity.duration_days * (100 - pct) / 100
                return remaining
            return 0

        # Not started: use full duration
        return activity.duration_days

    def _apply_constraints(self):
        """Apply activity constraints to set initial dates."""
        for activity in self.activities.values():
            if not activity.constraint_type or not activity.constraint_date:
                continue

            constraint_date = activity.constraint_date

            if activity.constraint_type == "must_start_on":
                activity.early_start = constraint_date
            elif activity.constraint_type == "must_finish_on":
                activity.early_finish = constraint_date
            elif activity.constraint_type == "start_no_earlier_than":
                if activity.early_start is None or activity.early_start < constraint_date:
                    activity.early_start = constraint_date
            elif activity.constraint_type == "finish_no_later_than":
                if activity.late_finish is None or activity.late_finish > constraint_date:
                    activity.late_finish = constraint_date

    def _forward_pass(self):
        """Forward pass: calculate early start and early finish dates.

        Process activities in topological order.
        For each activity, early_start is the maximum of:
        - Data date (if not completed and no actual start)
        - Predecessor's early finish + lag (for FS)
        - Predecessor's early start + lag (for SS)
        - Constraint dates
        - Actual start (if available)
        """
        activity_ids = set(self.activities.keys())
        topo_order = topological_sort(activity_ids, self.relationships)

        for aid in topo_order:
            activity = self.activities[aid]
            duration = self._get_effective_duration(activity)

            # Handle completed activities
            if activity.status == "completed":
                if activity.actual_start:
                    activity.early_start = activity.actual_start
                if activity.actual_finish:
                    activity.early_finish = activity.actual_finish
                elif activity.early_start:
                    activity.early_finish = add_working_days(
                        activity.early_start, duration,
                        self.working_days, self.holidays,
                    )
                continue

            # Handle in-progress activities
            if activity.status == "in_progress":
                # Respect actual start date
                if activity.actual_start:
                    activity.early_start = activity.actual_start
                else:
                    activity.early_start = self.data_date

                # Recalculate from predecessors
                max_predecessor_start = activity.early_start
                for rel in self.predecessors.get(aid, []):
                    pred = self.activities.get(rel.predecessor_id)
                    if pred and pred.early_finish:
                        proposed = self._calculate_successor_start(
                            pred, rel, duration
                        )
                        if proposed > max_predecessor_start:
                            max_predecessor_start = proposed

                activity.early_start = max(
                    next_working_day(max_predecessor_start, self.working_days, self.holidays),
                    next_working_day(self.data_date, self.working_days, self.holidays),
                )

                activity.early_finish = add_working_days(
                    activity.early_start, duration,
                    self.working_days, self.holidays,
                )
                continue

            # Not started activities
            max_start = self.data_date

            # Check all predecessor relationships
            for rel in self.predecessors.get(aid, []):
                pred = self.activities.get(rel.predecessor_id)
                if not pred:
                    continue

                proposed = self._calculate_successor_start(pred, rel, duration)
                if proposed > max_start:
                    max_start = proposed

            # Apply constraints
            if activity.constraint_type == "must_start_on" and activity.constraint_date:
                max_start = activity.constraint_date
            elif activity.constraint_type == "start_no_earlier_than" and activity.constraint_date:
                if max_start < activity.constraint_date:
                    max_start = activity.constraint_date
            elif activity.constraint_type == "must_finish_on" and activity.constraint_date:
                # Back-calculate start from finish
                finish = activity.constraint_date
                start = finish - timedelta(days=int(duration))
                if max_start < start:
                    max_start = start

            activity.early_start = next_working_day(max_start, self.working_days, self.holidays)
            activity.early_finish = add_working_days(
                activity.early_start, duration,
                self.working_days, self.holidays,
            )

    def _calculate_successor_start(
        self, pred: ActivityData, rel: RelationshipData, succ_duration: float
    ) -> date:
        """Calculate the successor start date based on predecessor and relationship type."""
        pred_start = pred.early_start or self.data_date
        pred_finish = pred.early_finish or self.data_date

        lag = timedelta(days=rel.lag_days)

        if rel.relationship_type == "FS":
            # Successor starts after predecessor finishes + lag
            return pred_finish + lag
        elif rel.relationship_type == "SS":
            # Successor starts after predecessor starts + lag
            return pred_start + lag
        elif rel.relationship_type == "FF":
            # Successor finishes when predecessor finishes + lag
            # Back-calculate start from finish
            finish = pred_finish + lag
            return finish - timedelta(days=int(succ_duration))
        elif rel.relationship_type == "SF":
            # Predecessor starts when successor finishes + lag
            # i.e., successor finishes before predecessor starts
            finish = pred_start - lag
            return finish - timedelta(days=int(succ_duration))
        else:
            self.warnings.append(
                f"Unknown relationship type {rel.relationship_type} "
                f"between {rel.predecessor_id} and {rel.successor_id}"
            )
            return pred_finish + lag

    def _backward_pass(self):
        """Backward pass: calculate late start and late finish dates.

        Process activities in reverse topological order.
        For each activity, late_finish is the minimum of:
        - Successor's late start - lag (for FS)
        - Successor's late finish - lag (for FF)
        - Project finish date (for activities with no successors)
        """
        activity_ids = set(self.activities.keys())
        topo_order = topological_sort(activity_ids, self.relationships)

        # Find project end date (maximum early finish)
        project_finish = self.data_date
        for activity in self.activities.values():
            if activity.early_finish and activity.early_finish > project_finish:
                project_finish = activity.early_finish

        # Initialize late_finish for all activities to project finish
        for activity in self.activities.values():
            activity.late_finish = project_finish

        # Process in reverse topological order
        for aid in reversed(topo_order):
            activity = self.activities[aid]
            duration = self._get_effective_duration(activity)

            # Handle completed activities
            if activity.status == "completed":
                activity.late_start = activity.early_start
                activity.late_finish = activity.early_finish
                continue

            # If activity has no successors, late_finish = project_finish
            successor_rels = self.successors.get(aid, [])
            if not successor_rels:
                activity.late_finish = project_finish
            else:
                # Late finish is the minimum of all successor constraints
                min_late = project_finish
                for rel in successor_rels:
                    succ = self.activities.get(rel.successor_id)
                    if not succ or not succ.late_start:
                        continue

                    lag = timedelta(days=rel.lag_days)

                    if rel.relationship_type == "FS":
                        # Predecessor must finish before successor starts - lag
                        proposed = succ.late_start - lag
                        if proposed < min_late:
                            min_late = proposed
                    elif rel.relationship_type == "SS":
                        # Predecessor starts before successor starts - lag
                        proposed = succ.late_start - lag + timedelta(days=int(duration))
                        if proposed < min_late:
                            min_late = proposed
                    elif rel.relationship_type == "FF":
                        # Predecessor finishes before successor finishes - lag
                        proposed = succ.late_finish - lag if succ.late_finish else project_finish
                        if proposed < min_late:
                            min_late = proposed
                    elif rel.relationship_type == "SF":
                        proposed = succ.late_finish - lag if succ.late_finish else project_finish
                        if proposed < min_late:
                            min_late = proposed

                activity.late_finish = prev_working_day(min_late, self.working_days, self.holidays)

            # Apply constraint: finish_no_later_than
            if activity.constraint_type == "finish_no_later_than" and activity.constraint_date:
                if activity.late_finish > activity.constraint_date:
                    activity.late_finish = activity.constraint_date

            # Calculate late start
            if duration > 0:
                activity.late_start = activity.late_finish - timedelta(days=int(duration))
                activity.late_start = prev_working_day(activity.late_start, self.working_days, self.holidays)
            else:
                activity.late_start = activity.late_finish

    def _calculate_float(self):
        """Calculate total float, free float, and identify critical path."""
        critical_activities = []

        for aid, activity in self.activities.items():
            if activity.early_start and activity.late_start:
                # Total float = late_start - early_start (in working days)
                es = activity.early_start
                ls = activity.late_start
                activity.total_float = Decimal(str((ls - es).days))

                # Free float: how much the activity can slip without delaying successors
                min_successor_es = None
                for rel in self.successors.get(aid, []):
                    succ = self.activities.get(rel.successor_id)
                    if succ and succ.early_start:
                        lag = timedelta(days=rel.lag_days)
                        if rel.relationship_type == "FS":
                            successor_available = succ.early_start - lag
                        elif rel.relationship_type == "SS":
                            successor_available = succ.early_start - lag
                        elif rel.relationship_type == "FF":
                            successor_available = (succ.early_finish or succ.early_start) - lag - timedelta(days=int(self._get_effective_duration(activity)))
                        else:
                            successor_available = succ.early_start - lag

                        if min_successor_es is None or successor_available < min_successor_es:
                            min_successor_es = successor_available

                if min_successor_es is not None and activity.early_finish:
                    activity.free_float = Decimal(str((min_successor_es - activity.early_finish).days))
                else:
                    activity.free_float = activity.total_float

                # Critical if total float <= 0
                if activity.total_float <= 0:
                    activity.is_critical = True
                    critical_activities.append(aid)
            else:
                activity.total_float = Decimal("0")
                activity.free_float = Decimal("0")
                activity.is_critical = False

        self.critical_path = critical_activities

    def _build_results(self) -> List[dict]:
        """Build the result list from computed activity data."""
        results = []
        for aid, activity in self.activities.items():
            results.append({
                "activity_id": aid,
                "early_start": activity.early_start,
                "early_finish": activity.early_finish,
                "late_start": activity.late_start,
                "late_finish": activity.late_finish,
                "total_float": activity.total_float,
                "free_float": activity.free_float,
                "is_critical": activity.is_critical,
                "status": activity.status,
            })
        return results