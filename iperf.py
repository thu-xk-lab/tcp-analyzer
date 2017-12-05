import json
import matplotlib.pyplot as plt
import numpy as np
import sys


class SampleList(object):
    class Sample:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __str__(self):
            return "({}:{})".format(self.x, self.y)

    def __init__(self, seq):
        self.__seq = [self.Sample(x, y) for (x, y) in seq]
        self.__sort()

    @property
    def seq(self):
        return self.__seq

    def __sort(self):
        self.seq.sort(key=lambda s: s.x)

    def __expand(self, x_seq):
        x1 = [s.x for s in self.seq]
        y1 = [s.y for s in self.seq]
        seq = []
        i, j = 0, 0

        while i < len(x1) and j < len(x_seq):
            if x1[i] <= x_seq[j]:
                seq.append((x1[i], y1[i]))
                if x1[i] == x_seq[j]:
                    j += 1
                i += 1
            elif x1[i] > x_seq[j]:
                if not i:
                    seq.append((x_seq[j], 0))
                else:
                    y = y1[i - 1] + (x_seq[j] - x1[i - 1]) \
                        * (y1[i] - y1[i - 1]) / (x1[i] - x1[i - 1])
                    seq.append((x_seq[j], y))
                j += 1

        if i < len(x1):
            seq += zip(x1[i:], y1[i:])

        if j < len(x_seq):
            seq += zip(x_seq[j:], [0] * (len(x_seq) - j))

        return SampleList(seq)

    def __iter__(self):
        for sample in self.seq:
            yield sample

    def __str__(self):
        return "[{}]".format(" ".join([str(s) for s in self.seq]))

    def __add__(self, sl):
        l1 = self.__expand([s.x for s in sl.seq])
        l2 = sl.__expand([s.x for s in self.seq])

        return SampleList([(s1.x, s1.y + s2.y) for (s1, s2) in zip(l1, l2)])

    def to_list(self):
        return [(s.x, s.y) for s in self.seq]


class IperfSample(object):
    def __init__(self, d, start_time=0):
        self._socket = d.get("socket", 0)
        self._start = d.get("start", 0) + start_time
        self._end = d.get("end", 0)
        self._seconds = d.get("seconds", 0)
        self._bytes = d.get("bytes", 0)
        self._bits_per_second = d.get("bits_per_second", 0)
        self._retransmits = d.get("retransmits", 0)
        self._snd_cwnd = d.get("snd_cwnd", 0)
        self._omitted = d.get("omitted", False)

    def __str__(self):
        return " ".join(["{}: {}".format(k, v)
                         for k, v in self.__dict__.items()])

    def __getattr__(self, name):
        return self.__dict__.get("_" + name)


class IperfObject(object):
    def __init__(self, filename, start_time=0):
        self._filename = filename
        self._streams = {}
        self.__load_json()

    def __init_sock(self, sock, flowid):
        if sock not in self.streams.keys():
            self.streams[sock] = {}
            self.streams[sock]["flowid"] = flowid
            self.streams[sock]["samples"] = []

    def __add_sock(self, sock_dict, flowid=None):
        sock = 0

        if not flowid:
            sock = sock_dict["socket"]
            lhost = sock_dict["local_host"]
            lport = sock_dict["local_port"]
            rhost = sock_dict["remote_host"]
            rport = sock_dict["remote_port"]
            flowid = "{}:{}-{}:{}".format(
                lhost, lport, rhost, rport)

        self.__init_sock(sock, flowid)

    def __load_json(self):
        with open(self.filename) as f:
            data = json.load(f)

            self._start_time = data["start"]["timestamp"]["timesecs"]

            for sock in data["start"]["connected"]:
                self.__add_sock(sock)

            self.__add_sock({}, flowid="sum")

            for interval in data["intervals"]:
                for stream in interval["streams"]:
                    self.__add_sock_sample(stream)
                self.__add_sock_sample(interval["sum"])

    def __add_sock_sample(self, stream_dict):
        sock = stream_dict.get("socket", 0)
        sock_sample = IperfSample(stream_dict, self.start_time)

        self.streams[sock]["samples"].append(sock_sample)

    def __getattr__(self, name):
        return self.__dict__.get("_" + name)

    def __get_item(self, sock, name):
        samples = self.streams[sock]["samples"]

        return SampleList([(s.start, getattr(s, name)) for s in samples])

    def to_list(self, sock, name):
        return self.__get_item(sock, name)

    def to_array(self, sock, name, seq=None):
        if not seq:
            seq = self.to_list(sock, name)
        dt = np.dtype([("time", "float"), (name, "float")])

        return np.array(seq.to_list(), dtype=dt)

    def __merge(self, iperf_obj, sock=0, name="bits_per_second"):
        sl1 = self.to_list(sock, name)
        sl2 = iperf_obj.to_list(sock, name)

        return self.to_array(sock, name, seq=sl1 + sl2)

    def merge(self, iperf_obj, sock=0, name="bits_per_second"):
        return self.__merge(iperf_obj, sock, name)

    def __plot_sock(self, sock, name):
        arr = self.to_array(sock, name)
        plt.plot(arr["time"], arr[name], label=sock)

    def plot(self, socks, name):
        for sock in socks:
            self.__plot_sock(sock, name)

#        plt.xlim((0, 60))
#        plt.savefig(self.filename + ".png")


if __name__ == "__main__":
    fname1 = sys.argv[1]
    fname2 = sys.argv[2]
    ipo1 = IperfObject(fname1)
    ipo2 = IperfObject(fname2)

    print([s["flowid"] for s in ipo1.streams.values()])
    print([s["flowid"] for s in ipo2.streams.values()])

    ipo1.plot(ipo1.streams.keys(), "bits_per_second")
    ipo2.plot(ipo2.streams.keys(), "bits_per_second")

    total = ipo1.merge(ipo2)
    plt.plot(total["time"], total["bits_per_second"])
    plt.savefig(fname1 + "-" + fname2 + ".png")
