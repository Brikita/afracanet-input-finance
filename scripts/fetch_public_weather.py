"""Download real public weather reanalysis; never substitute invented values."""
import argparse
from datetime import date, datetime, timezone
import hashlib
import json
import math
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
API = "https://archive-api.open-meteo.com/v1/archive"
# Representative county reference points, not verified farmer locations.
LOCATIONS = [
    {"id": "meru-reference", "name": "Meru reference point", "latitude": 0.0464, "longitude": 37.6538},
    {"id": "machakos-reference", "name": "Machakos reference point", "latitude": -1.5177, "longitude": 37.2634},
]


def validate_weather(payload, start, end):
    daily = payload.get("daily", {})
    times = daily.get("time", [])
    from datetime import timedelta
    expected = [(start + timedelta(days=index)).isoformat() for index in range((end-start).days+1)]
    if times != expected:
        raise ValueError("Provider did not return the requested daily interval.")
    for field in ["precipitation_sum", "temperature_2m_max", "temperature_2m_min"]:
        values = daily.get(field, [])
        if len(values) != len(times) or any(type(value) not in {int, float} or not math.isfinite(value) for value in values):
            raise ValueError(f"Missing or nonnumeric public weather values: {field}. No fallback generated.")
    return len(times)


def fetch(start, end, output, force=False):
    if end < start or (end - start).days > 365 or end >= date.today():
        raise ValueError("Choose a past interval of at most 366 days.")
    paths = [output / f"{location['id']}-{start}-{end}.json" for location in LOCATIONS]
    manifest_path = output / "manifest.json"
    if not force and any(path.exists() for path in [*paths, manifest_path]):
        raise ValueError("Snapshot already exists. Use --force only to intentionally refresh it.")
    snapshots, downloads = [], []
    with httpx.Client(timeout=30) as client:
        for location, path in zip(LOCATIONS, paths):
            params = {"latitude": location["latitude"], "longitude": location["longitude"],
                      "start_date": start.isoformat(), "end_date": end.isoformat(), "models": "era5",
                      "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min", "timezone": "Africa/Nairobi"}
            response = client.get(API, params=params)
            response.raise_for_status()
            payload = response.json()
            count = validate_weather(payload, start, end)
            content = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            downloads.append((path, content))
            snapshots.append({"location": location, "source_url": str(response.request.url),
                              "file": path.name, "sha256": hashlib.sha256(content).hexdigest(), "daily_records": count})
    manifest = {"source_kind": "public_weather_reanalysis", "provider": "Open-Meteo / ERA5",
                "license": "CC BY 4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/",
                "attribution": "Weather data by Open-Meteo.com; ERA5 via Copernicus Climate Change Service.",
                "documentation": "https://open-meteo.com/en/docs/historical-weather-api",
                "api_use_terms": "https://open-meteo.com/en/pricing",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "start_date": start.isoformat(), "end_date": end.isoformat(),
                "limits": "Gridded reanalysis, not on-farm measurements. Reference points are not verified farmer locations. No credit-risk score is inferred.",
                "snapshots": snapshots}
    output.mkdir(parents=True, exist_ok=True)
    # All requests/validation finish before publishing any new snapshot.
    for path, content in downloads:
        path.write_bytes(content)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "datasets/public/weather")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        manifest = fetch(args.start, args.end, args.output, args.force)
    except (ValueError, httpx.HTTPError) as exc:
        parser.exit(1, f"Public data fetch failed ({type(exc).__name__}): {exc}. No synthetic fallback substituted.\n")
    print(f"Saved {sum(item['daily_records'] for item in manifest['snapshots'])} public daily records for {len(manifest['snapshots'])} reference points.")


if __name__ == "__main__":
    main()
