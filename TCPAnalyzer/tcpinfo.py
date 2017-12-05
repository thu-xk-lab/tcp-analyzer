import os
import numpy as np


class tcpi_ipaddr(object):
    """Class for IP address"""
    TBL_PORT = {"ssh": 22, "http": 80}

    def get_port(self, port):
        return int(port) if self.port.isdigit() \
            else self.TBL_PORT.get(port, -1)

    def __init__(self, line):
        self.ip, self.port = line.split(":")
        self.port = self.get_port(self.port)

    def __str__(self):
        return "%s:%s" % (self.ip, self.port)


class tcpi_stat(object):
    """Class for connection state."""

    def __init__(self, line):
        words = line.split()

        self.state = words[0]
        self.rcvq = words[1]
        self.sndq = words[2]
        self.laddr = tcpi_ipaddr(words[3])
        self.raddr = tcpi_ipaddr(words[4])

    def __str__(self):
        return "%s %s %s %s %s" % (
            self.state,
            self.rcvq,
            self.sndq,
            self.laddr,
            self.raddr
        )

    @property
    def conn_id(self):
        return "%s-%s" % (self.laddr, self.raddr)


class tcpi_dctcp_sample(object):
    def __init__(self, line):
        pass

    def __str__(self):
        return "dctcp_sample"


class tcpi_bbr_sample(object):
    def __init__(self, line):
        words = line[1:-1].split(",")

        for word in words:
            if word.startswith("bw"):
                self.bbr_bw = word.split(":")[1][:-3]
            if word.startswith("mrtt"):
                self.bbr_min_rtt = word.split(":")[1]
            if word.startswith("pacing_gain"):
                self.bbr_pacing_gain = word.split(":")[1]
            if word.startswith("cwnd_gain"):
                self.bbr_cwnd_gain = word.split(":")[1]

    def __str__(self):
        return "%s %s %s %s" % (
            self.bbr_bw, self.bbr_min_rtt, self.bbr_pacing_gain,
            self.bbr_cwnd_gain
        )


class tcpi_pacing_rate_sample(object):
    def __init__(self, line):
        pass

    def __str__(self):
        return "pacing_rate_sample"


