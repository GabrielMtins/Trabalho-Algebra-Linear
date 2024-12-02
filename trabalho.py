import tkinter as tk
import numpy as np
import math

def Perspective(fov, aspect, near, far):
    f = 1 / np.tan((fov) / 2)
    a1 = -(far + near) / (far - near)
    a2 = -2.0 * far * near / (far - near)

    return np.array([
        [f / aspect, 0,  0,                             0],
        [0,          f,  0,                             0],
        [0,          0,  a1,                           a2],
        [0,          0, -1.0,                             0]
    ])

def Transform(x, y, z):
    return np.array([
        [1.0, 0, 0, x],
        [0, 1.0, 0, y],
        [0, 0, 1.0, z],
        [0, 0, 0, 1.0]
    ])

def Scale(x, y, z):
    return np.array([
        [x, 0, 0, 1.0],
        [0, y, 0, 1.0],
        [0, 0, z, 1.0],
        [0, 0, 0, 1.0]
        ])

def RotateX(angle):
    return np.array([
        [1.0, 0, 0, 0.0],
        [0, np.cos(angle), -np.sin(angle), 0.0],
        [0, np.sin(angle), np.cos(angle), 0.0],
        [0, 0, 0, 1],
        ])

def RotateY(angle):
    return np.array([
        [np.cos(angle), 0, np.sin(angle), 0],
        [0, 1, 0, 0],
        [-np.sin(angle), 0, np.cos(angle), 0],
        [0, 0, 0, 1]
        ])

def Vec4(x, y, z, w):
    return np.array([[x],[y],[z],[w]])

def Vec3(x, y, z):
    return Vec4(x, y, z, 1.0)

def ApplyProjection(arr):
    x = arr[0][0]
    y = arr[1][0]
    z = arr[2][0]
    w = arr[3][0]
    return np.array([[x / w], [y / w], [z / w], [1.0]])

class Line:
    def __init__(self, canvas, point_a, point_b):
        self.point_a = point_a
        self.point_b = point_b
        self.draw_line = canvas.create_line(0, 0, 0, 0, fill="black", width=2)

    def update(self, canvas, screen, perspective, view):
        new_point_a = screen @ ApplyProjection(perspective @ view @ self.point_a)
        new_point_b = screen @ ApplyProjection(perspective @ view @ self.point_b)

        canvas.coords(self.draw_line, new_point_a[0][0], new_point_a[1][0], new_point_b[0][0], new_point_b[1][0])


class App:
    def __init__(self, root):
        self.width = 1280
        self.height = 720
        self.delta_ms = 16
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()
        self.running = True
        self.current_time = 0
        
        self.points = []
        self.lines = []
        self.buildCube()

        self.screen_matrix = Transform(self.width / 2, self.height / 2, 0) @ Scale(self.width / 2, self.height / 2, 0)
        self.perspective_matrix = Perspective(math.pi / 3, self.width / self.height, 1.00, 100.0)

        self.start()

    def update(self):
        if not self.running:
            return

        for i in self.lines:
            i.update(self.canvas, self.screen_matrix, self.perspective_matrix, Transform(0, 0, -5.0) @ RotateX(self.current_time) @ RotateY(self.current_time))

        self.current_time += 0.001 * self.delta_ms
        self.canvas.after(self.delta_ms, self.update)

    def buildCube(self):
        self.points = [
                Vec3(-0.5, -0.5, -0.5), Vec3(+0.5, -0.5, -0.5), Vec3(+0.5, +0.5, -0.5), Vec3(-0.5, +0.5, -0.5),
                Vec3(-0.5, -0.5, +0.5), Vec3(+0.5, -0.5, +0.5), Vec3(+0.5, +0.5, +0.5), Vec3(-0.5, +0.5, +0.5)
                ]
        self.lines = []

        for i in list(range(4)):
            self.lines.append(Line(self.canvas, self.points[i], self.points[(i + 1) % 4]))
            self.lines.append(Line(self.canvas, self.points[i + 4], self.points[(i + 1) % 4 + 4]))
            self.lines.append(Line(self.canvas, self.points[i], self.points[i + 4]))

    def buildTetrahedron(self):
        self.points = [Vec4(0.5, 0.0, -0.35, 1.0), Vec4(-0.5, 0.0, -0.35, 1.0), Vec4(0.0, 0.5, 0.35, 1.0), Vec4(0.0, -0.5, 0.35, 1.0)]

        for i in self.points:
            for j in self.points:
                if not np.array_equal(i, j):
                    self.lines.append(Line(self.canvas, i, j))


    def start(self):
        self.update()

root = tk.Tk()
app = App(root)
root.mainloop()

