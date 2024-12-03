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

def SwapLinesList(lst, i, j):
    tmp = lst[i].color
    lst[i].color = lst[j].color
    lst[j].color = tmp

    tmp = lst[i].transformed_a
    lst[i].transformed_a = lst[j].transformed_a
    lst[j].transformed_a = tmp

    tmp = lst[i].transformed_b
    lst[i].transformed_b = lst[j].transformed_b
    lst[j].transformed_b = tmp


class Line:
    def __init__(self, canvas, point_a, point_b):
        self.point_a = point_a
        self.point_b = point_b

        self.draw_line = canvas.create_line(0, 0, 0, 0, fill="black", width=4)
        self.color = 0

    def update(self, canvas, screen, perspective, view):
        new_point_a = (perspective @ view @ self.point_a)
        new_point_b = (perspective @ view @ self.point_b)

        self.color = int((((new_point_a[3][0] + new_point_b[3][0]) / 10) ** 4) * 0.5 * 255)

        if self.color < 0:
            self.color = 0
        elif self.color > 255:
            self.color = 255

        new_point_a = screen @ ApplyProjection(new_point_a)
        new_point_b = screen @ ApplyProjection(new_point_b)

        self.transformed_a = new_point_a
        self.transformed_b = new_point_b

        #canvas.itemconfig(self.draw_line, fill=color_format)
        #canvas.coords(self.draw_line, new_point_a[0][0], new_point_a[1][0], new_point_b[0][0], new_point_b[1][0])

    def render(self, canvas):
        color_format = f'#{self.color:02x}{self.color:02x}{self.color:02x}'

        canvas.itemconfig(self.draw_line, fill=color_format)
        canvas.coords(self.draw_line, self.transformed_a[0][0], self.transformed_a[1][0], self.transformed_b[0][0], self.transformed_b[1][0])


