# Convex Hull: Implementation & Performance Study

A Python-based computational geometry tool that computes and visually animates the 2D Convex Hull using three distinct algorithms: **Brute Force**, **Graham Scan**, and **QuickHull**.

---

## Features

* **Step-by-Step Visualization:** Uses Matplotlib to record and animate intermediate steps (segment exploration, pivots, hull updates, and backtrack pops).
* **Multiple Execution Modes:** Run algorithms individually or sequentially to compare performance.
* **Performance Benchmarking:** Records and displays execution times for each algorithm.
* **Input Parser:** Extracts 2D coordinate points from text files using regex.

---

## Algorithms & Complexity

| Algorithm | Theoretical Complexity | Measured Runtime | Strategy |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(n^3)$ | 0.007100 s | Checks orientation for every point pair across all remaining points. |
| **Graham Scan** | $O(n \log n)$ | 0.000997 s | Polar angle sorting relative to lowest pivot + stack-based counter-clockwise scan. |
| **QuickHull** | Best/Avg: $O(n \log n)$<br>Worst: $O(n^2)$ | 0.000995 s | Divide-and-conquer strategy finding extreme points and recursive farthest distances. |

---

## Abstract Data Types (ADTs)

* **List:** Stores point sets, dynamic hull construction, step animation sequences, and stack operations (`append`, `pop`).
* **Set:** Ensures uniqueness for detected hull edges in Brute Force and QuickHull.
* **Dictionary:** Structures intermediate frame data (current hull, active edges, highlights, step title) for the visualizer.
* **Tuple:** Encapsulates `(x, y)` coordinate pairs for indexing.

---

## Project Structure

```text
├── main.py              # Core algorithms, file parsing, and Matplotlib visualizer
├── datapoints1.txt      # Input 2D coordinate dataset
└── README.md
```

---

## Getting Started

### Prerequisites

* Python 3.8+
* Matplotlib

```bash
pip install matplotlib
```

### Input File Format

Coordinates in `datapoints1.txt` should follow the format `(x, y)`:

```text
(110.2, 553.3)
(165.7, 111.2)
(930.2, 111.9)
(955.6, 145.3)
```

### Running the Program

Run the main script:

```bash
python main.py
```

Select the desired option from the interactive terminal menu:
* `1`: Run **Brute Force**
* `2`: Run **Graham Scan**
* `3`: Run **QuickHull**
* `4`: Run **ALL** algorithms sequentially

---

## Authors

* **Nawaf Albeshr**
* **Faisal Aljammaz**
