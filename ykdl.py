#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import ykdl
except(ImportError):
    import sys
    import os

    _srcdir = '%s/' % os.path.dirname(os.path.realpath(__file__))
    _filepath = os.path.dirname(sys.argv[0])
    sys.path.insert(1, os.path.join(_filepath, _srcdir))
    sys.path.insert(1, os.path.join(_filepath, '../lib/requests_lib/'))
    import ykdl

conn = None

import json
import socket
import traceback
from argparse import ArgumentParser
from multiprocessing.connection import Client, Connection

import logging

logger = logging.getLogger("YKDL")

from ykdl.common import url_to_module
from ykdl.version import __version__
from ykdl.util import html

_get_content = html.get_content


def get_content(url, headers=html.fake_headers, data=None, charset=None):
    # logger.warning((url, data, charset, headers))
    if conn:
        bd = json.dumps({"url": url, "headers": headers, "data": data, "charset": charset}).encode("utf-8")
        try:
            conn.send_bytes(bd)
            resp = conn.recv_bytes()
            if charset == "ignore":
                return resp
            else:
                return resp.decode("utf-8")
        except Exception:
            logger.exception("get_content")
            sys.exit(0)
    return _get_content(url, headers, data, charset)


html.get_content = get_content


def arg_parser():
    parser = ArgumentParser(
        description="YouKuDownLoader(ykdl {}), a video downloader. Forked form you-get 0.3.34@soimort".format(
            __version__))
    parser.add_argument('-i', '--info', action='store_true', default=False,
                        help="Display the information of videos without downloading.")
    parser.add_argument('-J', '--json', action='store_true', default=False, help="Display info in json format.")
    parser.add_argument('-F', '--format', help="Video format code, or resolution level 0, 1, ...")
    parser.add_argument('-t', '--timeout', type=int, default=60, help="set socket timeout seconds, default 60s")
    parser.add_argument('--debug', default=False, action='store_true', help="print debug messages from ykdl")
    parser.add_argument('video_url', type=str, help="video url")
    return parser.parse_args()


def main():
    args = arg_parser()
    address = os.environ.get("address_get_url", None)
    if address:
        global conn
        conn = Client(address=address)
    logging.root.setLevel(logging.WARNING)
    # if not args.debug:
    #     logging.root.setLevel(logging.WARNING)
    # else:
    #     logging.root.setLevel(logging.DEBUG)

    if args.timeout:
        socket.setdefaulttimeout(args.timeout)

    try:
        url = args.video_url
        try:
            m, u = url_to_module(url)
            parser = m.parser
            info = parser(u)
            print(json.dumps(info.jsonlize(), indent=4, sort_keys=True, ensure_ascii=False))
        except AssertionError as e:
            logger.critical(e)
        except (RuntimeError, NotImplementedError, SyntaxError) as e:
            logger.error(e)
    except KeyboardInterrupt:
        logger.info('Interrupted by Ctrl-C')


if __name__ == '__main__':
    main()
