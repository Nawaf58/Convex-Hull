import re
from math import atan2
import matplotlib.pyplot as plt
import time

# Seconds between frames
PAUSE_TIME = 0.0001

# =========================
# 1. Read points from file
# =========================

#O(n) : Where n is the size of input file.
def read_points_from_file(filename):
    points = []
    with open(filename, 'r') as f:
        text = f.read()
        matches = re.findall(r'\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\)', text)
        for x_str, y_str in matches:
            points.append((float(x_str), float(y_str)))
    return points

# =========================
# 2. Geometry helpers
# =========================

# Give +ve if it is counterclockwise and -ve if it is clockwise and 0 if it is collinear.
# Also helps decide which triangle will be bigger in Quick Hull.
# O(1).
def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

# To help us find which point is the farthest os nearest.
# O(1)
def distance(a, b):
    return (a[0] - b[0])**2 + (a[1] - b[1])**2

# =========================
# 3. Step recording + playback
# =========================

# This method help us record a step we try so we can run it after.
def record_step(steps_list, hull_points=None, edges=None, highlight_points=None, title=""):
    steps_list.append({
        "hull": list(hull_points) if hull_points else None,
        "edges": list(edges) if edges else None,
        "highlight": list(highlight_points) if highlight_points else None,
        "title": title
    })

# This method is for playing all the steps in one window to visualize the irritation that happened.
def play_steps(points, steps_list, window_title):
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle(window_title)

    xs_all = [p[0] for p in points]
    ys_all = [p[1] for p in points]

    for step_idx, step in enumerate(steps_list, start=1):
        ax.clear()
        # All points
        ax.scatter(xs_all, ys_all, s=10, label="Points")

        hull = step["hull"]
        edges = step["edges"]
        highlights = step["highlight"]
        title = step["title"]

        # Draw hull polygon if exists
        if hull and len(hull) > 1:
            hx = [p[0] for p in hull]
            hy = [p[1] for p in hull]
            ax.plot(hx, hy, linewidth=2, label="Current hull")

        # Draw edges
        if edges:
            for (a, b) in edges:
                ax.plot([a[0], b[0]], [a[1], b[1]], linestyle='--', color='grey')

        # Highlight important points
        if highlights:
            hx = [p[0] for p in highlights]
            hy = [p[1] for p in highlights]
            ax.scatter(hx, hy, s=50, marker='X', color='red', label='Highlighted')

        ax.set_title(f"{title} — Step {step_idx}/{len(steps_list)}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_aspect('equal', adjustable='box')
        ax.legend(loc='upper left', bbox_to_anchor=(1.05,1), borderaxespad=0)

        if step_idx != len(steps_list):
            plt.pause(PAUSE_TIME)

    plt.close(fig)

    # === Final frame with red hull points ===
    fig, ax = plt.subplots(figsize=(10, 6))

    fig.suptitle(window_title + " — FINAL RESULT")

    # Normal points
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.scatter(xs, ys, s=10, color="black")

    # Red hull points
    hx = [p[0] for p in steps_list[-1]["hull"]]
    hy = [p[1] for p in steps_list[-1]["hull"]]
    ax.scatter(hx, hy, s=60, color="red", label="Final hull points")

    # Draw final hull polygon
    ax.plot(hx + [hx[0]], hy + [hy[0]], color="red", linewidth=2)

    ax.set_aspect('equal')
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))  # ❗ legend outside

    # Keep final frame open until user closes window
    plt.show()

# ==================================
# 4. Graham Scan Convex Hull (O(n log n))
# ==================================
def convex_hull_graham(points, steps=None):
    points = list(set(points))  # Remove duplicates, O(n) : Where n is the number of points
    if len(points) <= 1:
        return points

    # Pivot: lowest y, then lowest x
    p0 = min(points, key=lambda p: (p[1], p[0])) # O(n)

    def polar_angle(p):
        return atan2(p[1] - p0[1], p[0] - p0[0])

    # Sort by angle, then distance
    sorted_points = sorted(points, key=lambda p: (polar_angle(p), distance(p0, p))) #sorting complexity O(n log n)

    # Initial step: show pivot
    if steps is not None:
        record_step(steps, hull_points=None, highlight_points=[p0],
                    title="Graham Scan: pivot p0")

    hull = []
    for p in sorted_points: #O(2n) = O(n)
        # Pop while last turn is not counter-clockwise
        # All pops across the loop <=n
        while len(hull) >= 2 and cross(hull[-2], hull[-1], p) <= 0:
            hull.pop()
            if steps is not None:
                record_step(steps, hull_points=hull,
                            highlight_points=[p],
                            title="Graham Scan: popping non-CCW point")

        hull.append(p)
        if steps is not None:
            record_step(steps, hull_points=hull,
                        highlight_points=[p],
                        title="Graham Scan: adding point to hull")

    # Final hull
    if steps is not None:
        record_step(steps, hull_points=hull,
                    title="Graham Scan: final hull")

    return hull

