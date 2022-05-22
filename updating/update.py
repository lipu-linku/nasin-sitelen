#!/usr/bin/env python3
import argparse
import urllib.request  # avoiding requests dep bc we can
import json
from datetime import datetime
import os
import logging

LOG = logging.getLogger()

HEADERS = {  # pretend to be Chrome 101 for Discord links
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
}

JASIMA = "https://raw.githubusercontent.com/lipu-linku/jasima/master/data.json"

VALID_LICENSES = [
    "GPL",
    "MIT",
    "CC",
    "OFL",
    "CC BY 4.0",
    "CC BY-SA 3.0",
]  # TODO: these are just the ones in the doc

# TODO: d9j when filename in jasima
NO_URL_NAME = {
    "Toki Pona Bubble",  # yes I know
    "insa pi supa lape",
    "sitelen Sans",
    "sitelen Antowi",
    "toki pona OTF",
    "sitelen telo",
}
FILENAME_MAP = {key: f"{key}-fixme.ttf" for key in NO_URL_NAME}

FONTDIR = ".."


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req).read()
    return resp


# TODO: d5j when filename in jasima
def get_filename(url: str) -> str:
    # MOST download links contain the filename
    # stopgap until filename is in jasima
    return url.split("/")[-1]


def write_font(filename: str, content: bytes) -> int:
    with open(os.path.join(FONTDIR, filename), "wb") as f:
        written = f.write(content)
    return written


def main(argv):
    LOG.setLevel(argv.log_level)

    fonts = json.loads(download(JASIMA).decode("UTF-8"))["fonts"]

    for name, data in fonts.items():
        if "fontfile" not in data["links"]:
            continue  # unsupported

        if argv.licenses and not (data["license"] in VALID_LICENSES):
            continue  # we can't distribute

        # TODO: store last checked time la only check new fonts
        # if datetime.strptime(data["last_updated"], "%Y-%m").date() >= ...:
        #     continue

        # TODO: unzip insa pi supa lape to fetch just the one file
        # TODO: anything on Box and Drive cannot be directly downloaded

        try:
            LOG.debug("NAME: %s" % name)
            download_url = data["links"]["fontfile"]
            LOG.debug("LINK: %s" % download_url)
            filename = (
                get_filename(download_url)
                if name not in NO_URL_NAME
                else FILENAME_MAP[name]
            )
            LOG.debug("FILE: %s" % filename)
            font = download(data["links"]["fontfile"])
            write_font(filename, font)
        except Exception as e:
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
        default=False,
        action="store_true",
    )
    ARGV = parser.parse_args()
    main(ARGV)
