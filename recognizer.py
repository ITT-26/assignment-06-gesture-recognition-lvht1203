import math
from dataclasses import dataclass

# Parameters defined by the original $1 Recognizer paper
NUM_POINTS = 64
SQUARE_SIZE = 250.0
ORIGIN = (0.0, 0.0)

DIAGONAL = math.sqrt(SQUARE_SIZE**2 + SQUARE_SIZE**2)
HALF_DIAGONAL = 0.5 * DIAGONAL

# Rotation search interval for Golden Section Search
ANGLE_RANGE = math.radians(45.0)
ANGLE_PRECISION = math.radians(2.0)

PHI = 0.5 * (-1.0 + math.sqrt(5.0))


@dataclass
class Point:
    # Rotation search interval for Golden Section Search
    x: float
    y: float


@dataclass
class Rectangle:
    x: float
    y: float
    width: float
    height: float

class Unistroke:
    """
    Stores a normalized gesture template.

    Each template is preprocessed using the same pipeline:
    resample -> rotate -> scale -> translate.
    """
    def __init__(self, name, points):
        self.name = name

        points = resample(points, NUM_POINTS)
        radians = indicative_angle(points)
        points = rotate_by(points, -radians)
        points = scale_to_square(points, SQUARE_SIZE)
        points = translate_to_origin(points, ORIGIN)

        self.points = points


class Result:
    def __init__(self, name, score):
        self.name = name
        self.score = score


class DollarRecognizer:
    """
    Implementation of the $1 Unistroke Recognizer.

    Recognition is performed by comparing an input gesture
    to all stored templates and selecting the one with the
    smallest path distance.
    """
    def __init__(self):
        self.unistrokes = []

    def add_template(self, name, points):
        self.unistrokes.append(Unistroke(name, points))

    def recognize(self, points):
        # Ignore gestures that contain too few points
        if len(points) < 2:
            return None, 0.0

        # Ignore gestures that contain too few points   
        points = resample(points, NUM_POINTS)
        radians = indicative_angle(points)
        points = rotate_by(points, -radians)
        points = scale_to_square(points, SQUARE_SIZE)
        points = translate_to_origin(points, ORIGIN)

        best_distance = float("inf")
        best_name = "No match"

        # Compare the input gesture with all stored templates
        # and keep the one with the smallest distance
        for template in self.unistrokes:
            distance = distance_at_best_angle(points, template, -ANGLE_RANGE, ANGLE_RANGE, ANGLE_PRECISION)
            if distance < best_distance:
                best_distance = distance
                best_name = template.name
        
        # Convert the distance into a confidence score between 0 and 1
        score = 1.0 - (best_distance / HALF_DIAGONAL)
        return best_name, score


def resample(points, n):
    """Resample the gesture to a fixed number of evenly spaced points."""
    points = [Point(p.x, p.y) for p in points]
    interval = path_length(points) / (n - 1)
    D = 0.0
    new_points = [points[0]]
    i = 1
    while i < len(points):
        d = distance(points[i - 1], points[i])
        if d == 0:
            i += 1
            continue
        if D + d >= interval:
            qx = points[i - 1].x + ((interval - D) / d) * (points[i].x - points[i - 1].x)
            qy = points[i - 1].y + ((interval - D) / d) * (points[i].y - points[i - 1].y)
            
            q = Point(qx, qy)
            new_points.append(q)
            points.insert(i, q)

            D = 0.0
            i += 1
        else:
            D += d
            i += 1

    while len(new_points) < n:
        new_points.append(points[-1])

    return new_points[:n]


def indicative_angle(points):
    """Compute the angle between the centroid and the first point."""
    c = centroid(points)
    return math.atan2(c.y - points[0].y, c.x - points[0].x)


def rotate_by(points, radians):
    """Rotate all points around the gesture centroid."""
    c = centroid(points)
    cos_val = math.cos(radians)
    sin_val = math.sin(radians)
    new_points = []
    for p in points:
        qx = (p.x - c.x) * cos_val - (p.y - c.y) * sin_val + c.x
        qy = (p.x - c.x) * sin_val + (p.y - c.y) * cos_val + c.y
        new_points.append(Point(qx, qy))
    return new_points


def scale_to_square(points, size):
    """Rotate all points around the gesture centroid."""
    box = bounding_box(points)
    width = max(box.width, 1e-6)
    height = max(box.height, 1e-6)
    return [
        Point((p.x - box.x) * size / width,(p.y - box.y) * size / height,)
        for p in points
    ]


def translate_to_origin(points, origin):
    """Move the gesture centroid to the origin."""
    c = centroid(points)
    new_points = []
    for p in points:
        qx = p.x + origin[0] - c.x
        qy = p.y + origin[1] - c.y
        new_points.append(Point(qx, qy))
    return new_points


def distance_at_best_angle(points, template, a, b, threshold):
    """Find the minimum distance using Golden Section Search."""
    x1 = PHI * a + (1.0 - PHI) * b
    f1 = distance_at_angle(points, template, x1)

    x2 = (1.0 - PHI) * a + PHI * b
    f2 = distance_at_angle(points, template, x2)

    while abs(b - a) > threshold:
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1

            x1 = PHI * a + (1.0 - PHI) * b
            f1 = distance_at_angle(points, template, x1)
        else:
            a = x1
            x1 = x2
            f1 = f2

            x2 = (1.0 - PHI) * a + PHI * b
            f2 = distance_at_angle(points, template, x2)

    return min(f1, f2)


def distance_at_angle(points, template, radians):
    new_points = rotate_by(points, radians)
    return path_distance(new_points, template.points)


def centroid(points):
    x = sum(p.x for p in points) / len(points)
    y = sum(p.y for p in points) / len(points)

    return Point(x, y)


def bounding_box(points):
    min_x = min(p.x for p in points)
    max_x = max(p.x for p in points)

    min_y = min(p.y for p in points)
    max_y = max(p.y for p in points)

    return Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)


def path_distance(points1, points2):
    """Compute the average distance between corresponding points."""
    d = 0.0
    for p1, p2 in zip(points1, points2):
        d += distance(p1, p2)
    return d / len(points1)

def path_length(points):
    d = 0.0
    for i in range(1, len(points)):
        d += distance(points[i - 1], points[i])
    return d


def distance(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return math.sqrt(dx * dx + dy * dy)