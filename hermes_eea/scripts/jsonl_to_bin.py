"""
Standalone script: extract real EEA packets out of a JSONL telemetry log
(e.g. log_0.jsonl) and write them out, in order, as a raw CCSDS binary file.

Packets can be selected either by packet name (e.g. "EEAtlmIntAccum") or by
CCSDS APID (e.g. 260 for the science packet, 265 for housekeeping).

A log file can span multiple distinct beam tests run back-to-back; use
--start-time/--end-time to keep only packets from one test's time window.

Usage
-----
    python -m hermes_eea.util.jsonl_to_bin log_0.jsonl output.bin
    python -m hermes_eea.util.jsonl_to_bin log_0.jsonl output.bin --packet-name EEAtlmIntAccum --max-packets 500
    python -m hermes_eea.util.jsonl_to_bin log_0.jsonl output.bin --apid 265
    python -m hermes_eea.util.jsonl_to_bin log_1.jsonl tb_ea_uneg135.bin \
        --start-time "06/10/2026, 14:18:44.0" --end-time "06/10/2026, 14:32:16.0"
"""

import argparse
import json
import sys
from datetime import datetime

TIMESTAMP_FORMAT = "%m/%d/%Y, %H:%M:%S.%f"


def parse_timestamp(value: str) -> datetime:
    """Parse a --start-time/--end-time command-line value, e.g. "06/10/2026, 14:18:44.0".

    Tolerates an omitted fractional-seconds part (e.g. "06/10/2026, 14:18:44").
    """
    try:
        return datetime.strptime(value, TIMESTAMP_FORMAT)
    except ValueError:
        return datetime.strptime(value, "%m/%d/%Y, %H:%M:%S")


def jsonl_to_bin(
    input_filename: str,
    output_filename: str,
    packet_name=None,
    apid=None,
    max_packets=None,
    start_time: datetime = None,
    end_time: datetime = None,
    timestamps_out: str = None,
) -> int:
    """Write the hex-decoded bytes of matching packets, in file order, to `output_filename`.

    Exactly one of `packet_name` or `apid` must be given to select which packets to extract.
    `start_time`/`end_time`, if given, restrict output to packets whose "timestamp" field
    (as parsed by `parse_timestamp`) falls within [start_time, end_time], inclusive.

    If `timestamps_out` is given, each written packet's original "timestamp" string is
    appended there (one per line, in output order). The CDF's own Epoch is derived from
    SHCOARSE/SHFINE and is not synced to real wall-clock time, so this sidecar file is the
    only way to later correlate packets/sweeps with the real time the facility recorded.

    Returns
    -------
    n_packets: int
        Number of packets written.
    """
    if (packet_name is None) == (apid is None):
        raise ValueError("Specify exactly one of packet_name or apid")

    if hasattr(sys, "set_int_max_str_digits"):  # not available before Python 3.9.17/3.10.9
        sys.set_int_max_str_digits(0)  # some "contents" fields are huge integers

    n_packets = 0
    timestamps_fh = open(timestamps_out, "w") if timestamps_out else None
    try:
        with open(input_filename) as fh_in, open(output_filename, "wb") as fh_out:
            for line in fh_in:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue  # the log has a handful of malformed/truncated lines
                for entry in record.values():
                    if packet_name is not None and entry["name"] != packet_name:
                        continue
                    if apid is not None and entry["contents"]["app_id"] != apid:
                        continue
                    if start_time is not None or end_time is not None:
                        entry_time = parse_timestamp(entry["timestamp"])
                        if start_time is not None and entry_time < start_time:
                            continue
                        if end_time is not None and entry_time > end_time:
                            continue
                    fh_out.write(bytes.fromhex(entry["hex"]))
                    if timestamps_fh is not None:
                        timestamps_fh.write(entry["timestamp"] + "\n")
                    n_packets += 1
                    if max_packets is not None and n_packets >= max_packets:
                        return n_packets
    finally:
        if timestamps_fh is not None:
            timestamps_fh.close()

    return n_packets


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_filename", help="Path to the JSONL telemetry log")
    parser.add_argument("output_filename", help="Path to write the resulting binary file to")
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument(
        "--packet-name",
        default=None,
        help="Packet 'name' to extract (default: EEAtlmIntAccum, the EEA science packet, if --apid is not given)",
    )
    selector.add_argument("--apid", type=int, help="CCSDS APID to extract instead of matching by packet name")
    parser.add_argument(
        "--max-packets", type=int, default=None, help="Optional cap on number of packets to write"
    )
    parser.add_argument(
        "--start-time",
        default=None,
        help='Only include packets at/after this timestamp, e.g. "06/10/2026, 14:18:44.0"',
    )
    parser.add_argument(
        "--end-time",
        default=None,
        help='Only include packets at/before this timestamp, e.g. "06/10/2026, 14:32:16.0"',
    )
    parser.add_argument(
        "--timestamps-out",
        default=None,
        help="Optional path to write a sidecar file of each written packet's real timestamp, one per line",
    )
    args = parser.parse_args()

    packet_name = args.packet_name
    if packet_name is None and args.apid is None:
        packet_name = "EEAtlmIntAccum"

    start_time = parse_timestamp(args.start_time) if args.start_time else None
    end_time = parse_timestamp(args.end_time) if args.end_time else None

    n_packets = jsonl_to_bin(
        args.input_filename,
        args.output_filename,
        packet_name,
        args.apid,
        args.max_packets,
        start_time,
        end_time,
        args.timestamps_out,
    )
    print(f"Wrote {n_packets} packets (packet_name={packet_name!r}, apid={args.apid}) to {args.output_filename}")
