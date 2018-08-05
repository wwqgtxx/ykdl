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
import os
from argparse import ArgumentParser
from multiprocessing.connection import Client, Connection

import logging

logger = logging.getLogger("YKDL")

from ykdl.common import url_to_module
from ykdl.version import __version__
from ykdl.util import html
from ykdl.compact import ProxyHandler, build_opener, install_opener, compact_str
from ykdl.util.html import default_proxy_handler


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
    parser.add_argument('--proxy', type=str, default='system',
                        help="set proxy HOST:PORT for http(s) transfer. default: use system proxy settings")
    parser.add_argument('video_url', type=str, help="video url")
    return parser.parse_args()


def main():
    args = arg_parser()

    logging.root.setLevel(logging.WARNING)
    # if not args.debug:
    #     logging.root.setLevel(logging.WARNING)
    # else:
    #     logging.root.setLevel(logging.DEBUG)

    if args.timeout:
        socket.setdefaulttimeout(args.timeout)

    if args.proxy == 'system':
        proxy_handler = ProxyHandler()
        args.proxy = os.environ.get('HTTP_PROXY', 'none')
    else:
        proxy_handler = ProxyHandler({
            'http': args.proxy,
            'https': args.proxy
        })
    if not args.proxy == 'none':
        opener = build_opener(proxy_handler)
        install_opener(opener)
        default_proxy_handler[:] = [proxy_handler]

    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context

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
