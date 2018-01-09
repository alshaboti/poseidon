# Poseidon with Faucet
This example shows how can you run Poseidon with Faucet controller. 
Motivated by Charlie blog [here](https://blog.cyberreboot.org/building-a-software-defined-network-with-raspberry-pis-and-a-zodiac-fx-switch-97184032cdc1),
this is example show detailed technical steps that I learned when I followed Charlie's blog. 
## Setup demo environment 
![alt text](./Poseidon_Faucet.png "Demo setup architecture")
## Hardware
- One OF-switch (in my case ovs on TP-Link router) 
- Three raspberry Pis (one will run Faucet controller, and two will run as hosts)
- One Host (PC, laptop) to run as Poseidon server. 
## Settings
Connect these devices as shown in the figure above.
### Faucet PI
- Install [Docker CE](https://docs.docker.com/engine/installation/linux/docker-ce/debian/) 
- Pull and run faucet container
```
docker pull faucet/faucet-pi
docker run -d \
    --name faucet \
    -v /etc/ryu/faucet/:/etc/ryu/faucet/ \
    -v /var/log/ryu/faucet/:/var/log/ryu/faucet/ \
    -p 6653:6653 \
    -p 9302:9302 \
    faucet/faucet-pi
```
- Enable ssh on Faucet PI as in [here](https://www.raspberrypi.org/documentation/remote-access/ssh/). Give pi user permission to change faucet.yaml and log files, such that Poseidon can edit these files later. 
```
sudo chmod auo+w /etc/ryu/faucet/faucet.yaml
sudo chmod -R auo+w /var/log/ryu/faucet/
```
- Configuring network interfaces of Faucet Pi. Edit file interfaces (/etc/network/interfaces) as:
```
auto eth0
iface eth0 inet static
    address 192.168.1.100
    
auto eth1
iface eth1 inet static
    address 192.168.3.1
```
- Configure /etc/ryu/faucet/faucet.yaml
Change dp_id (switch MAC without colons), and hardware values to match your case. 
```
vlans:
  demo:
    vid: 300
  mirror:
    vid: 101
    max_hosts: 0
dps:
  openwrt:
    dp_id: 0x14cc20be86aa
    hardware: "Open vSwitch"
    proactive_learn: true
    interfaces:
      1:
        native_vlan: demo
      2:
        native_vlan: demo
      3:
        native_vlan: mirror
```
## Poseidon server
- Install [Docker CE](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
- Configure server interface for ssh connectionto faucet 
```
auto eth1
iface eth1 inet static
    address 192.168.3.2
```
You should be able to ssh to faucet host.
```
ssh pi@192.168.3.1
```
- Clone model.pickle file to /tmp/models/
```
mkdir /tmp/models/
cp model.pickle /tmp/models/
```
- Clone poseidon, then set its environment variables then run. 
```
git clone https://github.com/alshaboti/poseidon
cd poseidon
export controller_uri=192.168.3.1
export controller_user=pi
export controller_pass=myPassword
export controller_type=faucet
export collector_nic=eth1
export controller_mirror_ports='{"openwrt":3}'
export max_concurrent_reinvestigations=1
./helpers/run
```
Once vent is running, you can see log events. 
```
docker logs -f cyberreboot-vent-syslog-master
```
## PI Clients 
- Configure PI 1 network interface as
```
auto eth1
iface eth1 inet static
    address 192.168.2.1
```

- Configure PI 2 network interface as
```
auto eth1
iface eth1 inet static
    address 192.168.2.2
```
## Test
Try to make aggressive pinging between Pis and see how Poseidon detects and block the connection. 
