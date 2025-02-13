import argparse
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import numpy as np
import importlib

class ObjectViewer:
    def __init__(self, object_module=None, texture_path=None):
        self.vertices = []
        self.faces = []
        self.texture_coords = []
        self.texture_path = texture_path

        self.angle_x = 0.0
        self.angle_y = 0.0
        self.rotation_speed = 0.1
        self.wireframe_mode = False
        self.anti_aliasing_samples = 4  # Default anti-aliasing level
        self.fps = 0
        self.clock = pygame.time.Clock()
        self.mipmapping = True

        self.init_pygame()  # Initialize pygame first!
        self.init_opengl()  # Make sure OpenGL is ready before loading textures
        self.font = pygame.font.Font(None, 36)

        self.load_object(object_module)

        # Load texture AFTER OpenGL is initialized!
        self.texture = self.load_texture(self.texture_path or "textures/1.jpg")



    def load_object(self, module_name):
        try:
            module = importlib.import_module(f"objects.{module_name}")
            self.vertices = module.vertices
            self.faces = module.faces
            self.texture_coords = module.texture_coords
        except Exception as e:
            print(f"Error loading object module '{module_name}': {e}")
            # Load fallback cube data
            from objects.cube import vertices, faces, texture_coords
            self.vertices = vertices
            self.faces = faces
            self.texture_coords = texture_coords

    def load_texture(self, image_path):
        try:
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)

            image = Image.open(image_path)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = np.array(image.convert("RGBA"), dtype=np.uint8)

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height,
                         0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

            if self.mipmapping:
                glGenerateMipmap(GL_TEXTURE_2D)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            else:
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            return texture
        except FileNotFoundError:
            print(f"Texture file '{image_path}' not found. Using fallback texture.")
            return self.load_texture("textures/missing.jpg")
        except Exception as e:
            print(f"An error occurred while loading texture '{image_path}': {e}")
            return self.load_texture("textures/missing.jpg")

    def init_pygame(self):
        pygame.init()
        pygame.font.init() 
        display_flags = OPENGL | DOUBLEBUF | RESIZABLE
        pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, self.anti_aliasing_samples)
        self.screen = pygame.display.set_mode((1024, 768), display_flags)
        pygame.display.set_caption("py3d - Object Viewer")

    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        if self.anti_aliasing_samples > 0:
            glEnable(GL_MULTISAMPLE)
        else:
            glDisable(GL_MULTISAMPLE)
        gluPerspective(60, (1024 / 768), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.cleanup()
                quit()
            elif event.type == VIDEORESIZE:
                self.resize(event.size)
            elif event.type == MOUSEMOTION:
                if event.buttons[0]:  # Left mouse button is pressed
                    dx, dy = event.rel
                    self.angle_x += dy * self.rotation_speed
                    self.angle_y += dx * self.rotation_speed
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.cleanup()
                    quit()
                elif event.key == K_w:
                    self.wireframe_mode = not self.wireframe_mode
                    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if self.wireframe_mode else GL_FILL)
                elif event.key == K_SPACE:
                    self.angle_x = 0.0
                    self.angle_y = 0.0
                elif event.key == K_m:
                    self.mipmapping = not self.mipmapping
                    glBindTexture(GL_TEXTURE_2D, self.texture)
                    if self.mipmapping:
                        glGenerateMipmap(GL_TEXTURE_2D)
                        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                    else:
                        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                elif event.key == K_f:
                    self.toggle_fullscreen()
                elif event.key == K_t:
                    self.change_texture()
                elif event.key == K_a:
                    self.change_anti_aliasing()

    def resize(self, size):
        width, height = size
        pygame.display.set_mode((width, height), OPENGL | DOUBLEBUF | RESIZABLE)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / height if height > 0 else 1
        gluPerspective(60, aspect, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def toggle_fullscreen(self):
        pygame.display.toggle_fullscreen()

    def change_texture(self):
        # Implement texture change logic here
        # For example, cycle through available textures
        pass  # Placeholder for actual implementation

    def change_anti_aliasing(self):
        # Switch between different anti-aliasing levels
        aa_levels = [0, 2, 4, 8, 16]
        current_index = aa_levels.index(self.anti_aliasing_samples)
        self.anti_aliasing_samples = aa_levels[(current_index + 1) % len(aa_levels)]
        self.init_pygame()
        self.init_opengl()

    def draw_object(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glBegin(GL_TRIANGLES)
    
        for face in self.faces:
            for idx in face:
                if idx >= len(self.texture_coords):  # Check if index is valid
                    print(f"Error: Index {idx} out of range for texture_coords (len={len(self.texture_coords)})")
                    continue  # Skip this iteration to prevent crashing
            
                glTexCoord2fv(self.texture_coords[idx])
                glVertex3fv(self.vertices[idx])

        glEnd()
    def draw_overlay(self):
        overlay_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 128))

        aa_text = f"{self.anti_aliasing_samples}x" if self.anti_aliasing_samples > 0 else "Off"
        wf_mode = "Wireframe" if self.wireframe_mode else "Solid"
        mipmap_status = "On" if self.mipmapping else "Off"

        lines = [
            f"FPS: {self.fps:.2f}",
            f"Angle X: {self.angle_x:.2f}",
            f"Angle Y: {self.angle_y:.2f}",
            f"Mode: {wf_mode}",
            f"Anti-Aliasing: {aa_text}",
            f"Mipmapping: {mipmap_status}"
        ]

        y = 10
        for line in lines:
            text_surface = self.font.render(line, True, (255, 255, 255))
            overlay_surface.blit(text_surface, (10, y))
            y += text_surface.get_height() + 5

        overlay_texture = glGenTextures(1)
        overlay_data = pygame.image.tostring(overlay_surface, "RGBA", True)
        glBindTexture(GL_TEXTURE_2D, overlay_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, overlay_surface.get_width(),
                     overlay_surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, overlay_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        width, height = self.screen.get_size()
        glOrtho(0, width, height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, overlay_texture)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(10, 10)
        glTexCoord2f(1, 1)
        glVertex2f(overlay_surface.get_width() + 10, 10)
        glTexCoord2f(1, 0)
        glVertex2f(overlay_surface.get_width() + 10, overlay_surface.get_height() + 10)
        glTexCoord2f(0, 0)
        glVertex2f(10, overlay_surface.get_height() + 10)
        glEnd()

        glDeleteTextures(1, [overlay_texture])
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(self.angle_x, 1, 0, 0)
        glRotatef(self.angle_y, 0, 1, 0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        self.draw_object()
        glPopMatrix()
        self.draw_overlay()
        pygame.display.flip()

    def update(self):
        delta_time = self.clock.tick(60) / 1000.0  # Limit to 60 FPS
        self.fps = self.clock.get_fps()
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            self.angle_x += 1
        if keys[K_DOWN]:
            self.angle_x -= 1
        if keys[K_LEFT]:
            self.angle_y -= 1
        if keys[K_RIGHT]:
            self.angle_y += 1

    def cleanup(self):
        pygame.quit()

    def run(self):
        running = True  # Variable to control the loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False  # Exit the loop when closing the window

            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()  # Update the display

        pygame.quit() 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='3D Object Viewer')
    parser.add_argument('-o', '--object', type=str, help='Name of the object module in objects package')
    parser.add_argument('-t', '--texture', type=str, help='Path to texture image')
    args = parser.parse_args()

    viewer = ObjectViewer(object_module=args.object or 'cube', texture_path=args.texture)
    viewer.run()