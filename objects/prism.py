vertices = [
    [0, 1, 0],     # Top (0)
    [-1, -1, -1],  # Base front left (1)
    [1, -1, -1],   # Base front right (2)
    [1, -1, 1],    # Base back right (3)
    [-1, -1, 1]    # Base back left (4)
]

faces = [
    [0, 1, 2],     # Front face
    [0, 2, 3],     # Right face
    [0, 3, 4],     # Back face
    [0, 4, 1],     # Left face
    [1, 2, 3, 4]   # Bottom face
]

texture_coords = [
    [0.5, 1.0], [0.0, 0.0], [1.0, 0.0],  # For triangular faces
    [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]  # For square base
]