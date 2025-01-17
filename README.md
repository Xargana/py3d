
# 3D Object Viewer

## Overview

This is a Python-based 3D object viewer built using **Pygame**, **PyOpenGL**, and **Pillow**. The application allows you to load and view 3D objects with textures, dynamically adjust rendering settings, and interact with the object using keyboard and mouse inputs.

## Requirements

- Python 3.8 or higher
- Dependencies:
  - `pygame`
  - `PyOpenGL`
  - `numpy`
  - `Pillow`

Install dependencies via pip:

```bash
pip install pygame PyOpenGL numpy Pillow
```


## How to Use

### Running the Program

To start the viewer, run the script in a terminal:

```bash
python viewer.py [-o OBJECT_FILE] [-t TEXTURE_FILE]
```

- `-o, --object`: Path to the 3D object module (Python file).
- `-t, --texture`: Path to the texture file (e.g., `.jpg`, `.png`).

### Example

```bash
python viewer.py -o cube -t 1.jpg
```

If no object or texture is specified, a default cube and texture will be used.

### Controls

- **Mouse**:
  - Drag (left button) to rotate the object.
- **Keyboard**:
  - Arrow keys: Rotate the object.
  - `F` + `1-5`: Set frame rate limit.
    - `F` + `0`: Disable frame rate limit.
  - `T` + `1-3`: Load different textures (`textures/1.jpg`, `textures/2.jpg`, etc.).
  - `A` + `1-4`: Set anti-aliasing (2x, 4x, 8x, 16x).
    - `A` + `0`: Disable anti-aliasing.
  - `M` + `1-2`: Enable/Disable mipmapping

## Customization

### Adding New Objects

Create a Python module for your object with the following attributes:

- `vertices`: List of vertex coordinates.
- `faces`: List of faces, defined by indices into the `vertices` list.
- `texture_coords`: Texture coordinates corresponding to each vertex.

Save the module in the `objects` directory.

### Adding New Textures

Place texture files (`.jpg`) in the `textures` directory. Use the `-t` flag to switch textures.

## License

This project is open-source and available under the MIT License. Feel free to modify and distribute it.

## Acknowledgments

- **Pygame** for window management and input handling.
- **PyOpenGL** for 3D rendering.
- **Pillow** for texture image processing.
