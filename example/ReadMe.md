# Poseidon with Faucet
This example shows how can you run Poseidon with Faucet controller. 
Motivated by Charlie blog [here](https://blog.cyberreboot.org/building-a-software-defined-network-with-raspberry-pis-and-a-zodiac-fx-switch-97184032cdc1),
this is example show detailed technical steps that I learned when I followed Charlie's blog. 
## Setup demo environment 
![alt text](./Poseidon_Faucet.png "Demo setup architecture")
## Prerequisites 
### Hardware
- One OF-switch (in my case ovs on TP-Link router) 
- Three raspberry Pis (one will run Faucet controller, and two will run as hosts)
- One Host (PC, laptop) to run as Poseidon server. 
## Software 
### Faucet PI
- Install [Docker CE](https://docs.docker.com/engine/installation/linux/docker-ce/debian/) 
- Build and run faucet container
```
git clone https://github.com/faucetsdn/faucet
cd faucet
FAUCET_CONFIG_STAT_RELOAD=1 docker-compose -f docker-compose-pi.yaml up --build -d
```
