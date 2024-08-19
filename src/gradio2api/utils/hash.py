import os
HASH_DIGEST_SIZE = int(os.getenv("HASH_DIGEST_SIZE", 8))
USED_HASHES = set()

def _make_hash(x:str|bytes, digest_size=HASH_DIGEST_SIZE)->str:
  from hashlib import blake2b
  h = blake2b(digest_size=digest_size)
  if type(x) is str:
    x = x.encode("utf-8")
  h.update(x)
  return h.hexdigest()

def _add_and_verify_hash(hash:str):
  assert type(hash) is str and hash not in USED_HASHES
  USED_HASHES.add(hash)

def add_key_and_verify(x:str|bytes, *args):
  hash = _make_hash(x, *args)
  _add_and_verify_hash(hash)
