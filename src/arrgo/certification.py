from dataclasses import dataclass

from .evaluation import Evaluation
from .regions import Region


@dataclass(frozen=True)
class RegionalBounds:
    lower_value: float
    upper_value: float
    uncertainty: float
    potential: float


def calculate_lower_envelope(
    x: float,
    evaluations: tuple[Evaluation, ...],
    lipschitz_constant: float,
) -> float:
    if not evaluations:
        raise ValueError(
            "At least one evaluation is required."
        )

    return max(
        evaluation.value
        - lipschitz_constant * abs(x - evaluation.x)
        for evaluation in evaluations
    )


def calculate_upper_envelope(
    x: float,
    evaluations: tuple[Evaluation, ...],
    lipschitz_constant: float,
) -> float:
    if not evaluations:
        raise ValueError(
            "At least one evaluation is required."
        )

    return min(
        evaluation.value
        + lipschitz_constant * abs(x - evaluation.x)
        for evaluation in evaluations
    )


def calculate_regional_uncertainty(
    x: float,
    evaluations: tuple[Evaluation, ...],
    lipschitz_constant: float,
) -> float:
    lower = calculate_lower_envelope(
        x=x,
        evaluations=evaluations,
        lipschitz_constant=lipschitz_constant,
    )

    upper = calculate_upper_envelope(
        x=x,
        evaluations=evaluations,
        lipschitz_constant=lipschitz_constant,
    )

    return upper - lower


def calculate_regional_potential(
    x: float,
    evaluations: tuple[Evaluation, ...],
    lipschitz_constant: float,
) -> float:
    return calculate_upper_envelope(
        x=x,
        evaluations=evaluations,
        lipschitz_constant=lipschitz_constant,
    )


def _candidate_points(
    region: Region,
    evaluations: tuple[Evaluation, ...],
    lipschitz_constant: float,
) -> tuple[float, ...]:
    points = {
        region.left_x,
        region.right_x,
    }

    for evaluation in evaluations:
        if region.contains(evaluation.x):
            points.add(evaluation.x)

    for first_index, first in enumerate(evaluations):
        if not region.contains(first.x):
            continue

        for second in evaluations[first_index + 1:]:
            if not region.contains(second.x):
                continue

            if abs(first.x - second.x) <= 1e-12:
                continue

            intersection = (
                second.value
                - first.value
                + lipschitz_constant
                * (first.x + second.x)
            ) / (2.0 * lipschitz_constant)

            if region.left_x <= intersection <= region.right_x:
                points.add(intersection)

    return tuple(sorted(points))


def calculate_exact_regional_bounds(
    region: Region,
    evaluations: tuple[Evaluation, ...],
    lipschitz_constant: float,
) -> RegionalBounds:
    region_evaluations = tuple(
        evaluation
        for evaluation in evaluations
        if region.contains(evaluation.x)
    )

    if not region_evaluations:
        raise ValueError(
            "Region must contain at least one evaluation."
        )

    candidate_points = _candidate_points(
        region=region,
        evaluations=region_evaluations,
        lipschitz_constant=lipschitz_constant,
    )

    upper_values = tuple(
        calculate_upper_envelope(
            x=x,
            evaluations=region_evaluations,
            lipschitz_constant=lipschitz_constant,
        )
        for x in candidate_points
    )

    lower_values = tuple(
        calculate_lower_envelope(
            x=x,
            evaluations=region_evaluations,
            lipschitz_constant=lipschitz_constant,
        )
        for x in candidate_points
    )

    upper_value = max(upper_values)
    lower_value = min(lower_values)

    uncertainty = max(
        upper - lower
        for upper, lower in zip(
            upper_values,
            lower_values,
        )
    )

    return RegionalBounds(
        lower_value=lower_value,
        upper_value=upper_value,
        uncertainty=uncertainty,
        potential=upper_value,
    )