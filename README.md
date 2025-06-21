# Dashcam GPX Converter

Convert 70mai dashcam GPS logs into GPX tracks for easy mapping and analysis

## Installation

```bash
pip install dashcam-gpx-converter
```

## Usage

```bash
dashcam2gpx GPSData000001.txt -o GPSData000001.gpx -v
```

- `GPSData000001.txt`: Your dashcam log file, including the `.txt` extension.
- `-o, --output`: Optional GPX output file name (e.g., GPSData000001.gpx).
- `-v, --verbose`: Enable debug logging.

## Development

```bash
git clone https://github.com/max2697/dashcam-gpx-converter.git
cd dashcam-gpx-converter
pip install -r requirements.txt
poetry install
poetry run dashcam2gpx GPSData000001.txt
```