"""§E v11.148: authoritative lobby seat/host/guest regression."""
import json,sys,tempfile,threading,time,unittest,urllib.request,urllib.error
from pathlib import Path
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from lan_bridge import LANState,MAX_SLOTS,make_handler

class Slots(unittest.TestCase):
    def test_host_owns_first_seat(self):
        state=LANState(ip="127.0.0.1")
        game=state.start("Sheep Tag")
        self.assertEqual(MAX_SLOTS,8)
        self.assertEqual(game["slots"][0]["role"],"host")
        self.assertEqual(game["players"],1)
        self.assertEqual(game["phase"],"waiting")
        self.assertFalse(game["canStartMatch"])
        for seat in range(2,MAX_SLOTS+1):
            self.assertTrue(state.register(game["id"],"guest-token-%02d"%seat,"Guest %d"%seat))
        full=state.snapshot()
        self.assertEqual(full["players"],8)
        self.assertEqual(len(full["slots"]),8)
        self.assertFalse(state.register(game["id"],"guest-token-99","No seat"))
        self.assertTrue(state.register(game["id"],"guest-token-02","Guest 2"))
        self.assertEqual(state.snapshot()["players"],8)
        self.assertTrue(state.leave(game["id"],"guest-token-04"))
        self.assertTrue(state.register(game["id"],"guest-token-09","Replacement"))
        self.assertEqual(state.snapshot()["slots"][3]["name"],"Replacement")
        self.assertTrue(state.pulse(game["id"],"guest-token-09"))
        self.assertFalse(state.pulse(game["id"],"wrong"))
        state.stop()
        self.assertIsNone(state.snapshot())

    def test_http_host_room_join_leave(self):
        with tempfile.TemporaryDirectory() as path:
            Path(path,"index.html").write_text("engine",encoding="utf8")
            state=LANState(ip="127.0.0.1")
            server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(state,Path(path)))
            state.port=server.server_address[1]
            worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
            url="http://127.0.0.1:%d"%state.port
            def get(p):
                with urllib.request.urlopen(url+p,timeout=2) as r:return json.loads(r.read())
            def post(p,body):
                req=urllib.request.Request(url+p,json.dumps(body).encode(),
                      {"Content-Type":"application/json"},method="POST")
                with urllib.request.urlopen(req,timeout=2) as r:return json.loads(r.read())
            try:
                game=post("/api/lan/host",{"name":"Moonbell"})["game"]
                room=get("/api/lan/lobby")
                self.assertEqual(room["game"]["slots"][0]["role"],"host")
                user=post("/api/lan/join",{"host":"127.0.0.1","port":state.port,
                          "gameId":game["id"],"name":"Clover"})
                token=user["playerId"]
                self.assertEqual(len(token),32)
                roster=get("/api/lan/lobby")["game"]
                self.assertEqual(roster["players"],2)
                self.assertEqual(roster["slots"][1]["name"],"Clover")
                ident={"gameId":game["id"],"playerId":token}
                self.assertTrue(post("/api/lan/pulse",ident)["ok"])
                self.assertTrue(post("/api/lan/leave",ident)["ok"])
                self.assertEqual(get("/api/lan/lobby")["game"]["players"],1)
                existing=post("/api/lan/host",{"name":"Replaced?"})["game"]
                self.assertEqual(existing["id"],game["id"])
                self.assertEqual(existing["name"],"Moonbell")
            finally:
                server.shutdown();server.server_close();worker.join(timeout=2)

if __name__=="__main__":unittest.main(verbosity=2)
