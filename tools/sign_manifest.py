#!/usr/bin/env python3
"""Sign manifest.json with the offline SmartStart P-256 private key."""

import argparse
import base64
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
def canonical(manifest: dict) -> bytes:
    return (
        "SMARTSTART-OTA-V1\n"
        f"{manifest['schema']}\n{manifest['product']}\n{manifest['target']}\n"
        f"{manifest['hardware']}\n{manifest['channel']}\n{manifest['sequence']}\n"
        f"{manifest['version']}\n{manifest['url']}\n{manifest['size']}\n"
        f"{manifest['image_sha256']}\n{manifest['file_sha256']}\n"
    ).encode("utf-8")


parser = argparse.ArgumentParser()
parser.add_argument("private_key", type=Path,
                    help="P-256 private PEM key kept outside the repository")
parser.add_argument("manifest", type=Path, nargs="?", default=ROOT / "manifest.json",
                    help="manifest to sign (default: repository manifest.json)")
args = parser.parse_args()
if not args.private_key.is_file():
    raise SystemExit("Private signing key not found")
manifest_path = args.manifest.resolve()
if not manifest_path.is_file():
    raise SystemExit(f"Manifest not found: {manifest_path}")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["signed_manifest"] = True
with tempfile.NamedTemporaryFile() as signature_file:
    subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(args.private_key),
         "-out", signature_file.name],
        input=canonical(manifest),
        check=True,
    )
    signature_file.seek(0)
    manifest["signature"] = base64.b64encode(signature_file.read()).decode("ascii")

manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
print(f"Signed {manifest['version']} sequence {manifest['sequence']}")
