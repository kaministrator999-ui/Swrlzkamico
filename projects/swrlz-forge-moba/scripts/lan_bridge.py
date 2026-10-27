#!/usr/bin/env python3
"""§wyrl§ Engine local LAN lobby discovery bridge (Python 3.10+, stdlib only).

Serve the local packaged §E editor on the LAN. Uses bounded /24 discovery
of *only* other copies of this bridge. Lobby presence is NOT game-state sync.
Never expose this process to the public Internet.
"""
import argparse
import concurrent.futures
import http.server
import ipaddress
import json
import secrets
import socket
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROTOCOL = "swrlz-lan-v1"
QUERY = b"SWYRLZ_LAN_QUERY_V1"
DEFAULT_PORT = 8765
DEFAULT_DISCOVERY_PORT = 8766
MAX_BODY = 4096


def lan_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.0.2.1", 9))  # routing decision only; sends no packets
        ip = sock.getsockname()[0]
        if ipaddress.ip_address(ip).is_private:
            return ip
    except OSError:
        pass
    finally:
        sock.close()
    try:
        for record in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = record[4][0]
            if ipaddress.ip_address(ip).is_private and not ip.startswith("127."):
                return ip
    except OSError:
        pass
    return "127.0.0.1"


def safe_local_ip(value, self_ip):
    try:
        ip = ipaddress.ip_address(value)
        own = ipaddress.ip_address(self_ip)
        # No public addresses and no cross-subnet SSRF.
        return isinstance(ip, ipaddress.IPv4Address) and (
            ip.is_loopback or (ip.is_private and ip in ipaddress.ip_network(str(own) + "/24", strict=False)))
    except (ValueError, TypeError):
        return False


def json_get(host, port, path="/api/lan/status", timeout=.3):
    req = urllib.request.Request(f"http://{host}:{port}{path}", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as reply:
        if reply.status != 200:
            return None
        return json.loads(reply.read(8192).decode("utf-8"))


class LANState:
    def __init__(self, port=DEFAULT_PORT, udp_port=DEFAULT_DISCOVERY_PORT, ip=None):
        self.port, self.udp_port = port, udp_port
        self.ip = ip or lan_ip()
        self.lock = threading.RLock()
        self.game = None
        self.players = {}
        self.remote = {}
        self.last_scan = 0
        self.last_result = []
        self.scan_lock = threading.Lock()

    def snapshot(self, host=None):
        with self.lock:
            if not self.game:
                return None
            now = time.monotonic()
            self.players = {k: v for k, v in self.players.items() if now - v < 45}
            return {
                "id": self.game["id"], "name": self.game["name"],
                "host": host or self.ip, "port": self.port,
                "players": 1 + len(self.players), "self": True,
            }

    def start(self, name="Sheep Tag"):
        clean = str(name).strip()[:60] or "Sheep Tag"
        with self.lock:
            if not self.game:
                self.game = {"id": secrets.token_hex(10), "name": clean}
            return self.snapshot()

    def stop(self):
        with self.lock:
            self.game = None
            self.players.clear()

    def register(self, game_id, player_id):
        with self.lock:
            if not self.game or self.game["id"] != game_id:
                return False
            self.players[str(player_id)[:48]] = time.monotonic()
            return True

    def verify(self, ip, port):
        if not safe_local_ip(ip, self.ip) or not (1 <= int(port) <= 65535):
            return None
        try:
            status = json_get(ip, int(port))
            if not isinstance(status, dict) or status.get("protocol") != PROTOCOL:
                return None
            game = status.get("game")
            if not isinstance(game, dict) or not isinstance(game.get("id"), str):
                return None
            return {"id": game["id"], "name": str(game.get("name", "Sheep Tag"))[:60],
                    "host": ip, "port": int(port), "players": int(game.get("players", 1)),
                    "self": False}
        except (OSError, ValueError, TypeError, urllib.error.URLError, json.JSONDecodeError):
            return None

    def discover_udp(self):
        peers = []
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                probe.bind(("", 0))
                probe.settimeout(.16)
                for address in ["255.255.255.255",
                                str(ipaddress.ip_network(self.ip + "/24", strict=False).broadcast_address)]:
                    try:
                        probe.sendto(QUERY, (address, self.udp_port))
                    except OSError:
                        continue
                until = time.monotonic() + .35
                while time.monotonic() < until:
                    try:
                        payload, (ip, _) = probe.recvfrom(1024)
                        announcement = json.loads(payload.decode("utf-8"))
                        if announcement.get("protocol") == PROTOCOL and safe_local_ip(ip, self.ip):
                            peers.append((ip, int(announcement["port"])))
                    except socket.timeout:
                        break
                    except (OSError, ValueError, KeyError, json.JSONDecodeError):
                        continue
        except OSError:
            pass
        return list(set(peers))

    def directory(self, scan=False):
        now = time.monotonic()
        with self.lock:
            if not scan and now - self.last_scan < 12:
                return list(self.last_result)
        if not self.scan_lock.acquire(blocking=False):
            with self.lock:
                return list(self.last_result)
        try:
            hosts = set(self.discover_udp())
            if scan and self.ip != "127.0.0.1":
                network = ipaddress.ip_network(self.ip + "/24", strict=False)
                hosts.update((str(ip), self.port) for ip in network.hosts() if str(ip) != self.ip)
            results = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=48) as pool:
                for game in pool.map(lambda pair: self.verify(*pair), sorted(hosts)):
                    if game:
                        results[(game["host"], game["port"], game["id"])] = game
            own = self.snapshot()
            if own:
                results[(own["host"], own["port"], own["id"])] = own
            games = sorted(results.values(), key=lambda row: (not row["self"], row["name"], row["host"]))
            with self.lock:
                self.last_result, self.last_scan = games, time.monotonic()
            return games
        finally:
            self.scan_lock.release()


