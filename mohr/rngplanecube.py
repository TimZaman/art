# (c) Tim Zaman 2017
# Draws rotating wireframe cubes in a grid with wire dropout
# Inspired by a work by Mohr in the Mountainview Computer Museum

import numpy as np
import math
import cairo
import datetime

canvas_size = np.array([512, 512], dtype=np.float32)
cube_size = 32
scale = 0.5
rot_scale = 3.14/12.
wire_line_width = 0.5
divider_line_width = 0.15
sign = "Tim Zaman %s"  % (datetime.datetime.now().isoformat())

def rotation_matrix(axis, theta):
    axis = np.asarray(axis)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

# Define cube
x = np.array([[0,0,0],
              [0,1,0],
              [1,1,0],
              [1,0,0],
              [0,0,1],
              [0,1,1],
              [1,1,1],
              [1,0,1] ], dtype=np.float32)

# Shift center to origin
x = x - 0.5

# Pre-rotate the center cube
# rm = rotation_matrix([1,1,1], 3.14/4)
# x = np.matmul(x, rm) 

def draw_wire(ctx, a, b, p_do=0):
    if np.random.random_sample() > p_do:
        # draw.line((a[0], a[1], b[0], b[1]), fill=0)
        ctx.move_to(a[0], a[1])
        ctx.line_to(b[0], b[1])

def draw_plane(ctx, a, b, c, d, rgb=[1,1,1], p_do=0):
    if np.random.random_sample() > p_do:
        ctx.move_to(a[0], a[1])
        ctx.line_to(b[0], b[1])
        ctx.line_to(c[0], c[1])
        ctx.line_to(d[0], d[1])
        ctx.set_source_rgba(rgb[0], rgb[1], rgb[2], 0.5)
        ctx.fill()

def draw_cube(ctx, x, size=64, offset=(0,0), p_do=0):

    # Project on 2D plane by dropping 3rd dim
    x = x[:,0:2]
    x = x * float(size) + offset
    p_do=0


    draw_plane(ctx, x[0], x[1], x[2], x[3], rgb=[1,0,0], p_do=p_do)
    draw_plane(ctx, x[4], x[5], x[6], x[7], rgb=[0,1,0], p_do=p_do)
    draw_plane(ctx, x[0], x[1], x[5], x[4], rgb=[0,0,1], p_do=p_do)
    draw_plane(ctx, x[2], x[3], x[7], x[6], rgb=[0,1,1], p_do=p_do)
    draw_plane(ctx, x[0], x[3], x[7], x[4], rgb=[1,1,0], p_do=p_do)
    draw_plane(ctx, x[1], x[5], x[6], x[2], rgb=[1,0,1], p_do=p_do)


    # Wire settings
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(wire_line_width)
    ctx.stroke()

surface = cairo.PDFSurface ("out2.pdf", canvas_size[0], canvas_size[1])
ctx = cairo.Context(surface)
# Fill the background with white
ctx.rectangle(0, 0, canvas_size[0], canvas_size[1])
ctx.set_source_rgb(1, 1, 1)
ctx.fill()


# Get a rotation matrix
nx = (canvas_size[0]/cube_size)/2
ny = (canvas_size[1]/cube_size)/2
for cx in np.arange(-nx+1, nx):
 
    # Draw horizontal lines
    # if cx != nx-1:
    #     h = (cx+nx+0.5) * cube_size
    #     draw_wire(ctx, [cube_size/2., h], [canvas_size[0]-cube_size/2., h])
    #     ctx.set_source_rgb(0, 0, 0)
    #     ctx.set_line_width(divider_line_width)
    #     ctx.stroke()

    for cy in np.arange(-ny+1, ny):
        
        # Compute rel. distance from center (L1)
        d_center = abs(float(cx)/float(nx)/2) + abs(float(cy)/float(ny)/2)

        # Compute wire dropout probability
        p_do = math.sqrt(d_center) #- 0.3

        rm = rotation_matrix([1,0,0], cy * rot_scale)
        xr = np.matmul(x, rm) 

        rm = rotation_matrix([0,1,0], cx * rot_scale)
        xr = np.matmul(xr, rm) 

        offset = canvas_size * 0.5
        offset = offset + (np.array([cx, cy]) * cube_size)

        draw_cube(ctx, xr, size=(cube_size * scale), offset=offset, p_do=p_do)


# Sign it
ctx.set_source_rgb(0.0, 0.0, 0.0)
ctx.select_font_face("Georgia")
ctx.set_font_size(3.)
x_bearing, y_bearing, width, height = ctx.text_extents(sign)[:4]
ctx.move_to(cube_size*0.2, canvas_size[1] - height * 0.5 - cube_size*0.2)
ctx.show_text(sign)

# Render
ctx.show_page()