# ==================================
# 5. Brute Force Convex Hull (O(n^3))
# ==================================
def convex_hull_bruteforce(points, steps=None):
    n = len(points)
    if n <= 1:
        return points

    points = list(points)
    edges = set()

    for i in range(n): # O(n)
        for j in range(i + 1, n): # O(n)
            p = points[i]
            q = points[j]
            pos = neg = False
            for k in range(n): # O(n)
                if k == i or k == j:
                    continue
                r = points[k]
                c = cross(p, q, r)
                if c > 0:
                    pos = True
                elif c < 0:
                    neg = True
                if pos and neg:
                    break  # not a hull edge

            # If all points are on one side or collinear -> hull edge
            if not (pos and neg):
                edges.add((p, q))

    # Unique hull vertices
    hull_points = list({p for edge in edges for p in edge}) # O(e) e < n

    # Sort around centroid
    cx = sum(p[0] for p in hull_points) / len(hull_points) # O(h) h <= n
    cy = sum(p[1] for p in hull_points) / len(hull_points) # O(h) h <= n
    hull_points.sort(key=lambda p: atan2(p[1] - cy, p[0] - cx)) # O(h log h)

    if steps is not None:
        record_step(steps, hull_points=hull_points,
                    title="Brute Force: final hull")

    return hull_points

# ==================================
# 6. QuickHull (Divide & Conquer) worst case O(n^2)
# Average case O(n log n)
# ==================================
def quickhull_recursive(points, a, b, side, hull_edges, all_points, steps, level=0):
    """
    Recursive helper for QuickHull.
    - points: candidate points on this side
    - a, b: current segment
    - side: +1 or -1
    - level: recursion depth (for title)
    """
    # Show current segment being explored
    edges_with_current = set(hull_edges)
    edges_with_current.add((a, b))
    if steps is not None:
        record_step(steps, hull_points=None,
                    edges=edges_with_current,
                    highlight_points=[a, b],
                    title=f"QuickHull (level {level}): exploring segment")

    idx = -1
    max_dist = 0

    for i, p in enumerate(points): # O(n)
        c = cross(a, b, p)
        if side * c > 0 and abs(c) > max_dist:
            max_dist = abs(c)
            idx = i

    if idx == -1:
        # No point is outside: (a, b) is hull edge
        hull_edges.add((a, b))
        if steps is not None:
            record_step(steps, hull_points=None,
                        edges=hull_edges,
                        highlight_points=[a, b],
                        title=f"QuickHull (level {level}): confirmed hull edge")
        return

    p = points[idx]
    if steps is not None:
        record_step(steps, hull_points=None,
                    edges=edges_with_current,
                    highlight_points=[a, b, p],
                    title=f"QuickHull (level {level}): farthest point chosen")

    # Points on left of (a, p)
    subset1 = [q for q in points if side * cross(a, p, q) > 0]
    # Points on left of (p, b)
    subset2 = [q for q in points if side * cross(p, b, q) > 0]

    quickhull_recursive(subset1, a, p, side, hull_edges, all_points, steps, level + 1) # O(n)
    quickhull_recursive(subset2, p, b, side, hull_edges, all_points, steps, level + 1) # O(n)


def convex_hull_quickhull(points, steps=None):
    points = list(set(points)) # O(n)

    n = len(points)
    if n <= 1:
        return points

    # Extreme points by x-coordinate
    # A function that returns the x-coordinate of a point
    a = min(points, key=lambda p: p[0]) # O(n)
    b = max(points, key=lambda p: p[0]) # O(n)

    if steps is not None:
        record_step(steps, hull_points=None,
                    highlight_points=[a, b],
                    title="QuickHull: initial extreme points")

    hull_edges = set()
    quickhull_recursive(points, a, b, +1, hull_edges, points, steps, level=1)
    quickhull_recursive(points, a, b, -1, hull_edges, points, steps, level=1)

    hull_points = list({p for edge in hull_edges for p in edge}) # O(h)

    # Sort around centroid
    cx = sum(p[0] for p in hull_points) / len(hull_points)
    cy = sum(p[1] for p in hull_points) / len(hull_points)
    hull_points.sort(key=lambda p: atan2(p[1] - cy, p[0] - cx)) # O(h log h)

    if steps is not None:
        record_step(steps, hull_points=hull_points,
                    title="QuickHull: final hull")

    return hull_points

