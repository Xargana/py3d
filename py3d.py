import argparse
import pygame
import pygame.font
import numpy 
from pygame.locals import *
from pygame import HWSURFACE, DOUBLEBUF
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

loaded_textures = []
mm = "on"

def load_texture(image_path, old_texture=None):
    global loaded_textures
    
    # Delete the old texture if it exists
    if old_texture:
        glDeleteTextures(1, [old_texture])
        loaded_textures.remove(old_texture)  # Remove from tracking list
    
    # Generate new texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    with Image.open(image_path) as image:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.convert("RGBA").tobytes()

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Track the new texture
    loaded_textures.append(texture)

    return texture

def draw_object(vertices, faces, texture_coords):
    glBegin(GL_QUADS if len(faces[0]) == 4 else GL_TRIANGLES)
    for face in faces:
        for i, vertex in enumerate(face):
            glTexCoord2f(*texture_coords[i])  # Assign correct texture coordinate
            glVertex3fv(vertices[vertex])
    glEnd()

def set_texture_quality(quality='high'):
    quality_settings = {
        'low': (GL_NEAREST, GL_NEAREST),
        'medium': (GL_LINEAR, GL_LINEAR),
        'high': (GL_LINEAR_MIPMAP_LINEAR, GL_LINEAR)
    }
    
    min_filter, mag_filter = quality_settings[quality]
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag_filter)

    return min_filter


def load_object_module(module_path):
    """Dynamically load an object module from a module path"""
    try:
        import importlib

        # Import the module using its module path
        module_pathfull = str("objects." + module_path)
        module = importlib.import_module(module_pathfull)

        return module.vertices, module.faces, module.texture_coords

    except Exception as e:
        print(f"Error loading object file: {e}")
        # Load fallback cube data
        from objects.cube import vertices, faces, texture_coords
        return vertices, faces, texture_coords

def draw_overlay(font, window_size, fps, angle_x, angle_y, anti_aliasing_samples, texture, wireframe_mode, mm):
    # Create an overlay surface at a fixed "virtual" resolution
    virtual_size = (300, 600)
    overlay_surface = pygame.Surface(virtual_size, pygame.SRCALPHA)
    # Optional: fill with a semi-transparent background
    overlay_surface.fill((0, 0, 0, 128))

    if anti_aliasing_samples > 1:
        aa = f"{anti_aliasing_samples}x"
    else:
        aa = "Off"
    
    if wireframe_mode == True:
        wf_mode = "Wireframe"
    elif wireframe_mode == False:
        wf_mode = "Solid"


    # Render your overlay text
    lines = [
        f"FPS: {fps:.2f}",
        f"Angle X: {angle_x:.2f}",
        f"Angle Y: {angle_y:.2f}",
        f"Mode: {wf_mode}",
        f"Anti-Aliasing: {aa}",
        f"Texture: {texture}",
        f"Mipmapping: {mm}"
        # Add more info lines here if needed.
    ]
    y = 10
    for line in lines:
        text_surface = font.render(line, True, (255, 255, 255))
        overlay_surface.blit(text_surface, (10, y))
        y += text_surface.get_height() + 5

    # Scale overlay to a portion of the window (e.g., right third)
    scaled_width = window_size[0] // 3
    scaled_height = window_size[1]
    scaled_overlay = pygame.transform.smoothscale(overlay_surface, (scaled_width, scaled_height))

    # Convert the scaled surface to a texture
    overlay_data = pygame.image.tostring(scaled_overlay, "RGBA", True)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, scaled_width, scaled_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, overlay_data)

    # Set up orthographic projection so we can draw in 2D
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, window_size[0], window_size[1], 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Enable blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)

    # Draw a quad for the overlay on the right side of the window
    x_pos = 0 
    y_pos = 0  # Top
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(x_pos, y_pos)  
    glTexCoord2f(1, 1); glVertex2f(x_pos + scaled_width, y_pos)
    glTexCoord2f(1, 0); glVertex2f(x_pos + scaled_width, y_pos + scaled_height)
    glTexCoord2f(0, 0); glVertex2f(x_pos, y_pos + scaled_height)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)

    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Clean up: delete the texture to avoid memory buildup





