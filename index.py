import argparse
import pygame
import numpy # Don't remove, needed by pyopengl
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image



def load_texture(image_path):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # Load image using PIL
    with Image.open(image_path) as image:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.convert("RGBA").tobytes()

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    # Change LINEAR to NEAREST for sharp textures
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    return texture

def draw_object(vertices, faces, texture_coords):
    glBegin(GL_QUADS if len(faces[0]) == 4 else GL_TRIANGLES)
    for face in faces:
        for i, vertex in enumerate(face):
            glTexCoord2f(*texture_coords[i])  # Assign correct texture coordinate
            glVertex3fv(vertices[vertex])
    glEnd()



def load_object_module(module_path):
    """Dynamically load an object module from a module path"""
    try:
        import importlib

        # Import the module using its module path
        module = importlib.import_module(module_path)

        return module.vertices, module.faces, module.texture_coords

    except Exception as e:
        print(f"Error loading object file: {e}")
        # Load fallback cube data
        from objects.cube import vertices, faces, texture_coords
        return vertices, faces, texture_coords


def main():
    parser = argparse.ArgumentParser(description='3D Object Viewer')
    parser.add_argument('-o', '--object', type=str, help='Path to object definition file')
    parser.add_argument('-t', '--texture', type=str, help='Path to texture file')
    args = parser.parse_args()

    # Load object data - either from specified file or fallback to cube
    if args.object:
        vertices, faces, texture_coords = load_object_module(args.object)
    else:
        from objects.cube import vertices, faces, texture_coords

    pygame.init()

    # Set the background color to light blue
    glClearColor(0.5, 0.7, 1.0, 1.0)  # RGB values from 0.0 to 1.0, plus alpha

    # Request multisampling (anti-aliasing) settings
    pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 4)  # Default to 4x multisampling

    screen = pygame.display.set_mode((800, 600), OPENGL | RESIZABLE | DOUBLEBUF)
    gluPerspective(45, (800 / 600), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)

    anti_aliasing_samples = 4  # Default anti-aliasing level
    glEnable(GL_MULTISAMPLE)

    def is_visible(position, radius):
        # Simple sphere-frustum intersection test
        x, y, z = position
        return abs(x) < radius and abs(y) < radius and -5 < z < -1
    
    def create_display_list(vertices, faces, texture_coords):
        display_list = glGenLists(1)
        glNewList(display_list, GL_COMPILE)
        draw_object(vertices, faces, texture_coords)
        glEndList()
        return display_list
    
    display_list = create_display_list(vertices, faces, texture_coords)

    def setup_vbo(vertices, faces):
        # Create buffers
        vbo = glGenBuffers(1)
        ebo = glGenBuffers(1)
    
        # Bind vertex buffer
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, numpy.array(vertices, dtype=numpy.float32), GL_STATIC_DRAW)
    
        # Bind element buffer
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, numpy.array(faces, dtype=numpy.uint32), GL_STATIC_DRAW)
    
        return vbo, ebo

    vbo, ebo = setup_vbo(vertices, faces)


    try:
        texture = load_texture("textures/1.jpg")  # Use the provided texture file
    except FileNotFoundError:
        print("Texture file not found. Using fallback texture.")
        texture = load_texture("textures/missing.jpg")  # Fallback texture
    finally:
        if args.texture:
            texturename = str("textures/" + args.texture)
            texture = load_texture(texturename)

    clock = pygame.time.Clock()
    frame_limit = 6  # Start with frame limiting enabled
    refresh_rate = 60  # Target FPS
    fps_display_timer = 0
    angle_x = 0.0  # Rotation around x-axis
    angle_y = 0.0  # Rotation around y-axis
    rotation_speed_factor = 0.1  # Adjust this for mouse sensitivity

    while True:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # Left mouse button is pressed
                    dx, dy = event.rel
                    angle_x += dy * rotation_speed_factor
                    angle_y += dx * rotation_speed_factor

        if keys[K_UP]:
            angle_x += 1
        if keys[K_DOWN]:
            angle_x -= 1
        if keys[K_LEFT]:
            angle_y -= 1
        if keys[K_RIGHT]:
            angle_y += 1
        

        # i know the check for the key is a bit weird
        if keys[K_f]:
                if keys[K_1]:
                    refresh_rate = 10
                    print(f"Frame limiting enabled. FPS: {refresh_rate}")
                elif keys[K_2]:
                    refresh_rate = 30
                    print(f"Frame limiting enabled. FPS: {refresh_rate}")
                elif keys[K_3]:
                    refresh_rate = 60
                    print(f"Frame limiting enabled. FPS: {refresh_rate}")
                elif keys[K_4]:
                    refresh_rate = 144
                    print(f"Frame limiting enabled. FPS: {refresh_rate}")
                elif keys[K_5]:
                    refresh_rate = 165
                    print(f"Frame limiting enabled. FPS: {refresh_rate}")
                elif keys[K_0]:
                    refresh_rate = 0
                    print(f"Frame limiting disabled.")

        if keys[K_t]:
            try:
                if keys[K_1]:
                    texture = load_texture("textures/1.jpg")
                    print(f"Texture 1 loaded.")
                elif keys[K_2]:
                    texture = load_texture("textures/2.jpg")
                    print(f"Texture 2 loaded.")
                elif keys[K_3]:
                    texture = load_texture("textures/3.jpg")
                    print(f"Texture 3 loaded.")
            except FileNotFoundError:
                print("Texture file not found. Using fallback texture.")
                texture = load_texture("textures/missing.jpg")

        if keys[K_a]:
            if keys[K_1]:
                anti_aliasing_samples = 2
            elif keys[K_2]:
                anti_aliasing_samples = 4
            elif keys[K_3]:
                anti_aliasing_samples = 8
            elif keys[K_4]:
                anti_aliasing_samples = 16
            elif keys[K_0]:
                anti_aliasing_samples = 0

            if anti_aliasing_samples > 0:
                pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, anti_aliasing_samples)
                glEnable(GL_MULTISAMPLE)
                print(f"Anti-aliasing set to {anti_aliasing_samples}x.")
            else:
                glDisable(GL_MULTISAMPLE)
                print("Anti-aliasing disabled.")

        # Frame limiting logic
        if frame_limit:
            delta_time = clock.tick(refresh_rate) / 1000.0 if refresh_rate else clock.tick() / 1000.0
        else:
            delta_time = clock.tick() / 1000.0

        # Calculate FPS
        fps = clock.get_fps()
        fps_display_timer += delta_time
        if fps_display_timer >= 0.5:
            print(f"FPS: {fps:.2f}")
            fps_display_timer = 0

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(angle_x, 1, 0, 0)
        glRotatef(angle_y, 0, 1, 0)
        glBindTexture(GL_TEXTURE_2D, texture)
        draw_object(vertices, faces, texture_coords)
        if is_visible([0, 0, -5], 2.0):
            glCallList(display_list)
        glPopMatrix()

        pygame.display.flip()
if __name__ == "__main__":
    main()

