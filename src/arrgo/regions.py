from dataclasses import dataclass, field
from enum import Enum


class RegionState(Enum):
    ACTIVE = "active"
    STABLE = "stable"
    REFINED = "refined"


@dataclass
class Region:
    id: int
    left_x: float
    right_x: float
    parent_id: int | None = None
    children_ids: list[int] = field(default_factory=list)
    state: RegionState = RegionState.ACTIVE

    @property
    def width(self) -> float:
        return self.right_x - self.left_x

    @property
    def midpoint(self) -> float:
        return (self.left_x + self.right_x) / 2.0

    def contains(
        self,
        x: float,
        tolerance: float = 0.0,
    ) -> bool:
        return (
            self.left_x - tolerance
            <= x
            <= self.right_x + tolerance
        )

    def add_child(self, child_id: int) -> None:
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)


class RegionHierarchy:
    def __init__(self) -> None:
        self._regions: dict[int, Region] = {}

    @property
    def regions(self) -> tuple[Region, ...]:
        return tuple(self._regions.values())

    def add_region(self, region: Region) -> None:
        if region.id in self._regions:
            raise ValueError(
                f"Region with id {region.id} already exists."
            )

        self._regions[region.id] = region

    def get_region(self, region_id: int) -> Region:
        try:
            return self._regions[region_id]
        except KeyError as exc:
            raise KeyError(
                f"Region with id {region_id} does not exist."
            ) from exc

    def contains(self, region_id: int) -> bool:
        return region_id in self._regions

    def add_child_relationship(
        self,
        parent_id: int,
        child_id: int,
    ) -> None:
        parent = self.get_region(parent_id)
        child = self.get_region(child_id)

        if child.parent_id != parent_id:
            child.parent_id = parent_id

        parent.add_child(child_id)

    def roots(self) -> tuple[Region, ...]:
        return tuple(
            region
            for region in self._regions.values()
            if region.parent_id is None
        )