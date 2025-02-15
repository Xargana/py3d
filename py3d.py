import argparse
import pygame
import pygame.font
import numpy 
import threading
import queue
import numpy as np
from pygame.locals import *
from pygame import HWSURFACE, DOUBLEBUF
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

loaded_textures = []
command_queue = queue.Queue()
prev_tex_id = None  # Store the previous texture globally


# Will probably remove this, easily causes a memory leak
def console_input():
    try:
        while True:
            command = input("> ")  # Read user input
            command_queue.put(command)
            if command == "exit":
                print("Exiting...")
                break
    except EOFError:
        # do nothing
        print("")
        
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

def draw_overlay(font, window_size, fps, angle_x, angle_y, anti_aliasing_samples, texture, wireframe_mode, mm, delta_time, fov, refresh_rate, view_mode):
    global prev_tex_id  # Reference the previous texture

    if prev_tex_id is not None:
        glDeleteTextures([prev_tex_id])  # Delete the old texture before creating a new one

    # Create an overlay surface at a fixed "virtual" resolution
    virtual_size = (280, 310)
    overlay_surface = pygame.Surface(virtual_size, pygame.SRCALPHA)
    overlay_surface.fill((0, 0, 0, 128))  # Optional: semi-transparent background

    # Anti-aliasing and wireframe mode text
    aa = f"{anti_aliasing_samples}x" if anti_aliasing_samples > 1 else "Off"
    wf_mode = "Wireframe" if wireframe_mode else "Solid"

    # Overlay text
    lines = [
        f"FPS: {fps:.1f}/{refresh_rate}",
        f"Angle X: {angle_x:.2f}",
        f"Angle Y: {angle_y:.2f}",
        f"Fov: {fov}",
        f"Mode: {wf_mode}",
        f"Anti-Aliasing: {aa}",
        f"Texture: {texture}",
        f"Mipmapping: {mm}",
        f"Delta Time: {delta_time:.3f}",
        f"View mode: {view_mode}",
        f"tex_debug: {prev_tex_id}"  # Debug previous texture ID
    ]

    # Render text
    y = 10
    for line in lines:
        text_surface = font.render(line, True, (255, 255, 255))
        overlay_surface.blit(text_surface, (10, y))
        y += text_surface.get_height() + 5

    # Scale overlay
    scaled_width = window_size[0] // 3.6
    scaled_height = window_size[1] // 2.2
    scaled_overlay = pygame.transform.smoothscale(overlay_surface, (scaled_width, scaled_height))

    # Convert the scaled surface to a texture
    overlay_data = pygame.image.tostring(scaled_overlay, "RGBA", True)
    tex_id = glGenTextures(1)  # Generate new texture
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, scaled_width, scaled_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, overlay_data)

    # Store the current texture for next frame deletion
    prev_tex_id = tex_id  

    # Setup orthographic projection
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, window_size[0], window_size[1], 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Enable blending and texture for overlay
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)

    # Draw overlay quad
    x_pos = 0
    y_pos = 0  # Top-left corner
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(x_pos, y_pos)
    glTexCoord2f(1, 1); glVertex2f(x_pos + scaled_width, y_pos)
    glTexCoord2f(1, 0); glVertex2f(x_pos + scaled_width, y_pos + scaled_height)
    glTexCoord2f(0, 0); glVertex2f(x_pos, y_pos + scaled_height)
    glEnd()

    # Cleanup
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)

    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glBindTexture(GL_TEXTURE_2D, 0)  # Unbind texture

# todo:

def generate_missing_texture(size=128, squares=8):
    """
    Generate a checkerboard missing texture.
    :param size: Overall resolution (size x size pixels).
    :param squares: Number of squares per row/column.
    :return: NumPy array with shape (size, size, 3) in uint8.
    """
    # Calculate the size of each square.
    square_size = size // squares
    # Create an empty array.
    image = np.zeros((size, size, 3), dtype=np.uint8)
    for y in range(squares):
        for x in range(squares):
            if (x + y) % 2 == 0:
                color = [0, 0, 0]         # Black
            else:
                color = [255, 0, 255]     # Purple
            image[y*square_size:(y+1)*square_size, x*square_size:(x+1)*square_size] = color
    return image

def load_missing_texture():
    img_data = generate_missing_texture()
    size = img_data.shape[0]  # assuming square texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    # Upload the texture data.
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, size, size, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    
    # Set texture parameters.
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    return texture

