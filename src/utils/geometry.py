from typing import Tuple
import math


class Point:
    """Simple 2D point."""
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def as_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def distance_to(self, other: 'Point') -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class Segment:
    """Line segment between two points."""
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def length(self) -> float:
        return self.start.distance_to(self.end)

    def midpoint(self) -> Point:
        return Point(
            (self.start.x + self.end.x) / 2,
            (self.start.y + self.end.y) / 2
        )

    def __repr__(self):
        return f"Segment({self.start}, {self.end})"


class Quadrilateral:
    """Quadrilateral defined by 4 points in order (p1, p2, p3, p4)."""
    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

    def as_tuple_list(self):
        return [self.p1.as_tuple(), self.p2.as_tuple(),
                self.p3.as_tuple(), self.p4.as_tuple()]

    def centroid(self) -> Point:
        cx = (self.p1.x + self.p2.x + self.p3.x + self.p4.x) / 4
        cy = (self.p1.y + self.p2.y + self.p3.y + self.p4.y) / 4
        return Point(cx, cy)

    def __repr__(self):
        return f"Quadrilateral({self.p1}, {self.p2}, {self.p3}, {self.p4})"
