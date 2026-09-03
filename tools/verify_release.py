#!/usr/bin/env python3
"""Validate the static SmartStart OTA release before publishing it."""

import hashlib
import json
import base64
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
PUBLIC_PREFIX = "https://ota.greenier.dk/"


def fail(message: str) -> None:
    raise SystemExit(f"OTA validation failed: {message}")


manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
required = {
    "schema", "product", "target", "hardware", "channel", "sequence",
    "version", "url", "size", "image_sha256", "file_sha256",
    "signed_manifest", "signature", "published_at",
}
missing = sorted(required - manifest.keys())
if missing:
    fail(f"missing manifest fields: {', '.join(missing)}")

if manifest["schema"] != 1 or manifest["product"] != "smartstart":
    fail("unsupported schema or product")
if manifest["target"] != "esp32s3":
    fail("target must be esp32s3")
if not manifest["url"].startswith(PUBLIC_PREFIX):
    fail("firmware URL is outside the SmartStart Pages origin")

url_path = urlparse(manifest["url"]).path.removeprefix("/")
firmware = (ROOT / url_path).resolve()
if ROOT not in firmware.parents or not firmware.is_file():
    fail("firmware path is missing or unsafe")

payload = firmware.read_bytes()
if len(payload) != manifest["size"]:
    fail("file size does not match manifest")
if hashlib.sha256(payload).hexdigest() != manifest["file_sha256"]:
    fail("whole-file SHA-256 does not match manifest")
if len(payload) < 32 or payload[-32:].hex() != manifest["image_sha256"]:
    fail("ESP image validation hash does not match manifest")
if firmware.parent.name != manifest["version"]:
    fail("version and firmware directory do not match")
if not manifest["signed_manifest"] or not manifest["signature"]:
    fail("manifest must be digitally signed")

canonical = (
    "SMARTSTART-OTA-V1\n"
    f"{manifest['schema']}\n{manifest['product']}\n{manifest['target']}\n"
    f"{manifest['hardware']}\n{manifest['channel']}\n{manifest['sequence']}\n"
    f"{manifest['version']}\n{manifest['url']}\n{manifest['size']}\n"
    f"{manifest['image_sha256']}\n{manifest['file_sha256']}\n"
).encode("utf-8")
try:
    signature = base64.b64decode(manifest["signature"], validate=True)
except ValueError as error:
    fail(f"invalid base64 signature: {error}")
with tempfile.NamedTemporaryFile() as signature_file:
    signature_file.write(signature)
    signature_file.flush()
    verified = subprocess.run(
        ["openssl", "dgst", "-sha256", "-verify",
         str(ROOT / "keys/ota-signing-public.pem"),
         "-signature", signature_file.name],
        input=canonical,
        capture_output=True,
        check=False,
    )
if verified.returncode != 0:
    fail("ECDSA manifest signature is invalid")

print(f"Validated signed SmartStart {manifest['version']} ({len(payload)} bytes)")
