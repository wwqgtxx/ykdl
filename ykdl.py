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

import json
import socket
import traceback
import base64
from argparse import ArgumentParser
from multiprocessing.connection import Client, Connection

import logging

logger = logging.getLogger("YKDL")

from ykdl.common import url_to_module
from ykdl.version import __version__
from ykdl.util import html


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
        conn = Client(address=address)

        def _get(bd, decoded=True):
            try:
                conn.send_bytes(bd)
                resp = conn.recv_bytes()
                if decoded:
                    return resp.decode("utf-8")
                else:
                    return resp
            except Exception:
                sys.exit(0)

        class Response(object):
            __slots__ = ("data", "headers", "url")

        def get_response(url, faker=False, headers=None, get_method=None, without_data=False, no_logging=False):
            if not no_logging:
                logging.debug('get_response: %s' % url)

            bd = json.dumps({"url": url, "headers": headers,
                             "encoding": "response_without_data" if without_data else "response",
                             "method": get_method}).encode("utf-8")
            resp = json.loads(_get(bd, True))
            response = Response()
            response.data = None if without_data else base64.b64decode(resp["data"])
            response.headers = resp["headers"]
            response.url = resp["url"]
            return response

        def get_location(url, headers=html.fake_headers):
            resp = get_response(url, headers=headers, without_data=True, no_logging=True)
            return resp.url

        def get_content(url, headers=html.fake_headers, data=None, charset=None):
            # logger.warning((url, data, charset, headers))
            bd = json.dumps({"url": url, "headers": headers, "data": data, "charset": charset}).encode("utf-8")
            return _get(bd, charset != "ignore")

        html.get_location = get_location
        html.get_content = get_content

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
