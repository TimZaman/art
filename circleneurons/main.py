import cv2
import numpy as np
import time


def radius_to_circle_pts(pts_on_circle, radius):
    # Distributed the points over normalized interval [0:1)
    lengths = np.arange(pts_on_circle).astype(np.float32) / pts_on_circle * 2 * np.pi
    x = np.cos(lengths)
    y = np.sin(lengths)
    pts = np.stack((x, y), 1)
    return pts * radius


def draw_pts(img, pts, color):
    for pt in pts:
        img = cv2.circle(img, tuple(pt), radius=2, color=color, lineType=cv2.LINE_AA)


def main():
    n_fixed_pts = 512
    pts_on_circle = 36
    width, height = 2000, 1000
    radius_step_size = 4
    n_steps = 256
    line_thickness = 1

    start_radius = (max(width, height) * 1.0) // 2


    fixed_pts = np.random.random((n_fixed_pts, 2))
    fixed_pts = (fixed_pts * (width, height)).astype(np.float32)
    # print(fixed_pts)

    for i in range(n_steps):
        # Create a fresh canvas
        img = np.zeros((height, width, 3), np.uint8)

        # Create a circle with points on it
        circle_pts = radius_to_circle_pts(pts_on_circle=pts_on_circle,
                                          radius=start_radius - radius_step_size * i)

        # Move to center
        circle_pts += (width//2, height//2)

        # draw_pts(img, pts=circle_pts, color=(10, 50, 50))

        # Draw lines between each of the circle points and the fixed points if they are within some
        # distance. Sadly, the python cv2 bindings require us to do this one by one.

        for circle_pt in circle_pts:
            d = np.sqrt( (fixed_pts[:,0] - circle_pt[0]) ** 2 + (fixed_pts[:, 1] - circle_pt[1]) ** 2)
            for pt_i, d in enumerate(d):
                c = max(255 - d * 1.5, 0)
                if c:
                    img = cv2.line(img, tuple(circle_pt), tuple(fixed_pts[pt_i]), (c, c, c), line_thickness, lineType=cv2.LINE_AA)

        # Show the points for debugging
        draw_pts(img, pts=fixed_pts, color=(50, 50, 50))

        cv2.imshow('image', img)
        cv2.waitKey(1)
        cv2.imwrite(f'out/{i:03d}.png', img)

    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
