import numpy as np
from PIL import Image
from utils.geometry import Point, Segment

COLOR_THRESHOLD = 50  # Max allowed color difference for a cluster


def diff_colors(c1, c2):
    """
    Compute difference between two RGB colors.
    Returns sum of absolute differences across R, G, B (0-765 max)
    """
    arr1 = np.array(c1, dtype=int)
    arr2 = np.array(c2, dtype=int)
    return np.sum(np.abs(arr1 - arr2))


def diff_points(image: Image.Image, p1: Point, p2: Point):
    """
    Compare colors at two points in an image.
    """
    c1 = image.getpixel((int(p1.x), int(p1.y)))
    c2 = image.getpixel((int(p2.x), int(p2.y)))
    return diff_colors(c1, c2)


def get_color_clusters(image: Image.Image, start: Point, direction: Point):
    """
    Scan along a vector and split into clusters of similar colors.
    Returns a list of Segment objects.
    """
    clusters = []

    last_point = start
    next_point = start + direction
    cluster_start = last_point

    width, height = image.size

    def in_bounds(p: Point):
        return 0 <= p.x < width and 0 <= p.y < height

    while in_bounds(next_point):
        delta = diff_points(image, last_point, next_point)

        if delta > COLOR_THRESHOLD:
            clusters.append(Segment(cluster_start, last_point))
            cluster_start = next_point

        last_point = next_point
        next_point = last_point + direction

    # Add the final cluster
    clusters.append(Segment(cluster_start, last_point))
    return clusters
