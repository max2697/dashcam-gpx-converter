"""
Convert 70mai dashcam logs into GPX tracks.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from zoneinfo import ZoneInfo

__all__ = ["to_local_timestamp", "parse_tracks", "write_gpx"]

logger = logging.getLogger(__name__)


def to_local_timestamp(dash_cam_timestamp: str) -> str:
    """
    Convert a 70mai dashcam UNIX timestamp (Asia/Shanghai) to local ISO8601.

    :param dash_cam_timestamp: Timestamp string from dashcam log
    :return: Local time in ISO8601 format
    """
    china_ts = datetime.fromtimestamp(int(dash_cam_timestamp), ZoneInfo("Asia/Shanghai"))
    utc_ts = china_ts.replace(tzinfo=timezone.utc)
    local_ts = utc_ts.astimezone(datetime.now().astimezone().tzinfo)
    return local_ts.isoformat()


def parse_tracks(log_path: Path) -> List[List[List[str]]]:
    """
    Read a dashcam GPS .txt log and split into tracks.

    :param log_path: Path to input .txt file
    :return: List of tracks, each track is a list of points [timestamp, status, lat, lon]
    """
    tracks: List[List[List[str]]] = []
    current: List[List[str]] = []
    first_segment = True
    previous: Optional[List[str]] = None

    with open(log_path, "r") as f:
        for line in f:
            token = line.strip()
            if token != "$V02":
                parts = token.split(",")
                point = [p.strip() for p in parts]
                if previous and int(point[0]) <= int(previous[0]):
                    continue
                if point[1] != "A" or point[2] == "0.000000" or point[3] == "0.000000":
                    continue
                current.append(point)
                previous = point
            else:
                if first_segment:
                    first_segment = False
                else:
                    if current:
                        tracks.append(current)
                    current = []
                    previous = None
    if current:
        tracks.append(current)
    logger.debug("Parsed %d tracks from %s", len(tracks), log_path)
    return tracks


def write_gpx(tracks: List[List[List[str]]], output_path: Path, segments_limit: int = 0) -> None:
    """
    Write tracks to a GPX file.

    :param tracks: Tracks parsed by parse_tracks()
    :param output_path: Path to output .gpx file
    :param segments_limit: Max number of segments to write into an output file
    """

    def write_file(path: Path, segments: List[List[List[str]]]) -> None:
        header = (
            '<?xml version="1.0" encoding="UTF-8" ?>\n'
            '<gpx\n\txmlns="http://www.topografix.com/GPX/1/1" \n'
            '\tversion="1.1"\n\txmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \n'
            '\txmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" \n'
            '\txsi:schemaLocation="\n'
            "\t\thttp://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd \n"
            "\t\thttp://www.garmin.com/xmlschemas/TrackPointExtension/v1 \n"
            '\t\thttp://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">\n'
            "\t<trk>"
        )
        points = 0
        with open(path, "w") as f:
            f.write(header)
            for segment in segments:
                f.write("\n\t\t<trkseg>")
                for point in segment:
                    ts = to_local_timestamp(point[0])
                    lat, lon = point[2], point[3]
                    speed = int(point[5]) / 100  # speed in m/s
                    f.write(
                        f'\n\t\t\t<trkpt lat="{lat}" lon="{lon}">'
                        f"\n\t\t\t\t<time>{ts}</time>"
                        "\n\t\t\t\t<extensions>\n\t\t\t\t\t<gpxtpx:TrackPointExtension>"
                        f"\n\t\t\t\t\t\t<gpxtpx:speed>{speed}</gpxtpx:speed>"
                        "\n\t\t\t\t\t</gpxtpx:TrackPointExtension>\n\t\t\t\t</extensions>"
                        "\n\t\t\t</trkpt>"
                    )
                    points += 1
                f.write("\n\t\t</trkseg>")
            f.write("\n\t</trk>\n</gpx>")
        logger.info("Wrote GPX to %s (%i points)", path, points)

    if segments_limit <= 0 or segments_limit >= len(tracks):
        write_file(output_path, tracks)
    else:
        # split into chunks
        for idx in range(0, len(tracks), segments_limit):
            chunk = tracks[idx : idx + segments_limit]
            suffix = f"_{idx // segments_limit + 1}.gpx"
            out_path = output_path.with_suffix("")
            out_file = out_path.with_name(out_path.name + suffix)
            write_file(out_file, chunk)


def print_info(tracks: List[List[List[str]]]) -> None:
    """
    Show file info.

    :param tracks: Tracks parsed by parse_tracks()
    """
    logger.info("File info:")
    logger.info(f"Tracks count:\t{len(tracks)}")
    if len(tracks) > 0:
        logger.info(f"File start time:\t{to_local_timestamp(tracks[0][0][0])}")
        logger.info(f"File end time:\t{to_local_timestamp(tracks[-1][-1][0])}")
        logger.info("Tracks by months:")
        month = to_local_timestamp(tracks[0][0][0])[0:7]
        count = 0
        for track in tracks:
            new_month = to_local_timestamp(track[0][0])[0:7]
            if new_month != month:
                logger.info(f"{month}:\t{count}")
                month = new_month
                count = 1
            else:
                count += 1
        logger.info(f"{month}:\t{count}")
