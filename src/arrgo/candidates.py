from dataclasses import dataclass
from enum import Enum

from .analysis import RegionAnalysis
from .evaluation import Evaluation
from .regions import Region


class RefinementAction(Enum):
    SAMPLE = "sample"
    SPLIT = "split"
    STABLE = "stable"


@dataclass(frozen=True)
class Candidate:
    location: float
    action: RefinementAction
    region_id: int
    score: float | None = None


def generate_sampling_candidates(
    region: Region,
    evaluations: tuple[Evaluation, ...],
    coordinate_tolerance: float = 1e-12,
) -> tuple[Candidate, ...]:
    region_evaluations = tuple(
        evaluation
        for evaluation in evaluations
        if region.contains(
            evaluation.x,
            tolerance=coordinate_tolerance,
        )
    )

    if not region_evaluations:
        return (
            Candidate(
                location=region.midpoint,
                action=RefinementAction.SAMPLE,
                region_id=region.id,
            ),
        )

    points = sorted(
        evaluation.x
        for evaluation in region_evaluations
    )

    raw_locations = [
        region.left_x,
        region.right_x,
        region.midpoint,
    ]

    raw_locations.extend(
        (left + right) / 2.0
        for left, right in zip(points, points[1:])
    )

    candidates: list[Candidate] = []

    for location in raw_locations:
        if not region.contains(
            location,
            tolerance=coordinate_tolerance,
        ):
            continue

        if any(
            abs(location - point) <= coordinate_tolerance
            for point in points
        ):
            continue

        if any(
            abs(location - candidate.location)
            <= coordinate_tolerance
            for candidate in candidates
        ):
            continue

        candidates.append(
            Candidate(
                location=location,
                action=RefinementAction.SAMPLE,
                region_id=region.id,
            )
        )

    return tuple(candidates)


def evaluate_sampling_candidate(
    candidate: Candidate,
    evaluations: tuple[Evaluation, ...],
    coordinate_tolerance: float = 1e-12,
) -> Candidate:
    if candidate.action != RefinementAction.SAMPLE:
        raise ValueError(
            "Only sampling candidates can be evaluated."
        )

    if any(
        abs(candidate.location - evaluation.x)
        <= coordinate_tolerance
        for evaluation in evaluations
    ):
        raise ValueError(
            "Sampling candidate has already been evaluated."
        )

    return candidate


def select_sampling_candidate(
    candidates: tuple[Candidate, ...],
    evaluations: tuple[Evaluation, ...],
    coordinate_tolerance: float = 1e-12,
) -> Candidate | None:
    if not candidates:
        return None

    points = sorted(
        evaluation.x
        for evaluation in evaluations
    )

    valid_candidates = tuple(
        candidate
        for candidate in candidates
        if not any(
            abs(candidate.location - point)
            <= coordinate_tolerance
            for point in points
        )
    )

    if not valid_candidates:
        return None

    if not points:
        return valid_candidates[0]

    def nearest_distance(location: float) -> float:
        return min(
            abs(location - point)
            for point in points
        )

    return max(
        valid_candidates,
        key=lambda candidate: (
            nearest_distance(candidate.location),
            -candidate.location,
        ),
    )


@dataclass(frozen=True)
class SplitCandidate:
    region_id: int
    split_location: float
    contraction_valid: bool
    structural_value: float = 0.0
    structural_difference: float = 0.0
    directional_difference: float = 0.0
    slope_variation_difference: float = 0.0
    coverage_difference: float = 0.0
    uncertainty_difference: float = 0.0
    potential_difference: float = 0.0


def generate_split_locations(
    region: Region,
    contraction_factor: float,
) -> tuple[float, ...]:
    if not 0.0 < contraction_factor < 1.0:
        raise ValueError(
            "contraction_factor must be strictly between 0 and 1."
        )

    if contraction_factor < 0.5:
        return ()

    lower = (
        contraction_factor * region.left_x
        + (1.0 - contraction_factor) * region.right_x
    )

    upper = (
        (1.0 - contraction_factor) * region.left_x
        + contraction_factor * region.right_x
    )

    if lower > upper:
        return ()

    if abs(lower - upper) <= 1e-12:
        return (region.midpoint,)

    return (
        lower,
        region.midpoint,
        upper,
    )


def build_split_candidates(
    region: Region,
    contraction_factor: float,
    coordinate_tolerance: float = 1e-12,
) -> tuple[SplitCandidate, ...]:
    locations = generate_split_locations(
        region=region,
        contraction_factor=contraction_factor,
    )

    candidates: list[SplitCandidate] = []

    for location in locations:
        if not region.left_x + coordinate_tolerance < location:
            continue

        if not location < region.right_x - coordinate_tolerance:
            continue

        candidates.append(
            SplitCandidate(
                region_id=region.id,
                split_location=location,
                contraction_valid=True,
            )
        )

    return tuple(candidates)


def calculate_structural_value(
    region: Region,
    split_location: float,
) -> float:
    left_width = split_location - region.left_x
    right_width = region.right_x - split_location

    if left_width <= 0.0 or right_width <= 0.0:
        return 0.0

    return min(
        left_width,
        right_width,
    ) / region.width


def calculate_structural_difference(
    region: Region,
    split_location: float,
) -> float:
    return abs(
        (split_location - region.left_x)
        - (region.right_x - split_location)
    )


def calculate_directional_difference(
    region: Region,
    evaluations: tuple[Evaluation, ...],
    split_location: float,
) -> float:
    left_values = [
        evaluation.value
        for evaluation in evaluations
        if region.left_x <= evaluation.x <= split_location
    ]

    right_values = [
        evaluation.value
        for evaluation in evaluations
        if split_location <= evaluation.x <= region.right_x
    ]

    if not left_values or not right_values:
        return 0.0

    left_mean = sum(left_values) / len(left_values)
    right_mean = sum(right_values) / len(right_values)

    return abs(left_mean - right_mean)