def start_discovery(state, closed):
    def listen():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("", state.udp_port))
                sock.settimeout(.5)
                while not closed.is_set():
                    try:
                        packet, peer = sock.recvfrom(2048)
                        if packet != QUERY or not safe_local_ip(peer[0], state.ip):
                            continue
                        game = state.snapshot()
                        if game:
                            response = json.dumps({"protocol": PROTOCOL, "port": state.port,
                                                   "id": game["id"]}).encode("utf-8")
                            sock.sendto(response, peer)
                    except socket.timeout:
                        continue
                    except OSError:
                        continue
        except OSError as ex:
            print("UDP discovery unavailable:", ex, flush=True)
    thread = threading.Thread(target=listen, daemon=True, name="sheep-lan-udp")
    thread.start()
    return thread


def make_handler(state, static_root):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(static_root), **kwargs)

        def reply(self, status, result):
            raw = json.dumps({"protocol": PROTOCOL, **result}).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def peer_admin(self):
            peer = self.client_address[0]
            return peer in ("127.0.0.1", "::1", state.ip)

        def origin_ok(self):
            origin = self.headers.get("Origin")
            if not origin:
                return True   # local CLI/bridge-to-bridge requests
            parsed = urllib.parse.urlsplit(origin)
            return (parsed.scheme == "http" and parsed.hostname == self.headers.get("Host", "").split(":")[0]
                    and parsed.port in (state.port, None))

        def body(self):
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > MAX_BODY:
                raise ValueError("Invalid JSON body size")
            result = json.loads(self.rfile.read(size).decode("utf-8"))
            if not isinstance(result, dict):
                raise ValueError("Expected JSON object")
            return result

        def do_GET(self):
            parsed = urllib.parse.urlsplit(self.path)
            if parsed.path == "/api/lan/status":
                self.reply(200, {"available": True, "ip": state.ip,
                                 "canHost": self.peer_admin(), "game": state.snapshot()})
                return
            if parsed.path == "/api/lan/games":
                force = urllib.parse.parse_qs(parsed.query).get("scan", [""])[0] == "1"
                self.reply(200, {"games": state.directory(scan=force)})
                return
            if parsed.path.startswith("/api/"):
                self.reply(404, {"error": "Unknown LAN API"})
                return
            if parsed.path == "/":
                self.path = "/index.html"
            return super().do_GET()

        def do_POST(self):
            if not self.origin_ok():
                self.reply(403, {"error": "Cross-origin LAN writes are forbidden"})
                return
            parsed = urllib.parse.urlsplit(self.path)
            try:
                if parsed.path == "/api/lan/host":
                    if not self.peer_admin():
                        self.reply(403, {"error": "Only the device running the bridge may host"})
                        return
                    self.reply(200, {"game": state.start(self.body().get("name", "Sheep Tag"))})
                    return
                if parsed.path == "/api/lan/register":
                    body = self.body()
                    if state.register(str(body.get("gameId", "")), str(body.get("playerId", ""))):
                        self.reply(200, {"joined": True})
                    else:
                        self.reply(404, {"error": "Lobby is unavailable"})
                    return
                if parsed.path == "/api/lan/join":
                    body = self.body()
                    host, port = body.get("host"), int(body.get("port", state.port))
                    game_id = str(body.get("gameId", ""))
                    found = state.verify(host, port)
                    if not found or found["id"] != game_id:
                        self.reply(404, {"error": "Host no longer advertises this lobby"})
                        return
                    player = secrets.token_hex(12)
                    request = urllib.request.Request(
                        f"http://{host}:{port}/api/lan/register",
                        json.dumps({"gameId": game_id, "playerId": player}).encode("utf-8"),
                        {"Content-Type": "application/json"}, method="POST")
                    with urllib.request.urlopen(request, timeout=1.5) as reply:
                        if reply.status != 200:
                            raise ValueError("Lobby registration failed")
                    self.reply(200, {"joined": True,
                                     "message": "Joined LAN lobby; synchronized matches are not implemented yet."})
                    return
                self.reply(404, {"error": "Unknown LAN API"})
            except (ValueError, TypeError, KeyError, OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
                self.reply(400, {"error": str(exc)[:160]})

        def do_DELETE(self):
            if not self.origin_ok() or not self.peer_admin():
                self.reply(403, {"error": "Only the local bridge owner can stop hosting"})
                return
            if urllib.parse.urlsplit(self.path).path == "/api/lan/host":
                state.stop()
                self.reply(200, {"hosting": False})
            else:
                self.reply(404, {"error": "Unknown LAN API"})

        def log_message(self, fmt, *args):
            print("[%s] %s" % (self.address_string(), fmt % args), flush=True)
    return Handler


def main():
    parser = argparse.ArgumentParser(description="Local Wi-Fi Sheep Tag lobby discovery, not multiplayer netcode")
    parser.add_argument("--serve", type=Path, required=True, help="Built §E dist folder containing index.html")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--udp-port", type=int, default=DEFAULT_DISCOVERY_PORT)
    args = parser.parse_args()
    root = args.serve.expanduser().resolve()
    if not (root / "index.html").is_file():
        parser.error("Build §E first: --serve must contain index.html")
    state = LANState(port=args.port, udp_port=args.udp_port)
    closed = threading.Event()
    listener = start_discovery(state, closed)
    http = http.server.ThreadingHTTPServer(("0.0.0.0", args.port), make_handler(state, root))
    http.daemon_threads = True
    print("§E LAN Bridge:", f"http://{state.ip}:{args.port}/", flush=True)
    print("Use on private Wi-Fi only. UDP", args.udp_port,
          "for discovery. No synchronized multiplayer yet.", flush=True)
    try:
        http.serve_forever(poll_interval=.25)
    except KeyboardInterrupt:
        pass
    finally:
        closed.set()
        http.shutdown()
        http.server_close()
        listener.join(timeout=1)


if __name__ == "__main__":
    main()