class tcpi_sample(object):
    """Class for each sample"""
    # Default list for printing
    DEFAULT_ATTR_LIST = ["time", "cong", "cwnd", "srtt"]

    attr_type = {
        "time": float,
        "cwnd": int,
        "srtt": float,
        "lbbr_bw_bps": float,
        "lbbr_mrtt_ms": float,
        "lbbr_ssthresh": int,
        "lbbr_target_cwnd": int,
    }

    def __init__(self, line, attr_list=None):
        self.base_init()

        words = line.split()
        for word in words:
            self.en_tc = True if "tc" == word else False
            self.en_sack = True if "sack" == word else False
            self.en_ecn = True if "ecn" == word else False
            self.ecnseen = True if "ecnseen" == word else False
            self.en_fastopen = True if "fastopen" == word else False
            self.bidir = True if "bidir" == word else False
            self.app_limited = True if "app_limited" == word else False

            if word.startswith("time:"):
                self.time = float(word.split(":")[1])

            if word.startswith("cong:"):
                self.cong = word.split(":")[1]
            if word.startswith("wscale:"):
                self.snd_wscale, self.rcv_wscale \
                    = [int(w) for w in word.split(":")[1].split(",")]
            if "rto" in word:
                self.rto = float(word.split(":")[1])
            if "backoff" in word:
                self.backoff = int(word.split(":")[1])
            if "rtt" == word[:3]:
                self.srtt, self.rttvar \
                    = [float(w) for w in word.split(":")[1].split("/")]
            if "ato" in word:
                self.ato = float(word.split(":")[1])
            if "qack" in word:
                self.qack = int(word.split(":")[1])

            if "mss" in word:
                self.mss = int(word.split(":")[1])
            if "rcvmss" in word:
                self.rcvmss = int(word.split(":")[1])
            if "advmss" in word:
                self.advmss = int(word.split(":")[1])
            if "cwnd" == word[:4]:
                self.cwnd = int(word.split(":")[1])
            if word.startswith("ssthresh:"):
                self.ssthresh = int(word.split(":")[1])

            if "bytes_acked" in word:
                self.bytes_acked = int(word.split(":")[1])
            if "bytes_received" in word:
                self.bytes_received = int(word.split(":")[1])
            if "segs_out" in word:
                self.segs_out = int(word.split(":")[1])
            if "segs_in" in word:
                self.segs_in = int(word.split(":")[1])
            if "data_segs_out" in word:
                self.data_segs_out = int(word.split(":")[1])
            if "data_segs_in" in word:
                self.data_segs_in = int(word.split(":")[1])

            if "dctcp:" in word:
                self.dctcp = tcpi_dctcp_sample(word.split(":")[1])

            if word.startswith("bbr:"):
                self.bbr = tcpi_bbr_sample(word.split(":")[1])

            if word.startswith("lbbr:"):
                self.get_lbbr_info(word.split(":", 1)[1])

            if "send" in word:
                send_bps = word.split(":")[1][:-3]
                self.send_bps, self.send_bps_unit \
                    = float(send_bps[:-1]), send_bps[-1]

            if "lastsnd" in word:
                self.lastsnd = int(word.split(":")[1])
            if "lastrcv" in word:
                self.lastrcv = int(word.split(":")[1])
            if "lastack" in word:
                self.lastack = int(word.split(":")[1])

            if "pacing_rate" in word:
                self.pacing_rate = tcpi_pacing_rate_sample(word.split(":")[1])

            if "delivery_rate" in word:
                delivery_rate_bps = word.split(":")[1][:-3]
                self.delivery_rate_bps, self.delivery_rate_bps_unit \
                    = float(delivery_rate_bps[:-1]), delivery_rate_bps[-1]

            if "busy" in word:
                self.busy_time_ms = int(word.split(":")[1][:-2])
            if "rwnd_limited" in word:
                self.rwnd_limited_ms \
                    = int(word.split(":")[1].split("(")[0][-2])
            if "sndbuf_limited" in word:
                self.sndbuf_limited_ms \
                    = int(word.split(":")[1].split("(")[0][-2])

            if "unacked" in word:
                self.unacked = int(word.split(":")[1])
            if "retrans" in word:
                retrans = word.split(":")[1]
                self.retrans, self.retrans_total = [
                    int(w) for w in retrans.split("/")]
            if "lost" in word:
                self.lost = int(word.split(":")[1])
            if "sacked" in word:
                self.sacked = int(word.split(":")[1])
            if "fackets" in word:
                self.fackets = int(word.split(":")[1])
            if "reordering" in word:
                self.reordering = int(word.split(":")[1])
            if "rcv_rtt" in word:
                self.rcv_rtt = float(word.split(":")[1])
            if "rcv_space" in word:
                self.rcv_space = int(word.split(":")[1])
            if "notsent" in word:
                self.notsend = int(word.split(":")[1])
            if "minrtt" in word:
                self.min_rtt = float(word.split(":")[1])

        self.set_attr_list(attr_list)

    def __str__(self):
        if not self.attr_list:
            self.set_attr_list(self.DEFAULT_ATTR_LIST)
        return " ".join(str(attr) for attr in self.get_attrs())

    def base_init(self):
        self.state = ""
        self.rcvq = 0
        self.sndq = 0

    def get_send_rate(self, line):
        if line[-1] == "K":
            return float(line[:-1]) * 1000
        elif line[-1] == "M":
            return float(line[:-1]) * 1000000
        else:
            return float(line)

    def get_lbbr_info(self, line):
        words = line[1:-1].split(",")

        for word in words:
            if word.startswith("bw"):
                self.lbbr_bw_bps = self.get_lbbr_info(word.split(":")[1][:-3])
            if word.startswith("mrtt"):
                self.lbbr_mrtt_ms = float(word.split(":")[1])
            if word.startswith("ssthresh"):
                self.lbbr_ssthresh = int(word.split(":")[1])
            if word.startswith("target_cwnd"):
                self.lbbr_target_cwnd = int(word.split(":")[1])

    def set_attr_list(self, attr_list):
        self.attr_list = attr_list

    def get_attrs(self, attr_list):
        return tuple([getattr(self, attr, -1)
                      for attr in attr_list])

    @classmethod
    def get_types(cls, attr_list):
        return np.dtype([(attr, cls.attr_type[attr])
                         for attr in attr_list])


class tcpi_connection(object):
    def __init__(self):
        self.flow_id = ""
        self.samples = []
        self.attr_list = []

    def add_sample(self, base, detail):
        if self.flow_id == "":
            self.flow_id = base.conn_id

        if self.flow_id != base.conn_id:
            print("Incorrect flow-id: <%s> not equals to <%s>" % (
                self.flow_id, base.conn_id
            ))
            raise

        detail.state = base.state
        detail.rcvq = base.rcvq
        detail.sndq = base.sndq

        self.samples.append(detail)

    def get_attrs(self, attr_list):
        dt = tcpi_sample.get_types(attr_list)

        return np.array([s.get_attrs(attr_list)
                         for s in self.samples],
                        dtype=dt)


class tcpi_conn_set(object):
    def __init__(self, filename=None):
        self.conns = {}
        self.attr_list = []

        if filename:
            self.build_conns_by_file(filename)

    def add_sample(self, base, detail):
        flow_id = base.conn_id

        if flow_id not in self.conns.keys():
            self.conns[flow_id] = tcpi_connection()
        self.conns[flow_id].add_sample(base, detail)

    def build_conns_by_file(self, filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError

        with open(filename) as f:
            for idx, line in enumerate(f):
                if idx % 2 == 0:
                    base = tcpi_stat(line)
                    continue
                detail = tcpi_sample(line)
                self.add_sample(base, detail)

    def get_attrs(self, attr_list):
        ret = {}

        for id, conn in self.conns.items():
            ret[id] = conn.get_attrs(attr_list)

        return ret


def retrieve_data_from_file(fin, attr_list):
    connections = tcpi_conn_set(fin)
    ret = connections.get_attrs(attr_list)

    return ret


if __name__ == '__main__':
    filename = "output"

    conns = retrieve_data_from_file(filename, True, ["time", "cwnd"])
