from dataclasses import dataclass

from .analysis import RegionAnalysis
from .candidates import (
    Candidate,
    RefinementAction,
    SplitCandidate,
    StructuralDifferenceProfile,
    dominates,
)


@dataclass(frozen=True)
class RegionRefinementObjective:
    coverage: float
    behavior: float
    uncertainty: float
    potential: float

    @property
    def unresolved_count(self) -> int:
        return sum(
            value > 0.0
            for value in (
                self.coverage,
                self.behavior,
                self.uncertainty,
                self.potential,
            )
        )


@dataclass(frozen=True)
class CoverageResolutionObjective:
    value: float


@dataclass(frozen=True)
class BehaviorResolutionObjective:
    value: float


@dataclass(frozen=True)
class UncertaintyResolutionObjective:
    value: float


@dataclass(frozen=True)
class OptimizationPotentialResolutionObjective:
    value: float


@dataclass(frozen=True)
class UnresolvedInformationState:
    coverage: float
    behavior: float
    uncertainty: float
    potential: float

    @property
    def unresolved_count(self) -> int:
        return sum(
            value > 0.0
            for value in (
                self.coverage,
                self.behavior,
                self.uncertainty,
                self.potential,
            )
        )


@dataclass(frozen=True)
class ResolutionCriteria:
    coverage_tolerance: float = 1e-12
    behavior_tolerance: float = 1e-12
    uncertainty_tolerance: float = 1e-12
    potential_tolerance: float = 1e-12

    def is_resolved(
        self,
        state: UnresolvedInformationState,
    ) -> bool:
        return (
            state.coverage <= self.coverage_tolerance
            and state.behavior <= self.behavior_tolerance
            and state.uncertainty <= self.uncertainty_tolerance
            and state.potential <= self.potential_tolerance
        )


@dataclass(frozen=True)
class DecisionStability:
    repeated_decisions: int = 0
    required_repetitions: int = 2

    @property
    def is_stable(self) -> bool:
        return (
            self.repeated_decisions
            >= self.required_repetitions
        )


def calculate_region_refinement_objective(
    analysis: RegionAnalysis,
) -> RegionRefinementObjective:
    return RegionRefinementObjective(
        coverage=(
            analysis.coverage_resolution
            if analysis.coverage_resolution is not None
            else 0.0
        ),
        behavior=(
            analysis.behavior_resolution
            if analysis.behavior_resolution is not None
            else 0.0
        ),
        uncertainty=(
            analysis.observed_uncertainty
            if analysis.observed_uncertainty is not None
            else 0.0
        ),
        potential=(
            analysis.observed_potential
            if analysis.observed_potential is not None
            else 0.0
        ),
    )


def calculate_coverage_resolution_objective(
    analysis: RegionAnalysis,
) -> CoverageResolutionObjective:
    return CoverageResolutionObjective(
        value=(
            analysis.coverage_resolution
            if analysis.coverage_resolution is not None
            else 0.0
        )
    )


def calculate_behavior_resolution_objective(
    analysis: RegionAnalysis,
) -> BehaviorResolutionObjective:
    return BehaviorResolutionObjective(
        value=(
            analysis.behavior_resolution
            if analysis.behavior_resolution is not None
            else 0.0
        )
    )


def calculate_uncertainty_resolution_objective(
    analysis: RegionAnalysis,
) -> UncertaintyResolutionObjective:
    return UncertaintyResolutionObjective(
        value=(
            analysis.observed_uncertainty
            if analysis.observed_uncertainty is not None
            else 0.0
        )
    )


def calculate_optimization_potential_resolution_objective(
    analysis: RegionAnalysis,
) -> OptimizationPotentialResolutionObjective:
    return OptimizationPotentialResolutionObjective(
        value=(
            analysis.observed_potential
            if analysis.observed_potential is not None
            else 0.0
        )
    )


def build_unresolved_information_state(
    analysis: RegionAnalysis,
) -> UnresolvedInformationState:
    objective = calculate_region_refinement_objective(
        analysis
    )

    return UnresolvedInformationState(
        coverage=objective.coverage,
        behavior=objective.behavior,
        uncertainty=objective.uncertainty,
        potential=objective.potential,
    )


def select_non_dominated_profiles(
    profiles: tuple[StructuralDifferenceProfile, ...],
    tolerance: float = 1e-12,
) -> tuple[StructuralDifferenceProfile, ...]:
    selected: list[StructuralDifferenceProfile] = []

    for index, profile in enumerate(profiles):
        is_dominated = False

        for other_index, other in enumerate(profiles):
            if index == other_index:
                continue

            if dominates(
                other,
                profile,
                tolerance=tolerance,
            ):
                is_dominated = True
                break

        if not is_dominated:
            selected.append(profile)

    return tuple(selected)


def select_split_candidate(
    candidates: tuple[SplitCandidate, ...],
    profiles: tuple[StructuralDifferenceProfile, ...],
    tolerance: float = 1e-12,
) -> SplitCandidate | None:
    if not candidates:
        return None

    if len(candidates) != len(profiles):
        raise ValueError(
            "Candidates and profiles must have equal length."
        )

    non_dominated_indices: list[int] = []

    for index, profile in enumerate(profiles):
        dominated_profile = False

        for other_index, other in enumerate(profiles):
            if index == other_index:
                continue

            if dominates(
                other,
                profile,
                tolerance=tolerance,
            ):
                dominated_profile = True
                break

        if not dominated_profile:
            non_dominated_indices.append(index)

    if not non_dominated_indices:
        return None

    return max(
        (
            candidates[index]
            for index in non_dominated_indices
        ),
        key=lambda candidate: (
            candidate.structural_value,
            -abs(candidate.split_location),
        ),
    )


def select_refinement_action(
    analysis: RegionAnalysis,
    sampling_candidates: tuple[Candidate, ...],
    split_candidate: SplitCandidate | None,
    criteria: ResolutionCriteria | None = None,
) -> RefinementAction:
    if criteria is None:
        criteria = ResolutionCriteria()

    information_state = build_unresolved_information_state(
        analysis
    )

    if criteria.is_resolved(information_state):
        return RefinementAction.STABLE

    if split_candidate is not None:
        if (
            information_state.behavior
            > information_state.coverage
        ):
            return RefinementAction.SPLIT

    if sampling_candidates:
        return RefinementAction.SAMPLE

    if split_candidate is not None:
        return RefinementAction.SPLIT

    return RefinementAction.STABLE


def build_refinement_decision(
    analysis: RegionAnalysis,
    sampling_candidates: tuple[Candidate, ...],
    split_candidate: SplitCandidate | None,
    criteria: ResolutionCriteria | None = None,
) -> tuple[RefinementAction, Candidate | SplitCandidate | None]:
    action = select_refinement_action(
        analysis=analysis,
        sampling_candidates=sampling_candidates,
        split_candidate=split_candidate,
        criteria=criteria,
    )

    if action == RefinementAction.SAMPLE:
        return (
            action,
            sampling_candidates[0]
            if sampling_candidates
            else None,
        )

    if action == RefinementAction.SPLIT:
        return action, split_candidate

    return action, None