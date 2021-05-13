import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import json

indices = []
rtt = []
congestion = []
throughput_KbitPerS = []
with open("result.json") as json_file:
    data= json.load(json_file)

    intervals = data["intervals"]



    for i in range(len(intervals)):
        indices.append(i)
        stream = intervals[i]['streams'][0]
        rtt.append(stream['rtt'])
        congestion.append(stream['snd_cwnd'])
        throughput_KbitPerS.append(stream['bits_per_second']/1024.0)


f1 =plt.figure()
plt.title("RTT")
plt.ylabel("RTT")
plt.xlabel("Packet#")
plt.plot(indices,rtt)

f2 =plt.figure()
plt.title("Congestion Window")
plt.ylabel("Congestion Window")
plt.xlabel("Packet#")
plt.plot(indices,congestion)


f3 =plt.figure()
plt.title("Throughput")
plt.ylabel("Throughput (kb/s)")
plt.xlabel("Packet#")
plt.plot(indices,throughput_KbitPerS)


pdf = PdfPages('plots.pdf')
pdf.savefig(f1)
pdf.savefig(f2)
pdf.savefig(f3)
pdf.close()