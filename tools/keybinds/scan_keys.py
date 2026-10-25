#!/usr/bin/env python3
"""Read vanilla defaults from the real patched client, without launching Minecraft.

Requires a JDK providing javap. The snapshot and mod hashes are reviewed inputs
for the portable preset checks, which themselves need only Python in CI.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def key_name(kind: str, code: int) -> str:
    if code == -1:
        return "key.keyboard.unknown"
    if kind == "MOUSE":
        return "key.mouse." + {0: "left", 1: "right", 2: "middle"}.get(code, str(code + 1))
    if kind != "KEYSYM":
        raise ValueError(f"Unsupported input type: {kind}")
    if 65 <= code <= 90 or 48 <= code <= 57:
        return "key.keyboard." + chr(code).lower()
    if 290 <= code <= 314:
        return f"key.keyboard.f{code - 289}"
    known = {32: "space", 47: "slash", 258: "tab", 340: "left.shift", 341: "left.control"}
    if code not in known:
        raise ValueError(f"Add the verified GLFW key {code} to scan_keys.py")
    return "key.keyboard." + known[code]


def scan(client: Path, javap: str) -> dict:
    output = subprocess.check_output(
        [javap, "-p", "-c", "-classpath", str(client), "net.minecraft.client.Options"], text=True)
    constructors = re.finditer(
        r'new\s+[^\n]+// class net/minecraft/client/(?:KeyMapping|ToggleKeyMapping)\s*\n'
        r'(?P<code>.*?)invokespecial[^\n]+(?:KeyMapping|ToggleKeyMapping)\."<init>"[^\n]+',
        output, re.S)
    mappings = []
    for constructor in constructors:
        code = constructor.group("code")
        match = re.search(r"// String (key\.[^\n]+)", code)
        if not match:
            raise ValueError("A KeyMapping uses a dynamic name; extend the scanner before publishing")
        name = match.group(1).strip()
        tail = code[code.index("// String "):].splitlines()[1:]
        kind, number = "KEYSYM", None
        for line in tail:
            if "InputConstants$Type." in line:
                kind = line.split("InputConstants$Type.")[1].split(":")[0]
            if "InputConstants.UNKNOWN:" in line:
                number = -1
                break
            constant = re.search(r": (?:bipush|sipush)\s+(-?\d+)", line)
            if constant is None:
                constant = re.search(r": iconst_(\d+)", line)
            if constant:
                number = int(constant.group(1))
                break
            if ": iconst_m1" in line:
                number = -1
                break
        if number is None:
            raise ValueError(f"No default key read for {name}")
        category = re.search(r"KeyMapping\$Category\.([^:]+):", code)
        if category is None:
            raise ValueError(f"No category read for {name}")
        mappings.append({"name": name, "default": key_name(kind, number), "category": category.group(1)})
    if not mappings or len({m["name"] for m in mappings}) != len(mappings):
        raise ValueError("Missing or duplicate client mappings")
    mods = {}
    for mod in sorted((REPO / "mods").glob("*.jar")):
        with zipfile.ZipFile(mod) as archive:
            referenced = [name for name in archive.namelist() if name.endswith(".class")
                          and b"net/minecraft/client/KeyMapping" in archive.read(name)]
        for name in referenced:
            bytecode = subprocess.check_output(
                [javap, "-p", "-c", "-classpath", str(mod), name[:-6].replace("/", ".")], text=True)
            if re.search(r'// Method [^\n]*(?:KeyMapping|ToggleKeyMapping)\."<init>"', bytecode):
                raise ValueError(f"{mod.name} constructs KeyMapping in {name}; extend registry scanning")
        mods[mod.name] = hashlib.sha256(mod.read_bytes()).hexdigest()
    return {"minecraftVersion": "26.2", "neoForgeVersion": "26.2.0.84",
            "clientSha256": hashlib.sha256(client.read_bytes()).hexdigest(),
            "modSha256": mods, "mappings": mappings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", required=True, type=Path, help="NeoForge patched Minecraft 26.2 client jar")
    parser.add_argument("--javap", default=shutil.which("javap") or "javap")
    parser.add_argument("--verify", action="store_true", help="compare to snapshot without writing it")
    args = parser.parse_args()
    snapshot = scan(args.client, args.javap)
    target = HERE / "registered-keys.json"
    if args.verify:
        if json.loads(target.read_text(encoding="utf-8")) != snapshot:
            raise SystemExit("Client/mod registry differs; inspect and refresh registered-keys.json")
        print(f"Source verified: {len(snapshot['mappings'])} client mappings, no mod KeyMapping registrations")
    else:
        target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"Wrote {len(snapshot['mappings'])} registered mappings")


if __name__ == "__main__":
    main()
