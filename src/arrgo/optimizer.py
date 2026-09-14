from dataclasses import dataclass
from typing import Callable, Protocol

from .analysis import RegionAnalysis, analyze_region
from .candidates import (
    Candidate,
    RefinementAction,
    SplitCandidate,
    StructuralDifferenceProfile,
    build_split_candidates,
    build_split_profile,
    generate_sampling_candidates,
    select_sampling_candidate,
)
from .certification import calculate_exact_regional_bounds
from .config import ARRGOConfig
from .evaluation import Evaluation, EvaluationHistory
from .refinement import (
    ResolutionCriteria,
    select_refinement_action,
    select_split_candidate,
)
from .regions import Region, RegionHierarchy, RegionState
from .termination import (
    TerminationStatus,
    determine_termination,
)


class ObjectiveFunction(Protocol):
    def __call__(self, x: float) -> float:
        ...


class CallableObjective:
    def __init__(
        self,
        function: Callable[[float], float],
    ) -> None:
        self._function = function

    def __call__(self, x: float) -> float:
        return self._function(x)


class ObjectiveEvaluator:
    def __init__(
        self,
        objective: ObjectiveFunction,
        history: EvaluationHistory,
    ) -> None:
        self._objective = objective
        self._history = history

    @property
    def history(self) -> EvaluationHistory:
        return self._history

    def evaluate(self, x: float) -> Evaluation:
        value = self._objective(x)

        evaluation = Evaluation(
            x=x,
            value=value,
            id=self._history.count,
        )

        self._history.add(evaluation)

        return evaluation


@dataclass
class ARRGOGlobalState:
    evaluation_history: EvaluationHistory
    region_hierarchy: RegionHierarchy
    best_evaluation: Evaluation | None = None

    @property
    def evaluation_count(self) -> int:
        return self.evaluation_history.count

    @property
    def best_x(self) -> float | None:
        if self.best_evaluation is None:
            return None

        return self.best_evaluation.x

    @property
    def best_value(self) -> float | None:
        if self.best_evaluation is None:
            return None

        return self.best_evaluation.value


def create_initial_global_state() -> ARRGOGlobalState:
    return ARRGOGlobalState(
        evaluation_history=EvaluationHistory(),
        region_hierarchy=RegionHierarchy(),
    )


def update_global_incumbent(
    state: ARRGOGlobalState,
) -> ARRGOGlobalState:
    best_evaluation = state.evaluation_history.best()

    state.best_evaluation = best_evaluation

    return state


def count_unresolved_objectives(
    analysis: RegionAnalysis,
) -> int:
    return sum(
        value is not None and value > 0.0
        for value in (
            analysis.coverage_resolution,
            analysis.behavior_resolution,
            analysis.observed_uncertainty,
            analysis.observed_potential,
        )
    )


def build_global_region_priority(
    region: Region,
    analysis: RegionAnalysis,
) -> tuple:
    return (
        count_unresolved_objectives(analysis),
        (
            analysis.observed_potential
            if analysis.observed_potential is not None
            else float("-inf")
        ),
        (
            analysis.coverage_resolution
            if analysis.coverage_resolution is not None
            else float("-inf")
        ),
        (
            analysis.behavior_resolution
            if analysis.behavior_resolution is not None
            else float("-inf")
        ),
        region.width,
        -region.id,
    )


def select_global_region(
    regions: tuple[Region, ...],
    evaluations: tuple[Evaluation, ...],
    coordinate_tolerance: float = 1e-12,
) -> Region | None:
    active_regions = tuple(
        region
        for region in regions
        if region.state == RegionState.ACTIVE
    )

    if not active_regions:
        return None

    ranked_regions = []

    for region in active_regions:
        analysis = analyze_region(
            region=region,
            evaluations=evaluations,
            coordinate_tolerance=coordinate_tolerance,
        )

        priority = build_global_region_priority(
            region=region,
            analysis=analysis,
        )

        ranked_regions.append(
            (priority, region)
        )

    return max(
        ranked_regions,
        key=lambda item: item[0],
    )[1]


@dataclass(frozen=True)
class GlobalOptimizationObjective:
    best_x: float | None
    best_value: float | None
    evaluation_count: int


def build_global_optimization_objective(
    state: ARRGOGlobalState,
) -> GlobalOptimizationObjective:
    return GlobalOptimizationObjective(
        best_x=state.best_x,
        best_value=state.best_value,
        evaluation_count=state.evaluation_count,
    )