def set_projection(mode):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    if mode == 0:  # Perspective Projection
        gluPerspective(60, 1024 / 768, 0.1, 50.0)

    elif mode == 1:  # Orthographic Projection
        glOrtho(-2.0, 2.0, -2.0, 2.0, 0.1, 50.0)

    elif mode == 2:  # Isometric Projection
        glOrtho(-2.0, 2.0, -2.0, 2.0, 0.1, 50.0)
        glRotatef(35.26, 1, 0, 0)  # Tilt downwards
        glRotatef(45, 0, 1, 0)  # Rotate for isometric effect

    elif mode == 3:  # Oblique Projection
        glOrtho(-2.0, 2.0, -2.0, 2.0, 0.1, 50.0)
        shear_matrix = np.array([
            [1, 0.5, 0, 0],  # Shear X
            [0, 1, 0, 0],  # No shear Y
            [0, 0, 1, 0],  
            [0, 0, 0, 1]
        ], dtype=np.float32)
        glMultMatrixf(shear_matrix.flatten())  # Apply oblique shear

    elif mode == 4:  # Fisheye-Like Projection (Extreme Perspective)
        glFrustum(-1, 1, -1, 1, 0.1, 50.0)  # Wide frustum for distortion
        glTranslatef(0, 0, -2)  # Pull back slightly
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def cleanup():
    global loaded_textures
    for tex in loaded_textures:
        glDeleteTextures(1, [tex])
    loaded_textures.clear()
    if prev_tex_id:
        glDeleteTextures(1, [prev_tex_id])

