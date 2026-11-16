"""No live account or model: stop-control concurrency tests."""
from __future__ import annotations
import threading
import time
import unittest
from unittest.mock import patch
from scripts import stop_transport_v1 as st

class FakeSocket:
    def __init__(self):
        self.closed=threading.Event()
    def shutdown(self,how):
        self.closed.set()

class FakeConnection:
    instances=[]
    def __init__(self,host,port,timeout):
        self.sock=FakeSocket()
        self.connected=False
        self.closed=False
        self.host=host
        self.port=port
        FakeConnection.instances.append(self)
    def connect(self):
        self.connected=True
    def request(self,method,path,body,headers):
        self.path=path
        self.body=body
    def getresponse(self):
        return type("FakeResponse",(),{"status":200})()
    def close(self):
        self.closed=True

class StopTransportTests(unittest.TestCase):
    def setUp(self):
        FakeConnection.instances=[]

    def test_registered_request_can_interrupt_its_own_socket(self):
        scope=st.bind_generation_cancel("own-id",lambda:False)
        try:
            with patch.object(st.http.client,"HTTPConnection",FakeConnection):
                with st.completion_response({"messages":[]},16947,
                        lambda *a,**k:None):
                    self.assertEqual(FakeConnection.instances[0].host,"127.0.0.1")
                    self.assertFalse(st.cancel_active_request("other-id"))
                    self.assertFalse(FakeConnection.instances[0].sock.closed.is_set())
                    self.assertTrue(st.cancel_active_request("own-id"))
                    self.assertTrue(FakeConnection.instances[0].sock.closed.is_set())
                    self.assertTrue(st.generation_cancelled())
            self.assertTrue(FakeConnection.instances[0].closed)
        finally:
            st.release_generation_cancel("own-id")

    def test_stop_before_completion_network_admission(self):
        st.bind_generation_cancel("before",lambda:False)
        try:
            self.assertTrue(st.cancel_active_request("before"))
            with self.assertRaises(InterruptedError):
                with st.completion_response({"messages":[]},16947,None):
                    pass
        finally:
            st.release_generation_cancel("before")

    def test_generation_checker_prevents_decode_start(self):
        st.bind_generation_cancel("checker",lambda:True)
        try:
            self.assertTrue(st.generation_cancelled())
            with self.assertRaises(InterruptedError):
                with st.completion_response({"messages":[]},16947,None):
                    pass
        finally:
            st.release_generation_cancel("checker")

    def test_unbound_request_uses_original_http_adapter(self):
        class Context:
            def __enter__(self):return "old"
            def __exit__(self,*a):return None
        seen=[]
        def post(path,payload,timeout=0):
            seen.append((path,payload,timeout))
            return Context()
        with st.completion_response({"prompt":"sample"},16947,post,timeout=7) as value:
            self.assertEqual(value,"old")
        self.assertEqual(seen,[("/v1/chat/completions",{"prompt":"sample"},7)])

    def test_two_sessions_never_interrupt_each_other(self):
        barrier=threading.Barrier(3)
        results={}
        def worker(rid):
            st.bind_generation_cancel(rid,lambda:False)
            try:
                with patch.object(st.http.client,"HTTPConnection",FakeConnection):
                    with st.completion_response({"request":rid},16947,None):
                        results[rid]=st._scope().conn
                        barrier.wait(timeout=3)
                        barrier.wait(timeout=3)
            finally:
                st.release_generation_cancel(rid)
        ta=threading.Thread(target=worker,args=("A",))
        tb=threading.Thread(target=worker,args=("B",))
        ta.start();tb.start()
        try:
            barrier.wait(timeout=3)
            self.assertTrue(st.cancel_active_request("A"))
            self.assertFalse(results["B"].sock.closed.is_set())
            barrier.wait(timeout=3)
        finally:
            ta.join(timeout=3);tb.join(timeout=3)
        self.assertFalse(ta.is_alive());self.assertFalse(tb.is_alive())
        self.assertTrue(results["A"].sock.closed.is_set())
        self.assertFalse(results["B"].sock.closed.is_set())

if __name__=="__main__":
    unittest.main()
