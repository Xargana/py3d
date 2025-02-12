import pygame
from OpenGL.GL import *

def draw_overlay(font, window_size, fps, angle_x, angle_y):
    # Create an overlay surface at a fixed "virtual" resolution
    virtual_size = (300, 600)
    overlay_surface = pygame.Surface(virtual_size, pygame.SRCALPHA)
    # Optional: fill with a semi-transparent background
    overlay_surface.fill((0, 0, 0, 128))

    # Render your overlay text
    lines = [
        f"FPS: {fps:.2f}",
        f"Angle X: {angle_x:.2f}",
        f"Angle Y: {angle_y:.2f}",
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
    x_pos = window_size[0] - scaled_width  # Right side
    y_pos = 0  # Top
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x_pos, y_pos)
    glTexCoord2f(1, 0); glVertex2f(x_pos + scaled_width, y_pos)
    glTexCoord2f(1, 1); glVertex2f(x_pos + scaled_width, y_pos + scaled_height)
    glTexCoord2f(0, 1); glVertex2f(x_pos, y_pos + scaled_height)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)

    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Clean up: delete the texture to avoid memory buildup
    glDeleteTextures([tex_id])


# === In your main loop, after drawing the 3D scene but before flip() ===
# For example:
def main():
    pygame.init()
    # Setup your main window as usual
    screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
    pygame.display.set_caption("3D Viewer")
    font = pygame.font.Font(None, 36)
    
    # Initialize your OpenGL perspective, etc.
    # ... (your OpenGL initialization and scene setup)

    clock = pygame.time.Clock()
    angle_x, angle_y = 0.0, 0.0

    while True:
        # --- Handle events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            # ... (your event handling)

        # --- Update scene variables ---
        # (update angle_x, angle_y, etc. based on input)
        delta_time = clock.tick(60) / 1000.0
        fps = clock.get_fps()

        # --- Render 3D scene ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        # ... (your 3D rendering code using angle_x, angle_y, etc.)
        glPopMatrix()

        # --- Render overlay ---
        window_size = pygame.display.get_surface().get_size()
        draw_overlay(font, window_size, fps, angle_x, angle_y)

        pygame.display.flip()

if __name__ == "__main__":
    main()
