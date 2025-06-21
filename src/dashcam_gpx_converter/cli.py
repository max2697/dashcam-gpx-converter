"""
Command-line interface for 70mai dashcam GPX converter.
"""

import logging
from argparse import ArgumentParser
from pathlib import Path

from .converter import parse_tracks, write_gpx


def main() -> None:
    """
    Parse arguments and run conversion.
    """
    parser = ArgumentParser(prog="dashcam2gpx", description="Convert 70mai dashcam logs (.txt) to GPX tracks.")
    parser.add_argument("input", type=Path, help="Path to dashcam log file (e.g., GPSData000001.txt).")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Path for GPX output (e.g., GPSData000001.gpx). Defaults to input path with .gpx extension.",
    )
    parser.add_argument(
        "--segments-limit",
        "-s",
        type=int,
        default=0,
        help="Maximum number of track segments to include in the GPX file. 0 - no limit.",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")

    input_path = args.input
    output_path = args.output or input_path.with_suffix(".gpx")

    tracks = parse_tracks(input_path)
    if not tracks:
        logging.warning("No valid tracks found in %s", input_path)
        return
    write_gpx(tracks, output_path, segments_limit=args.segments_limit)


if __name__ == "__main__":
    main()
