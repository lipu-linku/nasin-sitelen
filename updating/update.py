#!/usr/bin/env python3
import argparse
import pygsheets
import requests

CLIENT = pygsheets.authorize()

TP_RESOURCES_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1DMgOQHw3R5yyrNF9BwWw9nWMwYaxI7D40-oEhI2Gm-c"


FONTS_SHEET = 0

# cols are 1 indexed
DOWNLOAD_COL = 3
LICENSE_COL = 7

VALID_LICENSES = [
    "GPL",
    "MIT",
    "CC",
    "OFL",
    "CC BY 4.0",
    "CC BY-SA 3.0",
]  # TODO: these are just the ones in the doc


def main(argv):
    sheets = CLIENT.open_by_url(TP_RESOURCES_SHEETS_URL)
    fonts_sheet = sheets[FONTS_SHEET]

    downloads = []
    for i, fontdef in enumerate(fonts_sheet):
        if i == 0:  # you can't slice fonts_sheet but you can enumerate it...
            continue

        if argv.licenses and not (fontdef[LICENSE_COL] in VALID_LICENSES):
            continue

        downloads.append(fontdef[DOWNLOAD_COL]) if fontdef[DOWNLOAD_COL] else None

    print(downloads)
    # each download is different
    # some give the font artifact directly
    # others are a zip file
    # more aren't actually a direct download link, but a secondary link


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to update locally tracked fonts"
    )
    parser.add_argument(
        "-l",
        "--licenses",
        dest="licenses",
        default=False,
        action="store_true",
    )
    ARGV = parser.parse_args()
    main(ARGV)