def main():
    parser = argparse.ArgumentParser(description='3D Object Viewer')
    parser.add_argument('-o', '--object', type=str, help='Path to object definition file')
    parser.add_argument('-t', '--texture', type=str, help='Path to texture file')
    args = parser.parse_args()
    wireframe_mode = False
    mm = "on"


    # Load object data - either from specified file or fallback to cube
    if args.object:
        vertices, faces, texture_coords = load_object_module(args.object)
    else:
        from objects.cube import vertices, faces, texture_coords


    pygame.init()

    font = pygame.font.Font(None, 36)

    # Request multisampling (anti-aliasing) settings
    pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 4)  # Default to 4x multisampling

    # Don't listen to your ide
    screen = pygame.display.set_mode((800, 600), OPENGL | RESIZABLE | DOUBLEBUF)
    # ^^^ this IS used, don't delete it
    gluPerspective(60, (800 / 600), 0.1, 50.0)
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

    # while true my beloved :3
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
            

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    wireframe_mode = not wireframe_mode
                    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe_mode else GL_FILL)
                    print(f"Wireframe mode: {'enabled' if wireframe_mode else 'disabled'}")                  

        if keys[K_UP]:
            angle_x += 1
        if keys[K_DOWN]:
            angle_x -= 1
        if keys[K_LEFT]:
            angle_y -= 1
        if keys[K_RIGHT]:
            angle_y += 1
        if keys[K_SPACE]:
            angle_x = 0
            angle_y = 0


        if keys[K_m]:  # 'Q' for texture quality
            if keys[K_1]:
                set_texture_quality('low')
                mm = "off"
                print("Mipmapping disabled")
            elif keys[K_2]:
                set_texture_quality('high')
                mm = "on"
                print("Mipmapping enabled")

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
                    # this weirdly sets it to 165 fps
                    # maybe it enables vsync?
                    refresh_rate = 144
                    print(f"Frame limiting enabled. FPS: {refresh_rate}")
                elif keys[K_5]:
                    refresh_rate = 165
                    print(f"Frame limiting enabled. FPS: {refresh_rate}")
                elif keys[K_0]:
                    refresh_rate = 0
                    print(f"Frame limiting disabled.")

        # fix later

        if keys[K_t]:
            try:
                if keys[K_1]:
                    texture = load_texture("textures/1.jpg")
                    glGenerateMipmap(GL_TEXTURE_2D)
                    print(f"Texture 1 loaded.")
                if keys[K_2]:
                    texture = load_texture("textures/2.jpg")
                    glGenerateMipmap(GL_TEXTURE_2D)
                    print(f"Texture 2 loaded.")
                if keys[K_3]:
                    texture = load_texture("textures/3.jpg")
                    glGenerateMipmap(GL_TEXTURE_2D)
                    print(f"Texture 3 loaded.")
                if keys[K_4]:
                    texture = load_texture("textures/white.jpg")
                    glGenerateMipmap(GL_TEXTURE_2D)
                    print(f"Texture 4 loaded.")
            except FileNotFoundError:
                print("Texture file not found. Using fallback texture.")
                texture = load_texture("textures/missing.jpg")
            except Exception as e:
                print(f"An error occurred while loading the texture: {e}")

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
        # just realised how bad this is
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
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        draw_object(vertices, faces, texture_coords)
        if is_visible([0, 0, -5], 2.0):
            glCallList(display_list)
        glPopMatrix()

        if wireframe_mode == True:
            pygame.display.set_caption(f"py3d | mode: wireframe | FPS: {fps:.2f} ")
        else:
            pygame.display.set_caption(f"py3d | mode: solid | FPS: {fps:.2f} ")

        window_size = pygame.display.get_surface().get_size()
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        draw_overlay(font, window_size, fps, angle_x, angle_y, anti_aliasing_samples, texture, wireframe_mode, mm)
        glBindTexture(GL_TEXTURE_2D, texture)
        if wireframe_mode == True:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        pygame.display.flip()

        
if __name__ == "__main__":
    main()

