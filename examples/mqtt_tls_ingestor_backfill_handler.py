#!/usr/bin/env python3
"""
DeviceLab DL-GW200 / DL-GW400: MQTT TLS 1.3 Telemetry & Flash Store-and-Forward Backfill Handler
Product Page:    https://devicelab.vn/san-pham/dl-gw200/
Technical Guide: https://devicelab.vn/kien-thuc/gateway-modbus-sang-mqtt/

Demonstrates how a Cloud IIoT / MES ingestion service processes both real-time
telemetry (`devicelab/+/telemetry`) and offline Flash backfill batches (`devicelab/+/backfill`)
with idempotent deduplication by `(device_id, seq, ts_unix_ms)`.
"""

import json
import sys
from collections import deque


class DeduplicatingTelemetryIngestor:
    def __init__(self, max_seen_cache: int = 50000):
        self._seen_keys = set()
        self._seen_order = deque(maxlen=max_seen_cache)

    def _mark_seen(self, key: tuple[str, int, int]) -> bool:
        if key in self._seen_keys:
            return False
        if len(self._seen_order) == self._seen_order.maxlen:
            oldest = self._seen_order.popleft()
            self._seen_keys.discard(oldest)
        self._seen_order.append(key)
        self._seen_keys.add(key)
        return True

    def process_message(self, topic: str, raw_payload: str) -> int:
        data = json.loads(raw_payload)
        device_id = data.get("device_id", "UNKNOWN")
        is_backfill = bool(data.get("is_backfill", False))

        inserted = 0
        if is_backfill and "records" in data:
            for rec in data["records"]:
                key = (device_id, int(rec["seq"]), int(rec["ts_unix_ms"]))
                if self._mark_seen(key):
                    inserted += 1
                    print(
                        f"[BACKFILL INSERT] device={device_id} seq={rec['seq']} ts={rec['ts_iso']} slaves={len(rec.get('slaves', []))}"
                    )
        else:
            key = (device_id, int(data["seq"]), int(data["ts_unix_ms"]))
            if self._mark_seen(key):
                inserted += 1
                print(
                    f"[REALTIME INSERT] device={device_id} seq={data['seq']} ts={data['ts_iso']} slaves={len(data.get('slaves', []))}"
                )
        return inserted


if __name__ == "__main__":
    import os

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rt_path = os.path.join(base_dir, "payloads", "dl_gw200_realtime_telemetry.json")
    bf_path = os.path.join(base_dir, "payloads", "dl_gw200_store_forward_backfill_batch.json")

    ingestor = DeduplicatingTelemetryIngestor()
    with open(rt_path, "r", encoding="utf-8") as f:
        ingestor.process_message("devicelab/DL-GW200-HN08/telemetry", f.read())
    with open(bf_path, "r", encoding="utf-8") as f:
        ingestor.process_message("devicelab/DL-GW200-HN08/backfill", f.read())
    sys.exit(0)
