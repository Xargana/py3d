import math

def generate_sphere(radius=1.0, lat_divisions=20, long_divisions=20):
    vertices = []
    faces = []
    texture_coords = []
    
    # Generate vertices
    for lat in range(lat_divisions + 1):
        lat_angle = (math.pi * lat) / lat_divisions
        for long in range(long_divisions + 1):
            long_angle = (2 * math.pi * long) / long_divisions
            
            # Calculate vertex position
            x = radius * math.sin(lat_angle) * math.cos(long_angle)
            y = radius * math.cos(lat_angle)
            z = radius * math.sin(lat_angle) * math.sin(long_angle)
            
            vertices.append([x, y, z])
            
            # Calculate texture coordinates
            u = long / long_divisions
            v = lat / lat_divisions
            texture_coords.append([u, v])
    
    # Generate faces
    for lat in range(lat_divisions):
        for long in range(long_divisions):
            # Calculate vertex indices
            current = lat * (long_divisions + 1) + long
            next_lat = (lat + 1) * (long_divisions + 1) + long
            
            # Create two triangles for each face
            faces.append([current, next_lat, next_lat + 1])
            faces.append([current, next_lat + 1, current + 1])
    
    return vertices, faces, texture_coords

# Generate the sphere with desired parameters
radius = 1.0
lat_divisions = 50
long_divisions = 50

# Directly assign the returned values
vertices, faces, texture_coords = generate_sphere(radius, lat_divisions, long_divisions)