class App:
    def __init__(self, root):
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Tetraedro", command=self.buildTetrahedron)
        filemenu.add_command(label="Cubo", command=self.buildCube)
        filemenu.add_command(label="Octaedro", command=self.buildOctahedron)
        filemenu.add_command(label="Icosaedro", command=self.buildIcosahedron)
        menubar.add_cascade(label="Visualizar", menu=filemenu)
        root.config(menu=menubar)

        scale_y = tk.Scale(root, from_=0, to=100, orient="vertical", command=self.update_angle_x, showvalue=False)
        scale_y.pack(side="right", fill="y")

        self.width = 1280
        self.height = 720
        self.delta_ms = 16
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack(fill="both", side="top", expand=True)
        self.canvas.bind("<Configure>", self.resize_canvas)
        self.running = True
        self.current_time = 0
        self.angle_x = math.pi
        self.angle_y = math.pi

        scale_x = tk.Scale(root, from_=0, to=100, orient="horizontal", command=self.update_angle_y, showvalue=False)
        scale_x.pack(side="bottom", fill="x")

        self.points = []
        self.lines = []
        self.buildCube()

        self.screen_matrix = Transform(self.width / 2, self.height / 2, 0) @ Scale(self.width / 2, self.height / 2, 0)
        self.perspective_matrix = Perspective(math.pi / 3, self.width / self.height, 1.00, 100.0)

        self.start()

    def update_angle_x(self, value):
        self.angle_x = math.pi -float(value) / 100 * math.pi

    def update_angle_y(self, value):
        self.angle_y = math.pi -float(value) / 100 * 2 * math.pi

    def update(self):
        if not self.running:
            return

        model_matrix = Transform(0, 0, -5.0) @ RotateX(self.angle_x) @ RotateY(self.angle_y)

        for i in self.lines:
            i.update(self.canvas, self.screen_matrix, self.perspective_matrix, model_matrix)

        self.sort_lines()

        for i in self.lines:
            i.render(self.canvas)

        self.current_time += 0.001 * self.delta_ms
        self.canvas.after(self.delta_ms, self.update)

    def sort_lines(self):
        for i in range(len(self.lines)):
            for j in range(0, len(self.lines) - i - 1):
                if self.lines[j].color < self.lines[j + 1].color:
                    SwapLinesList(self.lines, j, j + 1)

    def buildCube(self):
        self.canvas.delete("all")
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
        self.canvas.delete("all")
        self.points = [Vec4(0.5, 0.0, -0.35, 1.0), Vec4(-0.5, 0.0, -0.35, 1.0), Vec4(0.0, 0.5, 0.35, 1.0), Vec4(0.0, -0.5, 0.35, 1.0)]
        self.lines = []

        for i in range(len(self.points)):
            self.points[i] *= 1.7
            self.points[i][3][0] = 1.0

        for i in self.points:
            for j in self.points:
                if not np.array_equal(i, j):
                    self.lines.append(Line(self.canvas, i, j))

    def buildOctahedron(self):
        self.canvas.delete("all")
        self.points = [Vec3(1.0, 0.0, 0.0), Vec3(0.0, 1.0, 0.0), Vec3(-1.0, 0.0, 0.0), Vec3(0.0, -1.0, 0.0), Vec3(0.0, 0.0, 1.0), Vec3(0.0, 0.0, -1.0)]
        self.lines = []

        for i in range(4):
            self.lines.append(Line(self.canvas, self.points[i], self.points[(i + 1) % 4]))
            self.lines.append(Line(self.canvas, self.points[i], self.points[4]))
            self.lines.append(Line(self.canvas, self.points[i], self.points[5]))

    def buildIcosahedron(self):
        self.canvas.delete("all")
        self.points = [
                Vec3(0.000000, -0.525731, 0.850651),
                Vec3(0.850651, 0.000000, 0.525731),
                Vec3(0.850651, 0.000000, -0.525731),
                Vec3(-0.850651, 0.000000, -0.525731),
                Vec3(-0.850651, 0.000000, 0.525731),
                Vec3(-0.525731, 0.850651, 0.000000),
                Vec3(0.525731, 0.850651, 0.000000),
                Vec3(0.525731, -0.850651, 0.000000),
                Vec3(-0.525731, -0.850651, 0.000000),
                Vec3(0.000000, -0.525731, -0.850651),
                Vec3(0.000000, 0.525731, -0.850651),
                Vec3(0.000000, 0.525731, 0.850651)
                ]

        self.lines = []

        self.lines.append(Line(self.canvas, self.points[1], self.points[2]))
        self.lines.append(Line(self.canvas, self.points[1], self.points[7]))
        self.lines.append(Line(self.canvas, self.points[3], self.points[4]))
        self.lines.append(Line(self.canvas, self.points[4], self.points[3]))
        self.lines.append(Line(self.canvas, self.points[6], self.points[5]))
        self.lines.append(Line(self.canvas, self.points[5], self.points[6]))
        self.lines.append(Line(self.canvas, self.points[9], self.points[10]))
        self.lines.append(Line(self.canvas, self.points[10], self.points[9]))
        self.lines.append(Line(self.canvas, self.points[7], self.points[8]))
        self.lines.append(Line(self.canvas, self.points[8], self.points[7]))
        self.lines.append(Line(self.canvas, self.points[11], self.points[0]))
        self.lines.append(Line(self.canvas, self.points[0], self.points[11]))
        self.lines.append(Line(self.canvas, self.points[6], self.points[2]))
        self.lines.append(Line(self.canvas, self.points[1], self.points[6]))
        self.lines.append(Line(self.canvas, self.points[3], self.points[5]))
        self.lines.append(Line(self.canvas, self.points[5], self.points[4]))
        self.lines.append(Line(self.canvas, self.points[2], self.points[7]))
        self.lines.append(Line(self.canvas, self.points[7], self.points[1]))
        self.lines.append(Line(self.canvas, self.points[3], self.points[9]))
        self.lines.append(Line(self.canvas, self.points[4], self.points[8]))
        self.lines.append(Line(self.canvas, self.points[2], self.points[6]))
        self.lines.append(Line(self.canvas, self.points[7], self.points[2]))
        self.lines.append(Line(self.canvas, self.points[4], self.points[5]))
        self.lines.append(Line(self.canvas, self.points[3], self.points[8]))
        self.lines.append(Line(self.canvas, self.points[5], self.points[11]))
        self.lines.append(Line(self.canvas, self.points[6], self.points[10]))
        self.lines.append(Line(self.canvas, self.points[10], self.points[2]))
        self.lines.append(Line(self.canvas, self.points[9], self.points[3]))
        self.lines.append(Line(self.canvas, self.points[8], self.points[9]))
        self.lines.append(Line(self.canvas, self.points[7], self.points[0]))
        self.lines.append(Line(self.canvas, self.points[0], self.points[1]))
        self.lines.append(Line(self.canvas, self.points[11], self.points[4]))
        self.lines.append(Line(self.canvas, self.points[2], self.points[10]))
        self.lines.append(Line(self.canvas, self.points[6], self.points[11]))
        self.lines.append(Line(self.canvas, self.points[5], self.points[10]))
        self.lines.append(Line(self.canvas, self.points[4], self.points[11]))
        self.lines.append(Line(self.canvas, self.points[7], self.points[9]))
        self.lines.append(Line(self.canvas, self.points[1], self.points[0]))
        self.lines.append(Line(self.canvas, self.points[9], self.points[8]))
        self.lines.append(Line(self.canvas, self.points[8], self.points[0]))
        self.lines.append(Line(self.canvas, self.points[6], self.points[1]))
        self.lines.append(Line(self.canvas, self.points[2], self.points[1]))
        self.lines.append(Line(self.canvas, self.points[5], self.points[3]))
        self.lines.append(Line(self.canvas, self.points[8], self.points[4]))
        self.lines.append(Line(self.canvas, self.points[11], self.points[6]))
        self.lines.append(Line(self.canvas, self.points[10], self.points[5]))
        self.lines.append(Line(self.canvas, self.points[2], self.points[9]))
        self.lines.append(Line(self.canvas, self.points[3], self.points[10]))
        self.lines.append(Line(self.canvas, self.points[9], self.points[7]))
        self.lines.append(Line(self.canvas, self.points[0], self.points[8]))
        self.lines.append(Line(self.canvas, self.points[1], self.points[11]))
        self.lines.append(Line(self.canvas, self.points[4], self.points[0]))
        self.lines.append(Line(self.canvas, self.points[10], self.points[6]))
        self.lines.append(Line(self.canvas, self.points[11], self.points[1]))
        self.lines.append(Line(self.canvas, self.points[10], self.points[3]))
        self.lines.append(Line(self.canvas, self.points[11], self.points[5]))
        self.lines.append(Line(self.canvas, self.points[9], self.points[2]))
        self.lines.append(Line(self.canvas, self.points[0], self.points[7]))
        self.lines.append(Line(self.canvas, self.points[8], self.points[3]))
        self.lines.append(Line(self.canvas, self.points[0], self.points[4]))

    def resize_canvas(self, event):
        self.width = event.width
        self.height = event.height
        self.perspective_matrix = Perspective(math.pi / 3, self.width / self.height, 1.00, 100.0)
        self.screen_matrix = Transform(self.width / 2, self.height / 2, 0) @ Scale(self.width / 2, self.height / 2, 0)
        #self.canvas.delete("all")

    def start(self):
        self.update()

def main():
    root = tk.Tk()
    root.title("Visualizador de Sólidos de Platão")
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()

