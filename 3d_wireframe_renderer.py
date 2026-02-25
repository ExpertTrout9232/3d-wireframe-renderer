import numpy as np
from PIL import Image, ImageDraw

width, height = 640, 480
fov = 60
z_near, z_far = 0.1, 100

camera_pos = [2, 0.9, 0]
camera_rot = [0, 30, 0]

stroke_width = 2
stroke_color = (0, 0, 0)

vertices = [
    [-1, 0, -2],
    [1, 0, -2],
    [1, 0, -4],
    [-1, 0, -4],
    [-1, 1, -2],
    [1, 1, -2],
    [1, 1, -4],
    [-1, 1, -4],
]

edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7),]

img = Image.new('RGB', (width, height), color='white')

translation_matrix = np.array([
    [1, 0, 0, -camera_pos[0],],
    [0, 1, 0, -camera_pos[1],],
    [0, 0, 1, -camera_pos[2],],
    [0, 0, 0, 1,],
])

rotation_matrix_pitch = np.array([
    [1, 0, 0, 0,],
    [0, np.cos(np.radians(-camera_rot[0])), -np.sin(np.radians(-camera_rot[0])), 0,],
    [0, np.sin(np.radians(-camera_rot[0])), np.cos(np.radians(-camera_rot[0])), 0,],
    [0, 0, 0, 1,],
])

rotation_matrix_yaw = np.array([
    [np.cos(np.radians(-camera_rot[1])), 0, np.sin(np.radians(-camera_rot[1])), 0,],
    [0, 1, 0, 0,],
    [-np.sin(np.radians(-camera_rot[1])), 0, np.cos(np.radians(-camera_rot[1])), 0,],
    [0, 0, 0, 1,],
])

rotation_matrix_roll = np.array([
    [np.cos(np.radians(-camera_rot[2])), -np.sin(np.radians(-camera_rot[2])), 0, 0,],
    [np.sin(np.radians(-camera_rot[2])), np.cos(np.radians(-camera_rot[2])), 0, 0,],
    [0, 0, 1, 0,],
    [0, 0, 0, 1,],
])

rotation_matrix = rotation_matrix_roll @ rotation_matrix_pitch @ rotation_matrix_yaw
view_matrix = rotation_matrix @ translation_matrix

focus = 1 / np.tan(np.radians(fov) / 2)
aspect_ratio = width / height

projection_matrix = np.array([
    [focus / aspect_ratio, 0, 0, 0,],
    [0, focus, 0, 0,],
    [0, 0, (z_far + z_near) / (z_near - z_far), (2 * z_far * z_near) / (z_near - z_far),],
    [0, 0, -1, 0,],
])

projected_vertices = []

for vertex in vertices:
    view_pos = view_matrix @ np.array(vertex + [1])

    clip_pos = projection_matrix @ view_pos

    w = clip_pos[3]
    if w != 0:
        ndc_pos = clip_pos[:3] / w

        if any(np.abs(ndc_pos) > 1):
            projected_vertices.append(None)
            continue

        screen_x = int((ndc_pos[0] + 1) * width / 2)
        screen_y = int((1 - ndc_pos[1]) * height / 2)

        projected_vertices.append((screen_x, screen_y))
    else:
        projected_vertices.append(None)

        

for edge in edges:
    if projected_vertices[edge[0]] is None or projected_vertices[edge[1]] is None:
        continue
    else:
        x_start, y_start = projected_vertices[edge[0]]
        x_end, y_end = projected_vertices[edge[1]]

        draw = ImageDraw.Draw(img)
        draw.line([(x_start, y_start), (x_end, y_end)], fill=stroke_color, width=stroke_width)

img.show()