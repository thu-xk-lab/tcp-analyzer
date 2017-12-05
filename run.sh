#!/bin/bash

cong=$1
starttime=$(date +%y.%m.%d.%H.%M.%S)
ss_fname=$starttime.$cong.out
ipf1_fname=$starttime.$cong.1.json
ipf2_fname=$starttime.$cong.2.json

start () {
    watch -t -n 0.5 \
	  ss -tiH dst :5200 or dst :5201 or dst :5202 \
	  or dst :5203 or dst :5204 or dst :5205 \
	  or dst :5206 or dst :5207 or dst :5208 \
	  or dst :5209 or dst :5210 >> $ss_fname

}

start &
id=$!

iperf3 -c 192.168.0.165 -p 5200 -t 60 -C $cong -i 0.5 -J > $ipf1_fname &

sleep 17

iperf3 -c 192.168.0.165 -p 5201 -t 30 -C $cong -i 0.5 -J > $ipf2_fname &

while [[ -n $(pgrep iperf3) ]]; do
    :
done

kill $id

python3 script.py $ss_fname
python3 iperf.py $ipf1_fname $ipf2_fname

