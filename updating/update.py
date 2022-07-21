#!/usr/bin/env python3
import argparse
import json
import logging
import os
import urllib.request  # avoiding requests dep bc we can
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

LOG = logging.getLogger()

HEADERS = {  # pretend to be Chrome 101 for Discord links
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
}

JASIMA = "https://raw.githubusercontent.com/lipu-linku/jasima/master/data.json"

VALID_LICENSES = [
    "GPL",
    "MIT",
    "CC0",
    "OFL",
    "CC BY 4.0",
    "CC BY-SA 3.0",
    "OFL/GPL",
]  # TODO: these are just the ones in the doc

FONTDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")

# map of special behaviors per font
SPECIAL = {
    "insa pi supa lape": lambda url: download_zip(url, "standard/supalape.otf"),
    # TODO: below are maybe workaround-able
    "sitelen Antowi": lambda url: None,
    "sitelen Sans": lambda url: None,
    "sitelen telo": lambda url: None,
}

BAD_HOSTS = {"drive.google.com", "app.box.com", "1drv.ms", "infinityfreeapp.com"}


def can_download(url: str) -> bool:
    for s in BAD_HOSTS:
        if s in url:
            return False
    return True


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req).read()
    return resp


def download_zip(url: str, filename: str):
    zipfile = ZipFile(BytesIO(download(url)))
    f = zipfile.open(filename)
    resp = f.read()
    f.close()
    return resp


def write_font(filename: str, content: bytes) -> int:
    with open(os.path.join(FONTDIR, filename), "wb") as f:
        written = f.write(content)
    return written


def main(argv):
    LOG.setLevel(argv.log_level)

    fonts = json.loads(download(JASIMA).decode("UTF-8"))["fonts"]

    for name, data in fonts.items():
        if "fontfile" not in data["links"]:
            LOG.warning("No download available for %s", name)
            continue

        if argv.licenses and not ("license" in data):
            LOG.warning("No license available for %s", name)
            continue

        if argv.licenses and not (data["license"] in VALID_LICENSES):
            LOG.warning("Non-open license %s for %s", data["license"], name)
            continue

        # TODO: store last checked time la only check new fonts
        # if datetime.strptime(data["last_updated"], "%Y-%m").date() >= "TODO":
        #     LOG.info("No update for %s since last check", name)
        #     continue

        if not can_download(data["links"]["fontfile"]):
            LOG.warning("Cannot download %s", name)
            continue

        try:
            if name in SPECIAL:
                font = SPECIAL[name](data["links"]["fontfile"])
            else:
                font = download(data["links"]["fontfile"])

            if font:  # safety, don't overwrite
                write_font(data["filename"], font)
            else:
                LOG.error("Did not download %s", name)
        except Exception as e:
            LOG.error("Failed to download %s", name)
            LOG.error(e.__dict__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to update locally tracked fonts"
    )
    parser.add_argument(
        "--log-level",
        help="Set the log level",
        type=str.upper,
        dest="log_level",
        default="INFO",
        choices=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument(
        "--licenses",
        help="Enable license checking, excluding fonts with non-open licenses",
        dest="licenses",
        default=True,
        action="store_true",
    )
    ARGV = parser.parse_args()
    main(ARGV)
