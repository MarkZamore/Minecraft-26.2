import json
import unittest
from pathlib import Path

import check_preset


class PresetValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((check_preset.HERE / "registered-keys.json").read_text(encoding="utf-8"))
        cls.allowances = json.loads((check_preset.HERE / "allowed-conflicts.json").read_text(encoding="utf-8"))["pairs"]
        cls.mappings = check_preset.parse((check_preset.REPO / "launcher/controls-preset.txt").read_text(encoding="utf-8"))

    def test_complete_vanilla_layout_passes(self):
        overlaps, problems = check_preset.validate(self.mappings, self.registry, self.allowances)
        self.assertEqual([], problems)
        self.assertEqual(len(self.allowances), overlaps)
        self.assertEqual(61, len(self.mappings))

    def test_duplicate_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            check_preset.parse("key_key.jump:key.keyboard.space\nkey_key.jump:key.keyboard.a")

    def test_unreviewed_modifier_is_rejected(self):
        with self.assertRaises(ValueError):
            check_preset.parse("key_key.jump:key.keyboard.a:SHIFT")

    def test_missing_registration_is_rejected(self):
        mappings = dict(self.mappings)
        del mappings["key_key.jump"]
        self.assertTrue(any("Missing registered" in p for p in check_preset.validate(mappings, self.registry, self.allowances)[1]))

    def test_new_collision_does_not_inherit_vanilla_allowance(self):
        mappings = dict(self.mappings)
        mappings["key_key.jump"] = "key.keyboard.w"
        self.assertTrue(any("Unreviewed conflict" in p for p in check_preset.validate(mappings, self.registry, self.allowances)[1]))

    def test_changed_pair_key_does_not_inherit_vanilla_allowance(self):
        mappings = dict(self.mappings)
        mappings["key_key.debug.overlay"] = "key.keyboard.f10"
        mappings["key_key.debug.modifier"] = "key.keyboard.f10"
        problems = check_preset.validate(mappings, self.registry, self.allowances)[1]
        self.assertTrue(any("Unreviewed conflict" in p for p in problems))
        self.assertTrue(any("Stale conflict" in p for p in problems))

    def test_unregistered_mapping_is_rejected(self):
        mappings = dict(self.mappings)
        mappings["key_missing.mod.action"] = "key.keyboard.unknown"
        self.assertTrue(any("Unregistered" in p for p in check_preset.validate(mappings, self.registry, self.allowances)[1]))


if __name__ == "__main__":
    unittest.main()
