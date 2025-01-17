vertices = [
    [0, 1, 0],     # Top point
    [1, 0, 1],     # Upper front right
    [-1, 0, 1],    # Upper front left
    [-1, 0, -1],   # Upper back left
    [1, 0, -1],    # Upper back right
    [0, -1, 0]     # Bottom point
]

faces = [
    [0, 1, 2],     # Top front
    [0, 2, 3],     # Top left
    [0, 3, 4],     # Top back
    [0, 4, 1],     # Top right
    [5, 2, 1],     # Bottom front
    [5, 3, 2],     # Bottom left
    [5, 4, 3],     # Bottom back
    [5, 1, 4]      # Bottom right
]

texture_coords = [
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],  # For all triangular faces
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],
    [0.5, 0.0], [1.0, 1.0], [0.0, 1.0],
    [0.5, 0.0], [1.0, 1.0], [0.0, 1.0],
    [0.5, 0.0], [1.0, 1.0], [0.0, 1.0],
    [0.5, 0.0], [1.0, 1.0], [0.0, 1.0]
]
