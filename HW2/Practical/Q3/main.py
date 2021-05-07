import mininet.log
from mininet.link import OVSLink,TCLink
from mininet.node import DefaultController,RemoteController
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import *
from MyTopo import MyTopo
from mininet.node import OVSSwitch

mytopo = MyTopo()
cc = RemoteController(name='c0',ip="127.0.0.1",port=6653)

net = Mininet(topo=mytopo,controller=cc , link=TCLink , build=True , cleanup=True , autoStaticArp=True , switch=OVSSwitch)

setLogLevel("info")

net.start()
CLI(net)
net.stop()
print("Something")