"""
Standalone script: extract real EEA packets out of a JSONL telemetry log
(e.g. log_0.jsonl) and write them out, in order, as a raw CCSDS binary file.

Packets can be selected either by packet name (e.g. "EEAtlmIntAccum") or by
CCSDS APID (e.g. 260 for the science packet, 265 for housekeeping).

Usage
-----
    python -m hermes_eea.util.jsonl_to_bin log_0.jsonl output.bin
    python -m hermes_eea.util.jsonl_to_bin log_0.jsonl output.bin --packet-name EEAtlmIntAccum --max-packets 500
    python -m hermes_eea.util.jsonl_to_bin log_0.jsonl output.bin --apid 265
"""

import argparse
import json
import sys


def jsonl_to_bin(input_filename: str, output_filename: str, packet_name=None, apid=None, max_packets=None) -> int:
    """Write the hex-decoded bytes of matching packets, in file order, to `output_filename`.

    Exactly one of `packet_name` or `apid` must be given to select which packets to extract.

    Returns
    -------
    n_packets: int
        Number of packets written.
    """
    if (packet_name is None) == (apid is None):
        raise ValueError("Specify exactly one of packet_name or apid")

    sys.set_int_max_str_digits(0)  # some "contents" fields are huge integers

    n_packets = 0
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
                fh_out.write(bytes.fromhex(entry["hex"]))
                n_packets += 1
                if max_packets is not None and n_packets >= max_packets:
                    return n_packets

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
    args = parser.parse_args()

    packet_name = args.packet_name
    if packet_name is None and args.apid is None:
        packet_name = "EEAtlmIntAccum"

    n_packets = jsonl_to_bin(
        args.input_filename, args.output_filename, packet_name, args.apid, args.max_packets
    )
    print(f"Wrote {n_packets} packets (packet_name={packet_name!r}, apid={args.apid}) to {args.output_filename}")