def update_global_state(
    state: ARRGOGlobalState,
) -> ARRGOGlobalState:
    update_global_incumbent(state)

    return state


def create_root_region(
    config: ARRGOConfig,
) -> Region:
    return Region(
        id=0,
        left_x=config.lower_bound,
        right_x=config.upper_bound,
    )


def initialize_global_state(
    config: ARRGOConfig,
) -> ARRGOGlobalState:
    state = create_initial_global_state()

    root_region = create_root_region(config)

    state.region_hierarchy.add_region(
        root_region
    )

    return state


def create_child_regions(
    state: ARRGOGlobalState,
    parent_region: Region,
    split_location: float,
) -> tuple[Region, Region]:
    if not parent_region.left_x < split_location < parent_region.right_x:
        raise ValueError(
            "split_location must lie strictly inside the region."
        )

    if parent_region.children_ids:
        raise ValueError(
            "Region has already been split."
        )

    next_region_id = (
        max(
            (region.id for region in state.region_hierarchy.regions),
            default=-1,
        )
        + 1
    )

    left_child = Region(
        id=next_region_id,
        left_x=parent_region.left_x,
        right_x=split_location,
        parent_id=parent_region.id,
    )

    right_child = Region(
        id=next_region_id + 1,
        left_x=split_location,
        right_x=parent_region.right_x,
        parent_id=parent_region.id,
    )

    state.region_hierarchy.add_region(left_child)
    state.region_hierarchy.add_region(right_child)

    state.region_hierarchy.add_child_relationship(
        parent_id=parent_region.id,
        child_id=left_child.id,
    )

    state.region_hierarchy.add_child_relationship(
        parent_id=parent_region.id,
        child_id=right_child.id,
    )

    parent_region.state = RegionState.REFINED

    return left_child, right_child


def split_region(
    state: ARRGOGlobalState,
    region: Region,
    split_location: float,
) -> tuple[Region, Region]:
    if region.state != RegionState.ACTIVE:
        raise ValueError(
            "Only active regions can be split."
        )

    return create_child_regions(
        state=state,
        parent_region=region,
        split_location=split_location,
    )


def sample_region(
    state: ARRGOGlobalState,
    objective: ObjectiveFunction,
    location: float,
    coordinate_tolerance: float = 1e-12,
) -> Evaluation:
    if state.evaluation_history.contains_x(
        location,
        tolerance=coordinate_tolerance,
    ):
        raise ValueError(
            "Sampling location has already been evaluated."
        )

    evaluator = ObjectiveEvaluator(
        objective=objective,
        history=state.evaluation_history,
    )

    evaluation = evaluator.evaluate(location)

    update_global_incumbent(state)

    return evaluation


def calculate_global_potential(
    state: ARRGOGlobalState,
    lipschitz_constant: float,
) -> float:
    potentials: list[float] = []

    for region in state.region_hierarchy.regions:
        try:
            bounds = calculate_exact_regional_bounds(
                region=region,
                evaluations=state.evaluation_history.evaluations,
                lipschitz_constant=lipschitz_constant,
            )
        except ValueError:
            continue

        potentials.append(bounds.potential)

    if not potentials:
        raise ValueError(
            "No region contains an evaluation."
        )

    return max(potentials)


def calculate_global_gap(
    state: ARRGOGlobalState,
    lipschitz_constant: float,
) -> float:
    if state.best_value is None:
        raise ValueError(
            "Global gap requires at least one evaluation."
        )

    global_potential = calculate_global_potential(
        state=state,
        lipschitz_constant=lipschitz_constant,
    )

    return max(
        0.0,
        global_potential - state.best_value,
    )


def generate_initial_sampling_points(
    config: ARRGOConfig,
) -> tuple[float, ...]:
    left = config.lower_bound
    right = config.upper_bound
    midpoint = (left + right) / 2.0

    return (
        left,
        midpoint,
        right,
    )


def initialize_sampling(
    state: ARRGOGlobalState,
    objective: ObjectiveFunction,
    config: ARRGOConfig,
) -> tuple[Evaluation, ...]:
    points = generate_initial_sampling_points(config)

    evaluations: list[Evaluation] = []

    for point in points:
        if state.evaluation_history.contains_x(
            point,
            tolerance=config.coordinate_tolerance,
        ):
            continue

        evaluation = sample_region(
            state=state,
            objective=objective,
            location=point,
            coordinate_tolerance=config.coordinate_tolerance,
        )

        evaluations.append(evaluation)

    return tuple(evaluations)


