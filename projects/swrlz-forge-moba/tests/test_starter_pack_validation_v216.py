"""Read-only §E starter pack validator: positive, tampering, and real v10 seed."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import validate_starter_packs as v


def fixture():
    return {"engine":"§wyrl§ Engine · Maker v10.0","version":10,
        "project":{"canonicalId":"new-meadow","template":"sheep-tag-meadow","name":"New Meadow","kind":"sheep-tag"},
        "editor":{"layers":[{"id":"layer-one","name":"Terrain"},{"id":"layer-two","name":"Actors"}]},
        "scene":{"actors":[{"id":"a","editorLayerIds":["layer-one"],"type":"st-meadow"},
                           {"id":"b","editorLayerIds":["layer-two"],"type":"st-sheep"}]}}


class StarterPackValidation(unittest.TestCase):
    def make_pack(self,base):
        s=fixture()
        body=(json.dumps(s,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
        (base/"scenes").mkdir(parents=True)
        (base/"starter-packs").mkdir(parents=True)
        scene=base/"scenes/new-meadow.swyrl.json"
        scene.write_bytes(body)
        descriptor={
            "schema":v.SCHEMA,"id":"new-meadow","status":"draft-unregistered",
            "type":"existing-mode-map-variant",
            "source":{"seed":"sheep-tag-meadow","seedBlob":"a"*40,"engineMainSha":"b"*40,
                      "manifestBlob":"c"*40,"orderedPatchCount":60,"engineVersion":"§wyrl§ Engine v10.0"},
            "scene":{"path":"projects/swrlz-forge-moba/scenes/new-meadow.swyrl.json",
                    "sha256":hashlib.sha256(body).hexdigest(),"bytes":len(body),
                    "actorCount":2,"layerCount":2,"projectKind":"sheep-tag"}
        }
        p=base/"starter-packs/new-meadow.starter.json"
        p.write_text(json.dumps(descriptor,indent=2)+"\n",encoding="utf-8")
        return scene,p,descriptor

    def test_good_pack_is_draft_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            scene,descriptor,_ = self.make_pack(Path(tmp))
            result=v.verify_pack(Path(tmp),"new-meadow")
            self.assertTrue(result["valid"])
            self.assertEqual(result["level"],"draft-pack-source-only")
            self.assertEqual(result["registration"],"NOT REGISTERED")
            self.assertEqual(result["gameplay"],"NOT VERIFIED")
            self.assertEqual(result["actors"],2)

    def test_detects_bytes_and_provenance_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);scene,descriptor,info=self.make_pack(root)
            with scene.open("a",encoding="utf-8") as handle:
                handle.write(" ")
            with self.assertRaisesRegex(v.InvalidPack,"disagree"):
                v.verify_pack(root,"new-meadow")
            scene.write_bytes((json.dumps(fixture(),ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
            info["source"]["manifestBlob"]="not-a-sha"
            descriptor.write_text(json.dumps(info),encoding="utf-8")
            with self.assertRaisesRegex(v.InvalidPack,"Git identity"):
                v.verify_pack(root,"new-meadow")

    def test_rejects_duplicate_ids_and_unknown_layers(self):
        s=fixture()
        s["editor"]["layers"][1]["id"]="layer-one"
        with self.assertRaisesRegex(v.InvalidPack,"Duplicate"):
            v.scene_report(s,"new-meadow")
        s=fixture()
        s["scene"]["actors"][1]["editorLayerIds"]=["missing"]
        with self.assertRaisesRegex(v.InvalidPack,"missing layer"):
            v.scene_report(s,"new-meadow")
        s=fixture()
        s["scene"]["actors"][1]["id"]="a"
        with self.assertRaisesRegex(v.InvalidPack,"Duplicate actor"):
            v.scene_report(s,"new-meadow")

    def test_rejects_paths_and_unregistered_claim_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);scene,descriptor,info=self.make_pack(root)
            info["status"]="active-playable"
            descriptor.write_text(json.dumps(info),encoding="utf-8")
            with self.assertRaisesRegex(v.InvalidPack,"draft existing-mode"):
                v.verify_pack(root,"new-meadow")
        for invalid in ("../main", "a/b","UPPERCASE","a"):
            with self.assertRaises(v.InvalidPack):
                v._slug(invalid)

    def test_current_real_sheep_tag_scene_structure(self):
        actual=v.verify_scene(ROOT,"sheep-tag-meadow")
        self.assertTrue(actual["valid"])
        self.assertEqual(actual["projectKind"],"sheep-tag")
        self.assertEqual(actual["actors"],66)
        self.assertEqual(actual["layers"],4)


if __name__=="__main__":
    unittest.main()
