# this shit absoloutely sucks ass
# but it works
# so dont touch it

import time
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

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

def load_texture(image_path):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # Load image using PIL
    image = Image.open(image_path)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)  # Flip the image vertically
    img_data = image.convert("RGBA").tobytes()

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture

def draw_cube():
    texture_coords = [
        [0, 0], [1, 0], [1, 1], [0, 1] # Texture coordinates for each face
    ]

    glBegin(GL_QUADS)
    for face in faces:
        for i, vertex in enumerate(face):
            glTexCoord2f(*texture_coords[i])  # Assign correct texture coordinate
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    pygame.init()

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

    try:
        texture = load_texture("textures/1.jpg")  # Use the provided texture file
    except FileNotFoundError:
        print("Texture file not found. Using fallback texture.")
        texture = load_texture("textures/missing.jpg")  # Fallback texture

    clock = pygame.time.Clock()
    frame_limit = 6  # Start with frame limiting enabled
    refresh_rate = 60  # Target FPS
    fps_display_timer = 0
    angle_x = 0.0  # Rotation around x-axis
    angle_y = 0.0  # Rotation around y-axis
    rotation_speed_factor = 0.2  # Adjust this for mouse sensitivity

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

        # Check for frame rate toggles (F + 1, 2, 3, 4, 5, 0)
        if keys[K_f]:
            if keys[K_1]:
                refresh_rate = 24
            elif keys[K_2]:
                refresh_rate = 30
            elif keys[K_3]:
                refresh_rate = 60
            elif keys[K_4]:
                refresh_rate = 144
            elif keys[K_5]:
                refresh_rate = 165
            elif keys[K_0]:
                refresh_rate = 0  # Unlimited

        # Check for texture toggles (T + 1, 2, 3)
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

        # Check for anti-aliasing toggles (A + 1, 2, 3, 4, 0)
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
        draw_cube()
        glPopMatrix()

        pygame.display.flip()

if __name__ == "__main__":
    main()
