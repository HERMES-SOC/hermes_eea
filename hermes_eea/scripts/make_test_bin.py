"""
Generate a properly-named EEA level-0 test .bin file (matching HERMES filename
conventions: hermes_EEA_l0_{YYYYDDD-HHMMSS}_v{version}.bin) from a JSONL
telemetry log, for use as test fixture data.

Reuses `jsonl_to_bin` to do the actual packet extraction.

Usage
-----
    python -m hermes_eea.util.make_test_bin log_0.jsonl
    python -m hermes_eea.util.make_test_bin log_0.jsonl --max-packets 500 --version 1
    python -m hermes_eea.util.make_test_bin log_0.jsonl --time 2026001-000000 --output-dir hermes_eea/data
"""

import argparse
import os
from datetime import datetime, timezone

import hermes_eea
from hermes_eea.util.jsonl_to_bin import jsonl_to_bin


def make_l0_filename(time: str, version: int) -> str:
    """Build a HERMES-compliant L0 packet filename, e.g. hermes_EEA_l0_2026023-000000_v0.bin"""
    return f"hermes_EEA_l0_{time}_v{version}.bin"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_filename", help="Path to the JSONL telemetry log")
    parser.add_argument(
        "--output-dir",
        default=hermes_eea._data_directory,
        help="Directory to write the .bin file into (default: hermes_eea/data)",
    )
    parser.add_argument(
        "--time",
        default=None,
        help="L0 time string YYYYDDD-HHMMSS to embed in the filename (default: current UTC time)",
    )
    parser.add_argument("--version", type=int, default=0, help="File version number (default: 0)")
    parser.add_argument(
        "--packet-name",
        default="EEAtlmIntAccum",
        help="Packet 'name' to extract (default: EEAtlmIntAccum, the EEA science packet)",
    )
    parser.add_argument(
        "--max-packets", type=int, default=None, help="Optional cap on number of packets to write"
    )
    args = parser.parse_args()

    time_str = args.time or datetime.now(timezone.utc).strftime("%Y%j-%H%M%S")
    output_filename = os.path.join(args.output_dir, make_l0_filename(time_str, args.version))

    n_packets = jsonl_to_bin(
        args.input_filename, output_filename, args.packet_name, args.max_packets
    )
    print(f"Wrote {n_packets} '{args.packet_name}' packets to {output_filename}")
