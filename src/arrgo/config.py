from dataclasses import dataclass
from enum import Enum


class ARRGOExecutionMode(Enum):
    EMPIRICAL = "empirical"
    CERTIFIED = "certified"


class TerminationReason(Enum):
    CERTIFIED_TOLERANCE = "certified_tolerance"
    BUDGET_EXHAUSTED = "budget_exhausted"
    NUMERICAL_LIMIT = "numerical_limit"
    NO_VALID_ACTION = "no_valid_action"
    CONFIGURATION_ERROR = "configuration_error"


@dataclass(frozen=True)
class NumericalTolerances:
    coordinate: float = 1e-12
    objective: float = 1e-12
    slope: float = 1e-12
    uncertainty: float = 1e-12


@dataclass(frozen=True)
class ARRGOConfig:
    lower_bound: float
    upper_bound: float
    max_evaluations: int

    contraction_factor: float = 0.5

    coordinate_tolerance: float = 1e-12
    objective_tolerance: float = 1e-12
    slope_tolerance: float = 1e-12
    uncertainty_tolerance: float = 1e-12

    mode: ARRGOExecutionMode = ARRGOExecutionMode.EMPIRICAL

    lipschitz_constant: float | None = None
    epsilon: float | None = None

    @property
    def domain(self) -> tuple[float, float]:
        return self.lower_bound, self.upper_bound

    @property
    def tolerances(self) -> NumericalTolerances:
        return NumericalTolerances(
            coordinate=self.coordinate_tolerance,
            objective=self.objective_tolerance,
            slope=self.slope_tolerance,
            uncertainty=self.uncertainty_tolerance,
        )

    def __post_init__(self) -> None:
        if self.lower_bound >= self.upper_bound:
            raise ValueError("lower_bound must be smaller than upper_bound.")

        if self.max_evaluations <= 0:
            raise ValueError("max_evaluations must be positive.")

        if not 0.0 < self.contraction_factor < 1.0:
            raise ValueError(
                "contraction_factor must be strictly between 0 and 1."
            )

        if self.mode == ARRGOExecutionMode.CERTIFIED:
            if self.lipschitz_constant is None:
                raise ValueError(
                    "Certified mode requires a Lipschitz constant."
                )

            if self.lipschitz_constant <= 0.0:
                raise ValueError(
                    "lipschitz_constant must be positive."
                )

            if self.epsilon is None:
                raise ValueError(
                    "Certified mode requires an epsilon tolerance."
                )

            if self.epsilon <= 0.0:
                raise ValueError(
                    "epsilon must be positive."
                )