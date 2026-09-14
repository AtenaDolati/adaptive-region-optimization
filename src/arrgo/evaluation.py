from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Evaluation:
    x: float
    value: float
    id: int


class EvaluationHistory:
    def __init__(self) -> None:
        self._evaluations: list[Evaluation] = []

    @property
    def evaluations(self) -> tuple[Evaluation, ...]:
        return tuple(self._evaluations)

    @property
    def count(self) -> int:
        return len(self._evaluations)

    def add(self, evaluation: Evaluation) -> None:
        self._evaluations.append(evaluation)

    def extend(self, evaluations: Iterable[Evaluation]) -> None:
        for evaluation in evaluations:
            self.add(evaluation)

    def contains_x(
        self,
        x: float,
        tolerance: float,
    ) -> bool:
        return any(
            abs(evaluation.x - x) <= tolerance
            for evaluation in self._evaluations
        )

    def get_by_x(
        self,
        x: float,
        tolerance: float,
    ) -> Evaluation | None:
        for evaluation in self._evaluations:
            if abs(evaluation.x - x) <= tolerance:
                return evaluation

        return None

    def best(self) -> Evaluation | None:
        if not self._evaluations:
            return None

        return max(
            self._evaluations,
            key=lambda evaluation: evaluation.value,
        )