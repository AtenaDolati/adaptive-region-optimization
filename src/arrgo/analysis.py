from dataclasses import dataclass

from .evaluation import Evaluation
from .regions import Region


@dataclass(frozen=True)
class RegionEvaluationView:
    region: Region
    evaluations: tuple[Evaluation, ...]

    @property
    def count(self) -> int:
        return len(self.evaluations)

    @property
    def best_evaluation(self) -> Evaluation | None:
        if not self.evaluations:
            return None

        return max(
            self.evaluations,
            key=lambda evaluation: evaluation.value,
        )

    @property
    def worst_evaluation(self) -> Evaluation | None:
        if not self.evaluations:
            return None

        return min(
            self.evaluations,
            key=lambda evaluation: evaluation.value,
        )


def build_region_evaluation_view(
    region: Region,
    evaluations: tuple[Evaluation, ...],
    coordinate_tolerance: float = 1e-12,
) -> RegionEvaluationView:
    region_evaluations = tuple(
        evaluation
        for evaluation in evaluations
        if region.contains(
            evaluation.x,
            tolerance=coordinate_tolerance,
        )
    )

    return RegionEvaluationView(
        region=region,
        evaluations=region_evaluations,
    )


@dataclass(frozen=True)
class RegionAnalysis:
    region_id: int
    evaluation_count: int
    best_value: float | None
    worst_value: float | None
    value_range: float | None
    coverage_resolution: float | None
    behavior_resolution: float | None
    observed_uncertainty: float | None
    observed_potential: float | None


def calculate_coverage_resolution(
    region: Region,
    evaluations: tuple[Evaluation, ...],
) -> float | None:
    if not evaluations:
        return None

    points = sorted(
        evaluation.x
        for evaluation in evaluations
    )

    gaps = [
        points[0] - region.left_x,
        region.right_x - points[-1],
    ]

    gaps.extend(
        right - left
        for left, right in zip(points, points[1:])
    )

    return max(gaps)


def calculate_behavior_resolution(
    evaluations: tuple[Evaluation, ...],
    coordinate_tolerance: float = 1e-12,
) -> float | None:
    if len(evaluations) < 2:
        return None

    ordered = sorted(
        evaluations,
        key=lambda evaluation: evaluation.x,
    )

    slopes: list[float] = []

    for left, right in zip(ordered, ordered[1:]):
        delta_x = right.x - left.x

        if abs(delta_x) <= coordinate_tolerance:
            continue

        slopes.append(
            (right.value - left.value) / delta_x
        )

    if not slopes:
        return None

    return max(slopes) - min(slopes)


def calculate_observed_uncertainty(
    evaluations: tuple[Evaluation, ...],
) -> float | None:
    if len(evaluations) < 2:
        return None

    values = [
        evaluation.value
        for evaluation in evaluations
    ]

    return max(values) - min(values)


def calculate_observed_potential(
    evaluations: tuple[Evaluation, ...],
) -> float | None:
    if not evaluations:
        return None

    return max(
        evaluation.value
        for evaluation in evaluations
    )


def analyze_region(
    region: Region,
    evaluations: tuple[Evaluation, ...],
    coordinate_tolerance: float = 1e-12,
) -> RegionAnalysis:
    view = build_region_evaluation_view(
        region=region,
        evaluations=evaluations,
        coordinate_tolerance=coordinate_tolerance,
    )

    if not view.evaluations:
        return RegionAnalysis(
            region_id=region.id,
            evaluation_count=0,
            best_value=None,
            worst_value=None,
            value_range=None,
            coverage_resolution=None,
            behavior_resolution=None,
            observed_uncertainty=None,
            observed_potential=None,
        )

    best_value = view.best_evaluation.value
    worst_value = view.worst_evaluation.value

    return RegionAnalysis(
        region_id=region.id,
        evaluation_count=view.count,
        best_value=best_value,
        worst_value=worst_value,
        value_range=best_value - worst_value,
        coverage_resolution=calculate_coverage_resolution(
            region=region,
            evaluations=view.evaluations,
        ),
        behavior_resolution=calculate_behavior_resolution(
            evaluations=view.evaluations,
            coordinate_tolerance=coordinate_tolerance,
        ),
        observed_uncertainty=calculate_observed_uncertainty(
            evaluations=view.evaluations,
        ),
        observed_potential=calculate_observed_potential(
            evaluations=view.evaluations,
        ),
    )