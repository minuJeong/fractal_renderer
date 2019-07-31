"""
compute shader does nothing but simply push CPU written buffer into GPU rendering buffer.
used QOpenGLWidget from PyQt5 package
requires glsl #version 460

author: minu jeong
"""

import random
import time

import numpy as np
import moderngl as mg
from PyQt5 import QtWidgets
from PyQt5 import QtCore


W, H = 512, 512


class Renderer(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Renderer, self).__init__()
        self.setFixedSize(W, H)

    def shader(self, path, **karg):
        context = None
        with open(path, 'r') as fp:
            context = fp.read()

        for k, v in karg.items():
            context = context.replace(k, str(v))

        return context

    def reset_fract_buffer(self):
        self.data = np.zeros((W, H, 4)).astype(np.float32)
        self.points = []
        for i in range(3):
            self.points.append(
                np.array([random.random(), random.random()]).astype(np.float32)
            )
        self.cursor = self.points[0]

    def initializeGL(self):
        gl = mg.create_context()

        program = gl.program(
            vertex_shader=self.shader("./gl/vs.glsl"),
            fragment_shader=self.shader("./gl/fs.glsl"))

        vbo = [
            -1.0, -1.0, 0.0,
            +1.0, -1.0, 0.0,
            -1.0, +1.0, 0.0,
            +1.0, +1.0, 0.0,
        ]
        vbo = np.asarray(vbo).astype(np.float32)
        vbo = [(
            gl.buffer(vbo), "3f", "in_pos"
        )]

        ibo = [0, 1, 2, 1, 2, 3]
        ibo = np.asarray(ibo).astype(np.int32)
        ibo = gl.buffer(ibo)

        self.vao = gl.vertex_array(program, vbo, ibo)

        FULL_BUFFER_SIZE = W * H * 4 * 4

        self.buffer_0 = gl.buffer(reserve=FULL_BUFFER_SIZE)
        self.buffer_0.bind_to_storage_buffer(0)

        self.buffer_1 = gl.buffer(reserve=FULL_BUFFER_SIZE)
        self.reset_fract_buffer()

        self.draw_cs = gl.compute_shader(self.shader("./gl/cs.glsl"))
        if "u_width" in self.draw_cs:
            self.draw_cs["u_width"].value = W

        self.u_time = None
        if "u_time" in self.draw_cs:
            self.u_time = self.draw_cs["u_time"]

        if "u_width" in program:
            program["u_width"].value = W

        if "u_height" in program:
            program["u_height"].value = H

        self.gx, self.gy = int(W / 8), int(H / 8)
        self.steps = 0

    def paintGL(self):
        STEPS = 175
        MAX_STEPS = 80000
        self.steps += STEPS
        for i in range(STEPS):
            if i % 3 != 0:
                continue

            c = self.cursor
            p = random.choice(self.points)
            x = (c[0] + p[0]) * 0.5
            y = (c[1] + p[1]) * 0.5
            self.cursor = np.array([x, y]).astype(np.float32)
            x, y = self.cursor[0], self.cursor[1]
            x, y = int(round(x * W)), int(round(y * H))

            r = 0.65
            g = 0.25
            b = 0.15
            self.data[x, y] += (r, g, b, 1.0)

        self.buffer_1.write(self.data)
        self.buffer_1.bind_to_storage_buffer(1)

        if self.steps > MAX_STEPS:
            self.steps = 0
            self.reset_fract_buffer()
            print(["{:.2f}, {:.2f}".format(p[0], p[1]) for p in self.points])

        if self.u_time:
            self.u_time.value = time.time() % 1000
        self.draw_cs.run(self.gx, self.gy)

        self.vao.render()
        self.update()

    def keyPressEvent(self, e):
        key = e.key()
        if key == QtCore.Qt.Key_Space:
            self.steps = 0
            self.reset_fract_buffer()
            print(["{:.2f}, {:.2f}".format(p[0], p[1]) for p in self.points])


def main():
    app = QtWidgets.QApplication([])
    renderer = Renderer()
    renderer.show()
    app.exec()


if __name__ == "__main__":
    main()
