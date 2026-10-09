"""Add/update a gold-review user in <root>/gold-users.json."""
import argparse, getpass, hashlib, json, secrets
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("username")
ap.add_argument("--root",default="data/vietnamese-ser/episodes")
a=ap.parse_args()
if not a.username.replace("_","").replace("-","").replace(".","").isalnum(): raise SystemExit("bad username")
password=getpass.getpass("Password: "); confirm=getpass.getpass("Confirm: ")
if not password or password!=confirm: raise SystemExit("passwords do not match")
path=Path(a.root)/"gold-users.json"; users=json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
rounds=310000; salt=secrets.token_bytes(16); digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,rounds)
users[a.username]=f"{rounds}${salt.hex()}${digest.hex()}"
path.write_text(json.dumps(users,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"saved {a.username} -> {path}")
