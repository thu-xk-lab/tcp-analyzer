import numpy as np
import matplotlib.pyplot as plt

import tcpinfo as tcpi


def draw_attr():
    pass


def draw(filename, attr, save=None):
    attr_list = ["time", attr]
    connections = tcpi.retrieve_sample_from_file(filename, save, attr_list)
    dt = np.dtype([("time", float), (attr, int)])

    for conn_id, conn in connections.items():
        data = np.array(conn, dtype=dt)
        plt.plot(data["time"], data[attr])

    plt.show()


if __name__ == '__main__':
    draw("output", "cwnd")