def _calculate_slopes(
    evaluations: tuple[Evaluation, ...],
    coordinate_tolerance: float,
) -> tuple[float, ...]:
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

    return tuple(slopes)


def calculate_slope_variation_difference(
    region: Region,
    evaluations: tuple[Evaluation, ...],
    split_location: float,
    coordinate_tolerance: float = 1e-12,
) -> float:
    left_evaluations = tuple(
        evaluation
        for evaluation in evaluations
        if region.left_x <= evaluation.x <= split_location
    )

    right_evaluations = tuple(
        evaluation
        for evaluation in evaluations
        if split_location <= evaluation.x <= region.right_x
    )

    left_slopes = _calculate_slopes(
        left_evaluations,
        coordinate_tolerance,
    )

    right_slopes = _calculate_slopes(
        right_evaluations,
        coordinate_tolerance,
    )

    if not left_slopes or not right_slopes:
        return 0.0

    left_variation = max(left_slopes) - min(left_slopes)
    right_variation = max(right_slopes) - min(right_slopes)

    return abs(
        left_variation - right_variation
    )


def calculate_coverage_difference(
    region: Region,
    evaluations: tuple[Evaluation, ...],
    split_location: float,
    coordinate_tolerance: float = 1e-12,
) -> float:
    left_evaluations = tuple(
        evaluation
        for evaluation in evaluations
        if region.left_x <= evaluation.x <= split_location
    )

    right_evaluations = tuple(
        evaluation
        for evaluation in evaluations
        if split_location <= evaluation.x <= region.right_x
    )

    left_coverage = _coverage_resolution(
        region.left_x,
        split_location,
        left_evaluations,
        coordinate_tolerance,
    )

    right_coverage = _coverage_resolution(
        split_location,
        region.right_x,
        right_evaluations,
        coordinate_tolerance,
    )

    return abs(
        left_coverage - right_coverage
    )


def _coverage_resolution(
    left_x: float,
    right_x: float,
    evaluations: tuple[Evaluation, ...],
    coordinate_tolerance: float,
) -> float:
    if not evaluations:
        return right_x - left_x

    points = sorted(
        evaluation.x
        for evaluation in evaluations
    )

    gaps = [
        points[0] - left_x,
        right_x - points[-1],
    ]

    gaps.extend(
        right - left
        for left, right in zip(points, points[1:])
    )

    return max(gaps)


def calculate_uncertainty_difference(
    left_uncertainty: float | None,
    right_uncertainty: float | None,
) -> float:
    if left_uncertainty is None or right_uncertainty is None:
        return 0.0

    return abs(
        left_uncertainty - right_uncertainty
    )


def calculate_potential_difference(
    left_potential: float | None,
    right_potential: float | None,
) -> float:
    if left_potential is None or right_potential is None:
        return 0.0

    return abs(
        left_potential - right_potential
    )


@dataclass(frozen=True)
class StructuralDifferenceProfile:
    structural: float
    directional: float
    slope_variation: float
    coverage: float
    uncertainty: float
    potential: float


def build_split_profile(
    region: Region,
    evaluations: tuple[Evaluation, ...],
    split_location: float,
    left_analysis: RegionAnalysis,
    right_analysis: RegionAnalysis,
    coordinate_tolerance: float = 1e-12,
) -> StructuralDifferenceProfile:
    return StructuralDifferenceProfile(
        structural=calculate_structural_difference(
            region=region,
            split_location=split_location,
        ),
        directional=calculate_directional_difference(
            region=region,
            evaluations=evaluations,
            split_location=split_location,
        ),
        slope_variation=calculate_slope_variation_difference(
            region=region,
            evaluations=evaluations,
            split_location=split_location,
            coordinate_tolerance=coordinate_tolerance,
        ),
        coverage=calculate_coverage_difference(
            region=region,
            evaluations=evaluations,
            split_location=split_location,
            coordinate_tolerance=coordinate_tolerance,
        ),
        uncertainty=calculate_uncertainty_difference(
            left_analysis.observed_uncertainty,
            right_analysis.observed_uncertainty,
        ),
        potential=calculate_potential_difference(
            left_analysis.observed_potential,
            right_analysis.observed_potential,
        ),
    )


def dominates(
    first: StructuralDifferenceProfile,
    second: StructuralDifferenceProfile,
    tolerance: float = 1e-12,
) -> bool:
    first_values = (
        first.structural,
        first.directional,
        first.slope_variation,
        first.coverage,
        first.uncertainty,
        first.potential,
    )

    second_values = (
        second.structural,
        second.directional,
        second.slope_variation,
        second.coverage,
        second.uncertainty,
        second.potential,
    )

    return (
        all(
            first_value >= second_value - tolerance
            for first_value, second_value
            in zip(first_values, second_values)
        )
        and any(
            first_value > second_value + tolerance
            for first_value, second_value
            in zip(first_values, second_values)
        )
    )


def select_non_dominated_splits(
    candidates: tuple[SplitCandidate, ...],
    profiles: tuple[StructuralDifferenceProfile, ...],
    tolerance: float = 1e-12,
) -> tuple[SplitCandidate, ...]:
    if len(candidates) != len(profiles):
        raise ValueError(
            "Candidates and profiles must have equal length."
        )

    selected: list[SplitCandidate] = []

    for index, candidate in enumerate(candidates):
        dominated = False

        for other_index, other_profile in enumerate(profiles):
            if index == other_index:
                continue

            if dominates(
                other_profile,
                profiles[index],
                tolerance=tolerance,
            ):
                dominated = True
                break

        if not dominated:
            selected.append(candidate)

    return tuple(selected)