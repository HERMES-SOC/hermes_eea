"""
Standalone diagnostic script: extract only the packets for one APID out of a
mixed CCSDS binary file and write them to a new file.

Usage
-----
    python -m hermes_eea.util.filter_apid input.bin output.bin --apid 260
"""

import argparse

from ccsdspy.utils import split_by_apid


def filter_apid(input_filename: str, output_filename: str, apid: int) -> int:
    """Write only the packets matching `apid` from `input_filename` to `output_filename`.

    Returns
    -------
    n_bytes: int
        Number of bytes written to the output file.
    """
    streams_by_apid = split_by_apid(input_filename)
    if apid not in streams_by_apid:
        raise ValueError(
            f"APID {apid} not found in {input_filename}. "
            f"Available APIDs: {sorted(streams_by_apid)}"
        )

    data = streams_by_apid[apid].read()
    with open(output_filename, "wb") as fh:
        fh.write(data)

    return len(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_filename", help="Path to the mixed-APID CCSDS binary file")
    parser.add_argument("output_filename", help="Path to write the filtered binary file to")
    parser.add_argument("--apid", type=int, required=True, help="APID to keep")
    args = parser.parse_args()

    n_bytes = filter_apid(args.input_filename, args.output_filename, args.apid)
    print(f"Wrote {n_bytes} bytes ({args.apid=}) to {args.output_filename}")