# =========================
# 7. Main
# =========================
def main():
    filename = "datapoints1.txt"
    points = read_points_from_file(filename)
    print("Number of input points:", len(points))

    # ---- choose algorithm ----
    print("\nChoose convex hull algorithm:")
    print("  1) Brute Force")
    print("  2) Graham Scan")
    print("  3) QuickHull")
    print("  4) Run ALL (one after another)")

    choice = input("Enter your choice (1/2/3/4): ").strip()

    if choice == "1":
        # ---- Brute Force only ----
        brute_steps = []
        print("\nRunning Brute Force...")
        start = time.time()
        hull_brute = convex_hull_bruteforce(points, steps=brute_steps)
        end = time.time()
        print(f"Brute Force Time: {end - start:.30f} seconds")
        print("\nFinal Hull Coordinates:")
        for point in hull_brute:
            print(point)

        print("Brute Force hull has", len(hull_brute), "points")
        play_steps(points, brute_steps, "Brute Force Convex Hull")

    elif choice == "2":
        # ---- Graham Scan only ----
        graham_steps = []
        print("\nRunning Graham Scan...")
        start = time.time()
        hull_graham = convex_hull_graham(points, steps=graham_steps)
        end = time.time()
        print(f"Graham Scan Time: {end - start:.30f} seconds")
        print("\nFinal Hull Coordinates:")
        for point in hull_graham:
            print(point)

        print("Graham Scan hull has", len(hull_graham), "points")
        play_steps(points, graham_steps, "Graham Scan Convex Hull")

    elif choice == "3":
        # ---- QuickHull only ----
        quick_steps = []
        print("\nRunning QuickHull...")
        start = time.time()
        hull_quick = convex_hull_quickhull(points, steps=quick_steps)
        end = time.time()
        print(f"QuickHull Time: {end - start:.30f} seconds")
        print("\nFinal Hull Coordinates:")
        for point in hull_quick:
            print(point)

        print("QuickHull hull has", len(hull_quick), "points")
        play_steps(points, quick_steps, "QuickHull Convex Hull")

    elif choice == "4":
        # ---- Run all three ----
        # Brute Force
        brute_steps = []
        print("\nRunning Brute Force...")
        start = time.time()
        hull_brute = convex_hull_bruteforce(points, steps=brute_steps)
        end = time.time()
        print(f"Brute Force Time: {end - start:.30f} seconds")
        print("\nFinal Hull Coordinates:")
        for point in hull_brute:
            print(point)

        print("Brute Force hull has", len(hull_brute), "points")
        play_steps(points, brute_steps, "Brute Force Convex Hull")

        # Graham Scan
        graham_steps = []
        print("\nRunning Graham Scan...")
        start = time.time()
        hull_graham = convex_hull_graham(points, steps=graham_steps)
        end = time.time()
        print(f"Graham Scan Time: {end - start:.30f} seconds")
        print("\nFinal Hull Coordinates:")
        for point in hull_graham:
            print(point)

        print("Graham Scan hull has", len(hull_graham), "points")
        play_steps(points, graham_steps, "Graham Scan Convex Hull")

        # QuickHull
        quick_steps = []
        print("\nRunning QuickHull...")
        start = time.time()
        hull_quick = convex_hull_quickhull(points, steps=quick_steps)
        end = time.time()
        print(f"QuickHull Time: {end - start:.30f} seconds")
        print("\nFinal Hull Coordinates:")
        for point in hull_quick:
            print(point)

        print("QuickHull hull has", len(hull_quick), "points")
        play_steps(points, quick_steps, "QuickHull Convex Hull")

    else:
        print("\nInvalid choice. Please run the program again and choose 1, 2, 3, or 4.")
        return

    print("\nDone. Close the plot window(s) to exit.")


if __name__ == "__main__":
    main()
