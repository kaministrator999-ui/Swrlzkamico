"""Tests for reusing the existing encrypted account-bound GitHub OAuth record."""
from __future__ import annotations
import json
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

from cryptography.fernet import Fernet
from fastapi import HTTPException
sys.path.insert(0, str(Path(__file__).resolve().parent))
import github_oauth_reuse_v257 as bridge
import github_sandbox_create_txt as sandbox


class OAuthReuseTest(unittest.TestCase):
    def setUp(self):
        self.user={"id":"google:owner"}
        self.settings={
            "client":"id","secret":"secret",
            "callback":"https://kamiloki-swyrlz.hf.space/api/github/callback",
            "fernet":Fernet.generate_key().decode("ascii"),
            "redis":"https://redis.invalid","redis_token":"secret",
        }
        self.db={}
        def fake_redis(_cfg,*args):
            op=args[0]
            if op=="SET":
                self.db[args[1]]=args[2]
                return "OK"
            if op=="GET":
                return self.db.get(args[1])
            if op=="GETDEL":
                return self.db.pop(args[1],None)
            if op=="DEL":
                self.db.pop(args[1],None)
                return 1
            return None
        self.patches=[
            patch.object(bridge,"_settings",return_value=self.settings),
            patch.object(bridge,"_redis",side_effect=fake_redis),
        ]
        for p in self.patches:p.start()

    def tearDown(self):
        for p in reversed(self.patches):p.stop()

    def save_record(self,scopes="read:user",login="kaministrator999-ui",repo=bridge.TARGET):
        bridge._save(bridge._config(),self.user["id"],{
            "token":"existing-encrypted-oauth-token",
            "githubId":12345,"login":login,"repo":repo,"scopes":scopes,
        })

    def test_existing_account_record_key_and_encryption_compatibility(self):
        self.save_record()
        item=bridge._load(bridge._config(),self.user["id"])
        self.assertEqual(item["token"],"existing-encrypted-oauth-token")
        self.assertNotIn("existing-encrypted-oauth-token",str(self.db))
        self.assertEqual(bridge._record_key(self.user["id"]), "swrlz:github:account:" + __import__("hashlib").sha256(self.user["id"].encode()).hexdigest())

    def test_read_only_grant_requires_explicit_oauth_upgrade(self):
        self.save_record()
        state=bridge._write_state(bridge._load(bridge._config(),self.user["id"]))
        self.assertFalse(state["allowed"])
        self.assertEqual(state["reason"],"GITHUB_WRITE_SCOPE_REQUIRED")
        self.assertEqual(state["authorizeUrl"],"/api/github/start?access=public-write")
        with self.assertRaises(HTTPException) as e:
            bridge.authorize_sandbox_write(self.user)
        self.assertEqual(e.exception.status_code,403)

    def test_granted_write_scope_plus_push_role_reuses_token(self):
        self.save_record(scopes="read:user public_repo")
        with patch.object(bridge,"_api",return_value={
            "full_name":bridge.TARGET,"private":False,
            "permissions":{"push":True},
        }):
            self.assertEqual(bridge.authorize_sandbox_write(self.user),
                             "existing-encrypted-oauth-token")
            self.assertEqual(sandbox._authorized(self.user),
                             "existing-encrypted-oauth-token")

    def test_repo_selection_owner_and_role_cannot_be_bypassed(self):
        for repo,login,scopes,permissions in (
            ("other/repo","kaministrator999-ui","read:user public_repo",{"push":True}),
            (bridge.TARGET,"other-owner","read:user public_repo",{"push":True}),
            (bridge.TARGET,"kaministrator999-ui","read:user",{"push":True}),
            (bridge.TARGET,"kaministrator999-ui","read:user public_repo",{"pull":True}),
        ):
            with self.subTest(repo=repo,login=login,scopes=scopes,permissions=permissions):
                self.save_record(scopes=scopes,login=login,repo=repo)
                with patch.object(bridge,"_api",return_value={
                    "full_name":bridge.TARGET,"private":False,
                    "permissions":permissions,
                }):
                    self.assertFalse(bridge._write_state(bridge._load(bridge._config(),self.user["id"]))["allowed"])
        with self.assertRaises(HTTPException):
            bridge.authorize_sandbox_write({"id":"google:someone-else"})

    def test_no_authorization_without_existing_account_connection(self):
        with self.assertRaises(HTTPException) as error:
            bridge.authorize_sandbox_write(self.user)
        self.assertEqual(error.exception.status_code,403)
        self.assertEqual(error.exception.detail,"GITHUB_NOT_CONNECTED")

    def test_no_recovery_with_missing_oauth_storage_configuration(self):
        self.settings["fernet"]=""
        with self.assertRaises(HTTPException) as error:
            bridge.authorize_sandbox_write(self.user)
        self.assertEqual(error.exception.status_code,503)

if __name__=="__main__":
    unittest.main()
