vertices = [
    [0, 1, 0],    # Top vertex
    [1, 0, 0],    # Right vertex
    [0, 0, 1],    # Front vertex
    [-1, 0, 0],   # Left vertex
    [0, 0, -1],   # Back vertex
    [0, -1, 0]    # Bottom vertex
]

faces = [
    [0, 1, 2],    # Top front right
    [0, 2, 3],    # Top front left
    [0, 3, 4],    # Top back left
    [0, 4, 1],    # Top back right
    [5, 2, 1],    # Bottom front right
    [5, 3, 2],    # Bottom front left
    [5, 4, 3],    # Bottom back left
    [5, 1, 4]     # Bottom back right
]

texture_coords = [
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],  # For all triangular faces
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0]
]
