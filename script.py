import matplotlib.pyplot as plt
import argparse


import TCPAnalyzer.tcpinfo as tcpi


def ax_draw(ax, data, x, y, label):
    for attr in to_list(y):
        ax.plot(data[x], data[attr], label=label)
    ax.legend()


def to_list(e):
    return e if isinstance(e, list) else [e]


def draw(filename, x, y1, y2=None):
    attr_list = []
    attr_list.extend(to_list(x))
    attr_list.extend(to_list(y1))
    y2 and attr_list.extend(to_list(y2))

    connections = tcpi.tcpi_conn_set(filename)
    datas = connections.get_attrs(attr_list)

    fig, ax1 = plt.subplots()
    if y2:
        ax2 = ax1.twinx()

    for id, data in datas.items():
        ax_draw(ax1, data, x, y1, id)
        y2 and ax_draw(ax2, data, x, y2, id)

    plt.savefig(filename + ".png")
#    plt.show()


def parse_command():
    parser = argparse.ArgumentParser()

    parser.add_argument("filename", help="Source file name.")
    parser.add_argument("-1", "--master-y-vars",
                        nargs="+", default="cwnd", metavar="Y1",
                        help="List of preferred variables.")
    parser.add_argument("-2", "--secondary-y-vars",
                        nargs="+", metavar="Y2",
                        help="List of secondary preferred variables.")
    parser.add_argument("-x", "--x-var",
                        default="time", metavar="X",
                        help="Variable of X axis (Default: Time).")

    args = parser.parse_args()

    print("Filename: {}".format(args.filename))
    print("X-axis: {}".format(args.x_var))
    print("Y-axis: {}".format(args.master_y_vars))
    if args.secondary_y_vars:
        print("Secondary Y axis enabled. ({})".format(args.secondary_y_vars))

    return args


if __name__ == "__main__":
    args = parse_command()

    filename = args.filename
    connections = tcpi.tcpi_conn_set(filename)
    draw(filename, args.x_var, args.master_y_vars, args.secondary_y_vars)
