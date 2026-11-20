from dataclasses import dataclass, asdict
import json

@dataclass(frozen=True)
class Transaction:
    tx_id: int
    sender: str
    receiver: str
    amount: float
    nonce: int

    def to_dict(self):
        return asdict(self)

    def to_bytes(self):
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
