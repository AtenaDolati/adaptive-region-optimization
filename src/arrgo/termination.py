from dataclasses import dataclass

from .config import (
    ARRGOConfig,
    ARRGOExecutionMode,
    TerminationReason,
)


@dataclass(frozen=True)
class TerminationStatus:
    should_terminate: bool
    reason: TerminationReason | None = None


def check_budget_termination(
    evaluation_count: int,
    config: ARRGOConfig,
) -> TerminationStatus:
    if evaluation_count >= config.max_evaluations:
        return TerminationStatus(
            should_terminate=True,
            reason=TerminationReason.BUDGET_EXHAUSTED,
        )

    return TerminationStatus(
        should_terminate=False,
    )


def check_certified_termination(
    global_gap: float | None,
    config: ARRGOConfig,
) -> TerminationStatus:
    if config.mode != ARRGOExecutionMode.CERTIFIED:
        return TerminationStatus(
            should_terminate=False,
        )

    if global_gap is None:
        return TerminationStatus(
            should_terminate=False,
        )

    if config.epsilon is not None:
        if global_gap <= config.epsilon:
            return TerminationStatus(
                should_terminate=True,
                reason=TerminationReason.CERTIFIED_TOLERANCE,
            )

    return TerminationStatus(
        should_terminate=False,
    )


def check_numerical_termination(
    numerical_failure: bool,
) -> TerminationStatus:
    if numerical_failure:
        return TerminationStatus(
            should_terminate=True,
            reason=TerminationReason.NUMERICAL_LIMIT,
        )

    return TerminationStatus(
        should_terminate=False,
    )


def check_no_action_termination(
    has_valid_action: bool,
) -> TerminationStatus:
    if not has_valid_action:
        return TerminationStatus(
            should_terminate=True,
            reason=TerminationReason.NO_VALID_ACTION,
        )

    return TerminationStatus(
        should_terminate=False,
    )


def determine_termination(
    evaluation_count: int,
    global_gap: float | None,
    has_valid_action: bool,
    numerical_failure: bool,
    config: ARRGOConfig,
) -> TerminationStatus:
    numerical_status = check_numerical_termination(
        numerical_failure
    )

    if numerical_status.should_terminate:
        return numerical_status

    budget_status = check_budget_termination(
        evaluation_count=evaluation_count,
        config=config,
    )

    if budget_status.should_terminate:
        return budget_status

    certified_status = check_certified_termination(
        global_gap=global_gap,
        config=config,
    )

    if certified_status.should_terminate:
        return certified_status

    action_status = check_no_action_termination(
        has_valid_action=has_valid_action
    )

    if action_status.should_terminate:
        return action_status

    return TerminationStatus(
        should_terminate=False,
    )