def select_region_sampling_candidate(
    region: Region,
    state: ARRGOGlobalState,
    coordinate_tolerance: float = 1e-12,
) -> Candidate | None:
    candidates = generate_sampling_candidates(
        region=region,
        evaluations=state.evaluation_history.evaluations,
        coordinate_tolerance=coordinate_tolerance,
    )

    return select_sampling_candidate(
        candidates=candidates,
        evaluations=state.evaluation_history.evaluations,
        coordinate_tolerance=coordinate_tolerance,
    )


def generate_region_split_candidates(
    region: Region,
    config: ARRGOConfig,
) -> tuple[SplitCandidate, ...]:
    return build_split_candidates(
        region=region,
        contraction_factor=config.contraction_factor,
        coordinate_tolerance=config.coordinate_tolerance,
    )


def analyze_split_candidate(
    state: ARRGOGlobalState,
    region: Region,
    split_candidate: SplitCandidate,
) -> StructuralDifferenceProfile:
    if not split_candidate.contraction_valid:
        raise ValueError(
            "Split candidate does not satisfy the contraction condition."
        )

    split_location = split_candidate.split_location

    left_region = Region(
        id=-1,
        left_x=region.left_x,
        right_x=split_location,
        parent_id=region.id,
    )

    right_region = Region(
        id=-2,
        left_x=split_location,
        right_x=region.right_x,
        parent_id=region.id,
    )

    evaluations = state.evaluation_history.evaluations

    left_analysis = analyze_region(
        region=left_region,
        evaluations=evaluations,
        coordinate_tolerance=1e-12,
    )

    right_analysis = analyze_region(
        region=right_region,
        evaluations=evaluations,
        coordinate_tolerance=1e-12,
    )

    return build_split_profile(
        region=region,
        evaluations=evaluations,
        split_location=split_location,
        left_analysis=left_analysis,
        right_analysis=right_analysis,
        coordinate_tolerance=1e-12,
    )


def select_region_split_candidate(
    state: ARRGOGlobalState,
    region: Region,
    config: ARRGOConfig,
) -> SplitCandidate | None:
    candidates = generate_region_split_candidates(
        region=region,
        config=config,
    )

    if not candidates:
        return None

    profiles = tuple(
        analyze_split_candidate(
            state=state,
            region=region,
            split_candidate=candidate,
        )
        for candidate in candidates
    )

    return select_split_candidate(
        candidates=candidates,
        profiles=profiles,
        tolerance=config.uncertainty_tolerance,
    )


def select_region_refinement_action(
    state: ARRGOGlobalState,
    region: Region,
    config: ARRGOConfig,
) -> RefinementAction:
    analysis = analyze_region(
        region=region,
        evaluations=state.evaluation_history.evaluations,
        coordinate_tolerance=config.coordinate_tolerance,
    )

    sampling_candidates = generate_sampling_candidates(
        region=region,
        evaluations=state.evaluation_history.evaluations,
        coordinate_tolerance=config.coordinate_tolerance,
    )

    sampling_candidate = select_sampling_candidate(
        candidates=sampling_candidates,
        evaluations=state.evaluation_history.evaluations,
        coordinate_tolerance=config.coordinate_tolerance,
    )

    valid_sampling_candidates = (
        (sampling_candidate,)
        if sampling_candidate is not None
        else ()
    )

    split_candidate = select_region_split_candidate(
        state=state,
        region=region,
        config=config,
    )

    criteria = ResolutionCriteria(
        coverage_tolerance=config.coordinate_tolerance,
        behavior_tolerance=config.slope_tolerance,
        uncertainty_tolerance=config.uncertainty_tolerance,
        potential_tolerance=config.objective_tolerance,
    )

    return select_refinement_action(
        analysis=analysis,
        sampling_candidates=valid_sampling_candidates,
        split_candidate=split_candidate,
        criteria=criteria,
    )


