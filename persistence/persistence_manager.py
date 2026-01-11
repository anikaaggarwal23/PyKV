import os
import struct
import threading
import time
from config import WAL_PATH, REPLICA_WAL_PATH, COMPACTION_INTERVAL

class PersistenceManager:
    def __init__(self):
        self.wal_path = WAL_PATH
        self.replica_path = REPLICA_WAL_PATH
        os.makedirs("data", exist_ok=True)

    def log_set(self, key: str, value: str):
        record = self._encode_record(b"S", key, value)
        self._append(record)

    def log_delete(self, key: str):
        record = self._encode_record(b"D", key, "")
        self._append(record)

    def _encode_record(self, op: bytes, key: str, value: str) -> bytes:
        key_bytes = key.encode()
        value_bytes = value.encode()
        return struct.pack(
            f"!cII{len(key_bytes)}s{len(value_bytes)}s",
            op,
            len(key_bytes),
            len(value_bytes),
            key_bytes,
            value_bytes
        )

    def _append(self, record: bytes):
        with open(self.wal_path, "ab") as f:
            f.write(record)
        with open(self.replica_path, "ab") as rf:
            rf.write(record)

    def recover(self):
        data = {}
        if not os.path.exists(self.wal_path):
            return data

        with open(self.wal_path, "rb") as f:
            while True:
                header = f.read(9)
                if not header:
                    break
                op, klen, vlen = struct.unpack("!cII", header)
                key = f.read(klen).decode()
                value = f.read(vlen).decode()

                if op == b"S":
                    data[key] = value
                elif op == b"D":
                    data.pop(key, None)

        return data

    def start_background_compaction(self):
        def compact_loop():
            while True:
                time.sleep(COMPACTION_INTERVAL)
                self.compact()

        threading.Thread(target=compact_loop, daemon=True).start()

    def compact(self):
        data = self.recover()
        with open(self.wal_path, "wb") as f:
            for k, v in data.items():
                f.write(self._encode_record(b"S", k, v))
