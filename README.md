# Server Switch

A simple network switch using standards Python libraries.

## Prerequisites

Minimum requirement: Python
```zsh
sudo apt install python
```

Tested with:
- Python 2.7.17
- Python 3.7.5

## Usage

Start listening on localhost for connection on port 1234:
```zsh
python server_switch.py
```

Power-on two VM using QMU and an Alpine Standard ISO:
```zsh
qemu-system-x86_64 -m 512M -enable-kvm -net nic macaddr=14:c6:11:d6:f1:6b,netdev=net0 -netdev socket,id=net0,connect=127.0.0.1:1234 -cdrom alpine-standard-3.10.2-x86_64.iso -vga cirrus -curses
```
```zsh
qemu-system-x86_64 -m 512M -enable-kvm -net nic macaddr=14:c6:11:d6:f1:5b,netdev=net0 -netdev socket,id=net0,connect=127.0.0.1:1234 -cdrom alpine-standard-3.10.2-x86_64.iso -vga cirrus -curses
```

Set-up each network interface on the same LAN:
```zsh
ip addr add 192.168.1.1/24 dev eth0
ip link set eth0 up
```
```zsh
ip addr add 192.168.1.2/24 dev eth0
ip link set eth0 up
```

Ping each others:
```zsh
ping 192.168.1.2
```
```zsh
ping 192.168.1.1
```

## Authors

* **[x1n5h3n](https://github.com/x1n5h3n)**

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.


