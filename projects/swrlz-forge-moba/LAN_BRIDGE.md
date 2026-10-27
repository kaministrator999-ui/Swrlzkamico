# §wyrl§ Engine · Local LAN Bridge (v11.148)

The Sheep Tag **Main Menu → Local LAN** screen has **Host Game**, a real local-game directory, **Refresh**, and **Back**.

## Important capability boundary

The public Hugging Face version uses HTTPS and cannot enumerate local Wi-Fi IP addresses, listen for UDP advertisements or accept inbound game connections. Its LAN screen therefore displays a truthful “local bridge required” state and does not fake nearby matches. The **LAN Bridge** is a separate Python standard-library service running on a trusted device on the same local Wi-Fi network. Run a copy on each hosting device. It serves the real engine source and assets over the private LAN, advertises hosting status with UDP 8766 and scans one local /24 subnet for copies of this exact bridge on TCP 8765. The browser calls its **same-origin** API.

## Launch

From repository root:

```bash
python projects/swrlz-forge-moba/build_space.py --output dist/swrlz-forge-moba
python projects/swrlz-forge-moba/scripts/lan_bridge.py --serve dist/swrlz-forge-moba
```

Open the URL printed by the bridge, for example `http://192.168.1.5:8765/`, on a device connected to the **same private Wi-Fi**. (For Android, a local Python environment such as Termux can run the service; hosting needs a process that can accept incoming LAN connections.) Run the bridge on another device to advertise an additional lobby, then refresh the browser. The mobile browser cannot itself turn into an HTTP or UDP LAN server.

**Host Game** registers one real lobby on the device running that bridge; **Stop Hosting** removes it. **Refresh** uses UDP discovery and bounded IP probing; the list contains only positively verified running §E bridge hosts. **Join Lobby** registers presence on a host but **does not** synchronize Sheep Tag game state, players, physics or commands. That authoritative gameplay network layer requires a separate multiplayer implementation before these become playable networked matches. No outside cloud service, paid API or fictional LAN IP is used.

## Security / operating scope

Private LAN only. No port forwarding. Do not run on untrusted/public Wi-Fi. LAN host/stop APIs reject writes from remote clients, and cross-origin browser writes are rejected. The HTTP service serves only its packaged `--serve` folder. Local IP probes are restricted to the bridge's IPv4 /24 network, using a fixed port and a small timeout; scanning only runs on manual refresh, with UDP/discovery cached between refreshes. Network/firewall restrictions may prevent discovery. The bridge is not authenticated multiplayer infrastructure; it is a private Wi-Fi development service.

## v11.148 waiting-room behavior

Host Game opens the eight-slot room; the host permanently occupies seat 1. A joining guest gets a server-assigned seat, is visible to connected visitors and departs on Leave or after 45 seconds without heartbeat. Only the hosting bridge device can stop hosting. Start Match remains disabled until gameplay synchronization exists. Never internet-forward TCP 8765 or UDP 8766.
