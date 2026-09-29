"""
Standalone diagnostic script: report the APIDs present in a CCSDS binary file.
Optionally extract just one APID's packets into a new file.

Usage
-----
    python -m hermes_eea.util.inspect_apids path/to/file.bin
    python -m hermes_eea.util.inspect_apids path/to/file.bin --apid 260 --output only_260.bin
"""

import argparse
import collections

from ccsdspy.utils import read_primary_headers

from hermes_eea.util.filter_apid import filter_apid


def inspect_apids(filename: str) -> None:
    headers = read_primary_headers(filename)
    apids = headers["CCSDS_APID"]
    lengths = headers["CCSDS_PACKET_LENGTH"]

    counts = collections.Counter(apids.tolist())
    print(f"{filename}: {len(apids)} packets, {len(counts)} unique APID(s)")
    print(f"{'APID':>6}  {'count':>8}  {'min len':>8}  {'max len':>8}")
    for apid, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        mask = apids == apid
        apid_lengths = lengths[mask]
        print(
            f"{apid:>6}  {count:>8}  {apid_lengths.min():>8}  {apid_lengths.max():>8}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filename", help="Path to the CCSDS binary file to inspect")
    parser.add_argument("--apid", type=int, help="If given, extract only this APID's packets")
    parser.add_argument(
        "--output", help="Output filename for the filtered packets (required with --apid)"
    )
    args = parser.parse_args()

    inspect_apids(args.filename)

    if args.apid is not None:
        if not args.output:
            parser.error("--output is required when --apid is given")
        n_bytes = filter_apid(args.filename, args.output, args.apid)
        print(f"Wrote {n_bytes} bytes (apid={args.apid}) to {args.output}")
