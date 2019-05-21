
import random
import time

import numpy as np
import moderngl as mg
from PyQt5 import QtWidgets


W, H = 512, 512


class Renderer(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super(Renderer, self).__init__()
        self.setMinimumSize(W, H)
        self.setMaximumSize(W, H)

    def shader(self, path, **karg):
        context = None
        with open(path, 'r') as fp:
            context = fp.read()

        for k, v in karg.items():
            context = context.replace(k, str(v))

        return context

    def reset_fract_buffer(self):
        self.data[:, :, :] = 0.0

        self.points = []
        for i in range(3):
            self.points.append(
                np.array([random.random(), random.random()])
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
        self.data = np.zeros((W, H, 4)).astype(np.float32)
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
        STEPS = 300
        self.steps += STEPS
        for i in range(STEPS):
            p = random.choice(self.points)
            self.cursor = (self.cursor + p) / 2.0
            x, y = self.cursor[0], self.cursor[1]
            x, y = int(x * W), int(y * H)

            r = random.random() * 0.45
            g = random.random() * 0.25
            b = random.random() * 0.15
            self.data[x, y] += (r, g, b, 1.0)

        self.buffer_1.write(self.data)
        self.buffer_1.bind_to_storage_buffer(1)

        if self.steps > 50000:
            self.steps = 0
            self.reset_fract_buffer()

        if self.u_time:
            self.u_time.value = time.time() % 1000
        self.draw_cs.run(self.gx, self.gy)

        self.vao.render()
        self.update()


def main():
    app = QtWidgets.QApplication([])
    renderer = Renderer()
    renderer.show()
    app.exec()


if __name__ == "__main__":
    main()
