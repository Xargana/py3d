# cube.py

# Define the vertices for the cube
vertices = [
    [-1, -1, -1],  # Bottom-back-left
    [1, -1, -1],   # Bottom-back-right
    [1, -1, 1],    # Bottom-front-right
    [-1, -1, 1],   # Bottom-front-left
    [-1, 1, -1],   # Top-back-left
    [1, 1, -1],    # Top-back-right
    [1, 1, 1],     # Top-front-right
    [-1, 1, 1]     # Top-front-left
]

# Define the faces of the cube with corrected vertex orders
faces = [
    [0, 3, 2, 1],  # Bottom face (corrected winding)
    [4, 5, 6, 7],  # Top face
    [1, 0, 4, 5],  # Back face (corrected winding)
    [2, 3, 7, 6],  # Front face
    [1, 2, 6, 5],  # Right face
    [0, 4, 7, 3]   # Left face (corrected winding)
]

# Define texture coordinates for each face
texture_coords = [
    [0, 0], [1, 0], [1, 1], [0, 1]
]