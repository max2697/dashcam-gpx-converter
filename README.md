# Dashcam GPX Converter

Convert 70mai dashcam GPS logs into GPX tracks for easy mapping and analysis

## Installation

```bash
pip install dashcam-gpx-converter
```

## Usage

```bash
dashcam2gpx -s 250 GPSData000001.txt -o GPSData000001.gpx -v
```

- `GPSData000001.txt`: Your dashcam log file, including the `.txt` extension.
- `-o, --output`: Optional GPX output file name (e.g., GPSData000001.gpx).
- `-v, --verbose`: Enable debug logging.
- `-i, --info`: Show file info.
- `-s, --segments-limit`: Maximum number of track segments to include (default: 0). Set to **250** for easier importing into **Dawarich**.

## Development

```bash
git clone https://github.com/max2697/dashcam-gpx-converter.git
cd dashcam-gpx-converter
poetry install --with dev
poetry run dashcam2gpx -s 250 GPSData000001.txt
poetry run poe lint
```