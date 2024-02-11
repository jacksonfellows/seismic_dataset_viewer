# WARNING: This file currently needs the seismoslide conda env.

import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import obspy
import obspy.clients.fdsn.mass_downloader as mdown
import pandas as pd

exotic_m = pd.read_csv("~/.seisbench/datasets/pnwexotic/metadata.csv")
su_m = exotic_m[exotic_m["source_type"] == "surface event"]

pre_pick_time = 0
after_pick_time = 120


def download_event(event_m, radius_deg):
    lat, lon = event_m["station_latitude_deg"], event_m["station_longitude_deg"]
    # Min/max radius in degrees.
    domain = mdown.CircularDomain(
        latitude=lat, longitude=lon, minradius=0, maxradius=radius_deg
    )
    print(lat, lon, radius_deg)
    start_time = obspy.UTCDateTime(event_m["trace_start_time"])
    restrictions = mdown.Restrictions(
        starttime=start_time - pre_pick_time,
        endtime=start_time + after_pick_time,
        channel="*HZ",
        minimum_interstation_distance_in_m=0, # Default is 1000 m!
    )

    # Download event files to a temporary directory.
    download_dir = tempfile.mkdtemp()
    mdl = mdown.MassDownloader(providers=["IRIS"])
    mdl.download(
        domain=domain,
        restrictions=restrictions,
        mseed_storage=str(download_dir),
        stationxml_storage=str(download_dir),
    )

    # Read the files into obspy.
    st = obspy.read(Path(download_dir) / "*.mseed")
    inv = obspy.read_inventory(Path(download_dir) / "*.xml")
    return st, inv


def get_station_name(channel):
    return ".".join(channel.split(".")[:2])


def make_channel_name(m):
    network = m["station_network_code"]
    station = m["station_code"]
    loc = (
        m["station_location_code"]
        if m["station_location_code"] != "--"
        else ""
    )
    channel_code = m["station_channel_code"] + "Z"
    channel = ".".join([network, station, loc, channel_code])
    return channel


def write_event(event_m, picks_dict, st, inv):
    # Take obspy objects and write them in a format for the web tool.
    event_dir = Path("events") / event_m["event_id"]
    if event_dir.exists():
        raise ValueError()
    event_dir.mkdir()
    # Waveforms
    for tr in st:
        # Endianness important for loading in browser.
        X = tr.times().astype("<f")
        Y = tr.data.astype("<f")
        XY = np.concatenate((X, Y), axis=None)
        np.save(event_dir / tr.id, XY)
    # Metadata
    channels = inv.get_contents()["channels"]
    # TODO: Handle events w/ multiple picks.
    reference_channel = make_channel_name(event_m)
    ref_lat = inv.get_channel_metadata(reference_channel)["latitude"]
    ref_lon = inv.get_channel_metadata(reference_channel)["longitude"]
    metadata = {
        "event_id": event_m["event_id"],
        "station_metadata": {},
        "channels": channels,
        "reference_channel": reference_channel,
        "m_from_reference_station": {},
        "trace_start_time": event_m["trace_start_time"],
        "reference_picks": picks_dict,
    }
    for c in channels:
        cm = inv.get_channel_metadata(c)
        s = get_station_name(c)
        lat, lon = cm["latitude"], cm["longitude"]
        metadata["station_metadata"][s] = {"latitude": lat, "longitude": lon}
        metadata["m_from_reference_station"][s] = obspy.geodetics.gps2dist_azimuth(
            ref_lat, ref_lon, lat, lon
        )[0]
    with open(event_dir / "metadata.json", "w") as f:
        json.dump(metadata, f)


def download_and_write():
    event_ids = su_m["event_id"].unique()
    for event_id in event_ids[3000:3010]:
        if (Path("events") / event_id).exists():
            print(f"skipping event {event_id}")
            continue
        print(f"downloading & writing {event_id}")
        event_traces = su_m[su_m["event_id"] == event_id]
        # Take first pick (first start time) as reference channel/trace.
        times = np.array([obspy.UTCDateTime(st).timestamp for st in event_traces["trace_start_time"]])
        refi = np.argmin(times)
        ref_m = event_traces.iloc[refi]
        # Find rough max distance in deg between picked channels.
        ref_lat = ref_m["station_latitude_deg"]
        ref_lon = ref_m["station_longitude_deg"]
        print(f"{ref_lat=}, {ref_lon=}")
        distance_deg = [
            obspy.geodetics.kilometers2degrees(
                obspy.geodetics.gps2dist_azimuth(
                    ref_lat,
                    ref_lon,
                    event_traces.iloc[i]["station_latitude_deg"],
                    event_traces.iloc[i]["station_longitude_deg"],
                )[0]*1e-3
            ) for i in range(len(event_traces))
        ]
        radius_deg = max(0.2, max(distance_deg)) + 0.1
        # Store picks
        # assert((event_traces["trace_P_arrival_sample"]==7000).all)()
        # For some reason the trace_P_arrival_sample of 7000 seems to be 20 s.
        # TODO: Look into this. Is it always exactly 20 s?
        picks = pre_pick_time + 20 + times - times[refi]
        picks_dict = {make_channel_name(event_traces.iloc[i]): picks[i] for i in range(len(picks))}
        print(f"{picks_dict=}, {radius_deg=}")
        try:
            st, inv = download_event(ref_m, radius_deg=radius_deg)
        except Exception as e:
            print(f"downloading event {event_id} failed: {e}")
        try:
            write_event(ref_m, picks_dict, st, inv)
        except Exception as e:
            print(f"writing event {event_id} failed: {e}")
            # Cleanup! If we didn't download the full event stuff will be broken.
            event_dir = Path("events") / ref_m["event_id"]
            print(f"deleting {event_dir}")
            shutil.rmtree(event_dir)
            continue


if __name__ == "__main__":
    download_and_write()
