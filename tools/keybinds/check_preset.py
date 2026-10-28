#!/usr/bin/env python3
"""Check complete pinned-client controls and only documented vanilla overlaps.

Identical physical keys are reported even for vanilla debug chords and spectator actions.
The exact default pairs below are retained, never general per-key exemptions.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
UNKNOWN = "key.keyboard.unknown"
KNOWN_KEYS = {"key.keyboard." + chr(code).lower() for code in [*range(65, 91), *range(48, 58)]}
KNOWN_KEYS |= {f"key.keyboard.f{number}" for number in range(1, 26)}
KNOWN_KEYS |= {"key.keyboard." + key for key in ["space", "slash", "tab", "left.shift", "left.control", "unknown"]}
KNOWN_KEYS |= {"key.mouse." + key for key in ["left", "right", "middle", "4", "5", "6", "7", "8"]}
LINE = re.compile(r"^(key_[^:]+):(key\.(?:keyboard|mouse)\.[a-z0-9.]+)$")


def parse(text: str) -> dict[str, str]:
    mappings = {}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.split("  #", 1)[0].strip()
        if not line or line.startswith("#"):
            continue
        match = LINE.fullmatch(line)
        if not match:
            raise ValueError(f"Line {number}: expected key_<name>:<key>, without unreviewed modifiers")
        name, key = match.groups()
        if name in mappings:
            raise ValueError(f"Line {number}: duplicate mapping {name}")
        if key not in KNOWN_KEYS:
            raise ValueError(f"Line {number}: unknown input key {key}")
        mappings[name] = key
    return mappings


def validate(mappings: dict[str, str], registry: dict, allowances: list[dict]) -> tuple[int, list[str]]:
    expected = {"key_" + row["name"] for row in registry["mappings"]}
    problems = []
    if expected - mappings.keys():
        problems.append(f"Missing registered mappings: {sorted(expected - mappings.keys())}")
    if mappings.keys() - expected:
        problems.append(f"Unregistered mappings: {sorted(mappings.keys() - expected)}")
    allowed = {}
    for entry in allowances:
        pair = frozenset(entry["mappings"])
        if len(pair) != 2 or pair in allowed or not entry.get("reason"):
            problems.append(f"Invalid or duplicate conflict allowance: {entry}")
        allowed[pair] = entry["key"]
    actual = {}
    for (a, key), (b, other) in itertools.combinations(mappings.items(), 2):
        if key != UNKNOWN and key == other:
            actual[frozenset([a, b])] = key
    for pair, key in actual.items():
        if allowed.get(pair) != key:
            problems.append(f"Unreviewed conflict on {key}: {sorted(pair)}")
    for pair, key in allowed.items():
        if actual.get(pair) != key:
            problems.append(f"Stale conflict allowance on {key}: {sorted(pair)}")
    return len(actual), problems


def main() -> None:
    registry = json.loads((HERE / "registered-keys.json").read_text(encoding="utf-8"))
    allowances = json.loads((HERE / "allowed-conflicts.json").read_text(encoding="utf-8"))["pairs"]
    mappings = parse((REPO / "launcher/controls-preset.txt").read_text(encoding="utf-8"))
    overlaps, problems = validate(mappings, registry, allowances)
    descriptor = json.loads((REPO / "portable-pack.json").read_text(encoding="utf-8"))
    if descriptor["minecraftVersion"] != registry["minecraftVersion"] or descriptor["loader"] != {"type": "neoforge", "version": registry["neoForgeVersion"]}:
        problems.append("Minecraft/loader version changed; re-scan the actual named client")
    current_mods = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (REPO / "mods").glob("*.jar")}
    if current_mods != registry["modSha256"]:
        problems.append("Mod jars changed; re-run scan_keys.py and review new key registrations")
    print(f"{len(mappings)} mappings, {sum(v != UNKNOWN for v in mappings.values())} bound, "
          f"{overlaps} documented vanilla overlaps")
    if problems:
        raise SystemExit("\n".join(problems))
    print("Preset is complete; no unreviewed conflicts")


if __name__ == "__main__":
    main()