def main():
    try:
        parser = argparse.ArgumentParser(description='3D Object Viewer')
        parser.add_argument('-o', '--object', type=str, help='Path to object definition file')
        parser.add_argument('-t', '--texture', type=str, help='Path to texture file')
        args = parser.parse_args()
        projection_mode = 0  # 0 = Perspective, 1 = Ortho, 2 = Isometric, 3 = Oblique, 4 = Fisheye
        wireframe_mode = False
        mm = "on"
        view_mode = "Perspective"
        mipmapping = False
        camera_distance = -5 
        clock = pygame.time.Clock()
        frame_limit = 6  # Start with frame limiting enabled
        refresh_rate = 165  # Target FPS
        fps_display_timer = 0
        angle_x = 0.0  # Rotation around x-axis
        angle_y = 180.0  # Rotation around y-axis
        rotation_speed_factor = 0.1  # Adjust this for mouse sensitivity
        width = 1024
        height = 768


        # Load object data - either from specified file or fallback to cube
        if args.object:
            vertices, faces, texture_coords = load_object_module(args.object)
        else:            from objects.cube import vertices, faces, texture_coords


        pygame.init()

        font = pygame.font.Font(None, 32)

        # Request multisampling (anti-aliasing) settings
        pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 4)  # Default to 4x multisampling

        # Don't listen to your ide
        screen = pygame.display.set_mode((1024, 768), OPENGL | RESIZABLE | DOUBLEBUF)
        # ^^^ this IS used, don't delete it
        fov = 40
        gluPerspective(fov, (1024 / 768), 0.1, 50.0)
        glTranslatef(0.0, 0.0, camera_distance)

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
            if args.texture:
                try:
                    texturename = str("textures/" + args.texture)
                    texture = load_texture(texturename)
                except FileNotFoundError:
                    print("Texture file not found. Using fallback texture.")
                    load_missing_texture()  # Fallback texture
            else:        
                texture = load_texture("textures/1.jpg")  # Use the provided texture file
        except FileNotFoundError:
            print("Texture file not found. Using fallback texture.")
            load_missing_texture()  # Fallback texture


        # while true my beloved :3
        while True:
            keys = pygame.key.get_pressed()
            glClearColor(0.13, 0.17, 0.23, 1.0)  # RGB for sky-blue

            if angle_x > 360:
                angle_x = 0
            if angle_y > 360:
                angle_y = 0
            if angle_x < 0:
                angle_x = 360
            if angle_y < 0:
                angle_y = 360

            # Process commands
            while not command_queue.empty():
                command = command_queue.get()
                if command == "exit":
                    cleanup()
                    pygame.quit()
                    quit()
                elif command.startswith("texture "):
                    _, path = command.split(" ", 1)
                    texture = load_texture(path)
                    print(f"Texture set to {path}")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cleanup()
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        cleanup()
                        pygame.quit()
                        quit()

                if event.type == pygame.VIDEORESIZE:
                    width, height = event.size
                    glViewport(0, 0, width, height)
                    glMatrixMode(GL_PROJECTION)
                    glLoadIdentity()
                    gluPerspective(fov, width / height, 0.1, 50.0)
                    glMatrixMode(GL_MODELVIEW)
                    glLoadIdentity()
                    glTranslatef(0.0, 0.0, camera_distance)

                if event.type == pygame.MOUSEMOTION:
                    if event.buttons[0]:  # Left mouse button is pressed
                        dx, dy = event.rel
                        angle_x += dy * rotation_speed_factor
                        angle_y += dx * rotation_speed_factor 
                

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        wireframe_mode = not wireframe_mode
                        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe_mode else GL_FILL)     

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up
                        fov -= 1
                        glLoadIdentity()  # Reset matrix to apply changes
                        gluPerspective(fov, (1024 / 768), 0.1, 50.0)  # Update perspective
                        glTranslatef(0.0, 0.0, -5)
                    elif event.button == 5:  # Scroll down
                        fov += 1
                        glLoadIdentity()  # Reset matrix to apply changes
                        gluPerspective(fov, (1024 / 768), 0.1, 50.0)  # Update perspective
                        glTranslatef(0.0, 0.0, -5)

                if event.type == pygame.KEYDOWN:
                    if event.key == K_RETURN:
                        projection_mode = (projection_mode + 1) % 5  # Cycle through projections
                        set_projection(projection_mode)
                        if projection_mode == 0 :
                            view_mode = "Perspective"
                        elif projection_mode == 1 :
                            view_mode = "Orthographic"
                        elif projection_mode == 2 :
                            view_mode = "Isometric"
                        elif projection_mode == 3 :
                            view_mode = "Oblique"
                        elif projection_mode == 4 :
                            view_mode = "Fisheye"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        mipmapping = not mipmapping
                        if mipmapping:
                            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                            mm = "On"
                        else:
                            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                            mm = "Off"
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        print("\nExiting...")
                        pygame.quit()
                        quit()

            if keys[K_PAGEDOWN]:
                glTranslatef(0.0, 0.0, -0.1 * 100 * delta_time)
            if keys[K_PAGEUP]:
                glTranslatef(0.0, 0.0, 0.1 * 100 * delta_time)
            if keys[K_KP2]:
                glTranslatef(0.0, 0.1 * 100 * delta_time, 0.0)
            if keys[K_KP8]:
                glTranslatef(0.0, -0.1 * 100 * delta_time, 0.0)
            if keys[K_KP6]:
                glTranslatef(-0.1 * 100 * delta_time, 0.0, 0.0)
            if keys[K_KP4]:
                glTranslatef(0.1 * 100 * delta_time, 0.0, 0.0)

            if keys[K_KP_PLUS]:
                glScalef(1.1, 1.1, 1.1)
            if keys[K_KP_MINUS]:
                glScalef(0.9, 0.9, 0.9)


            if keys[K_UP]:
                if angle_x < 90 or angle_x >= 270:
                    angle_x = (angle_x + 1.5 * 100 * delta_time)
                else:
                    angle_x = 90  # Prevents crossing over

            if keys[K_DOWN]:
                if angle_x > 0 and angle_x <= 90 or angle_x > 270:
                    angle_x = (angle_x - 1.5 * 100 * delta_time)
                else:
                    angle_x = 270  # Prevents crossing over
            if keys [K_LEFT]:
                angle_y = (angle_y + 1.5 * 100 * delta_time) % 360
            if keys[K_RIGHT]:
                angle_y = (angle_y - 1.5 * 100 * delta_time) % 360
            if keys[K_SPACE]:
                angle_x = 180
                angle_y = 180

            # i know the check for the key is a bit weird
            if keys[K_f]:
                    if keys[K_1]:
                        refresh_rate = 10
                    elif keys[K_2]:
                        refresh_rate = 30
                    elif keys[K_3]:
                        refresh_rate = 60
                    elif keys[K_4]:
                        # this weirdly sets it to 165 fps
                        # maybe it enables vsync?
                        refresh_rate = 144
                    elif keys[K_5]:
                        refresh_rate = 165
                    elif keys[K_0]:
                        refresh_rate = 0

            # fix later

            if keys[K_t]:
                try:
                    if keys[K_1]:
                        texture = load_texture("textures/1.jpg")
                        glGenerateMipmap(GL_TEXTURE_2D)
                    if keys[K_2]:
                        texture = load_texture("textures/2.jpg")
                        glGenerateMipmap(GL_TEXTURE_2D)
                    if keys[K_3]:
                        texture = load_texture("textures/3.jpg")
                        glGenerateMipmap(GL_TEXTURE_2D)
                    if keys[K_4]:
                        texture = load_texture("textures/white.jpg")
                        glGenerateMipmap(GL_TEXTURE_2D)
                except FileNotFoundError:
                    print("Texture file not found. Using fallback texture.")
                    load_missing_texture()
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
                else:
                    glDisable(GL_MULTISAMPLE)
                    




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
            #    print(f"FPS: {fps:.2f}")
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
            draw_overlay(font, window_size, fps, angle_x, angle_y, anti_aliasing_samples, texture, wireframe_mode, mm, delta_time, fov, refresh_rate, view_mode)
            glBindTexture(GL_TEXTURE_2D, texture)
            if wireframe_mode == True:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

            pygame.display.flip()
    except KeyboardInterrupt:
        print(f"\nRecieved keyboard interrupt. Exiting...")
        cleanup()
        print(f"please wait while the program cleans the leaked memory")
        pygame.quit()
        quit()
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Renderer: {glGetString(GL_RENDERER).decode()}")
        print(f"Vendor: {glGetString(GL_VENDOR).decode()}")
        print(f"Version: {glGetString(GL_VERSION).decode()}")
        cleanup()
        pygame.quit()
        quit()

        
if __name__ == "__main__":
    main()
    