def execute_refinement_action(
    state: ARRGOGlobalState,
    objective: ObjectiveFunction,
    region: Region,
    action: RefinementAction,
    config: ARRGOConfig,
) -> tuple[Evaluation | None, tuple[Region, Region] | None]:
    if action == RefinementAction.SAMPLE:
        candidate = select_region_sampling_candidate(
            region=region,
            state=state,
            coordinate_tolerance=config.coordinate_tolerance,
        )

        if candidate is None:
            raise ValueError(
                "No valid sampling candidate is available."
            )

        evaluation = sample_region(
            state=state,
            objective=objective,
            location=candidate.location,
            coordinate_tolerance=config.coordinate_tolerance,
        )

        return evaluation, None

    if action == RefinementAction.SPLIT:
        candidate = select_region_split_candidate(
            state=state,
            region=region,
            config=config,
        )

        if candidate is None:
            raise ValueError(
                "No valid split candidate is available."
            )

        children = split_region(
            state=state,
            region=region,
            split_location=candidate.split_location,
        )

        return None, children

    if action == RefinementAction.STABLE:
        region.state = RegionState.STABLE

        return None, None

    raise ValueError(
        f"Unsupported refinement action: {action}"
    )


@dataclass(frozen=True)
class RefinementIterationResult:
    region_id: int
    action: RefinementAction
    evaluation: Evaluation | None
    children: tuple[Region, Region] | None


def execute_refinement_iteration(
    state: ARRGOGlobalState,
    objective: ObjectiveFunction,
    region: Region,
    config: ARRGOConfig,
) -> RefinementIterationResult:
    action = select_region_refinement_action(
        state=state,
        region=region,
        config=config,
    )

    evaluation, children = execute_refinement_action(
        state=state,
        objective=objective,
        region=region,
        action=action,
        config=config,
    )

    update_global_state(state)

    return RefinementIterationResult(
        region_id=region.id,
        action=action,
        evaluation=evaluation,
        children=children,
    )


def execute_global_refinement_iteration(
    state: ARRGOGlobalState,
    objective: ObjectiveFunction,
    config: ARRGOConfig,
) -> RefinementIterationResult | None:
    region = select_global_region(
        regions=state.region_hierarchy.regions,
        evaluations=state.evaluation_history.evaluations,
        coordinate_tolerance=config.coordinate_tolerance,
    )

    if region is None:
        return None

    return execute_refinement_iteration(
        state=state,
        objective=objective,
        region=region,
        config=config,
    )


def check_global_termination(
    state: ARRGOGlobalState,
    config: ARRGOConfig,
    numerical_failure: bool = False,
) -> TerminationStatus:
    global_gap = None

    if config.mode.value == "certified":
        if config.lipschitz_constant is None:
            raise ValueError(
                "Certified mode requires a Lipschitz constant."
            )

        if state.best_value is not None:
            global_gap = calculate_global_gap(
                state=state,
                lipschitz_constant=config.lipschitz_constant,
            )

    has_valid_action = select_global_region(
        regions=state.region_hierarchy.regions,
        evaluations=state.evaluation_history.evaluations,
        coordinate_tolerance=config.coordinate_tolerance,
    ) is not None

    return determine_termination(
        evaluation_count=state.evaluation_count,
        global_gap=global_gap,
        has_valid_action=has_valid_action,
        numerical_failure=numerical_failure,
        config=config,
    )


@dataclass(frozen=True)
class ARRGOResult:
    best_x: float | None
    best_value: float | None
    evaluation_count: int
    termination_reason: object | None
    global_gap: float | None
    state: ARRGOGlobalState


def run_arrgo(
    objective: ObjectiveFunction,
    config: ARRGOConfig,
) -> ARRGOResult:
    state = initialize_global_state(config)

    initialize_sampling(
        state=state,
        objective=objective,
        config=config,
    )

    update_global_state(state)

    termination_status = check_global_termination(
        state=state,
        config=config,
    )

    while not termination_status.should_terminate:
        iteration_result = execute_global_refinement_iteration(
            state=state,
            objective=objective,
            config=config,
        )

        if iteration_result is None:
            break

        termination_status = check_global_termination(
            state=state,
            config=config,
        )

    global_gap = None

    if (
        config.mode.value == "certified"
        and config.lipschitz_constant is not None
        and state.best_value is not None
    ):
        global_gap = calculate_global_gap(
            state=state,
            lipschitz_constant=config.lipschitz_constant,
        )

    return ARRGOResult(
        best_x=state.best_x,
        best_value=state.best_value,
        evaluation_count=state.evaluation_count,
        termination_reason=termination_status.reason,
        global_gap=global_gap,
        state=state,
    )


def optimize(
    objective: Callable[[float], float],
    config: ARRGOConfig,
) -> ARRGOResult:
    return run_arrgo(
        objective=CallableObjective(objective),
        config=config,
    )