#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..util.html import get_content
from ..util.match import match1, matchall
from ..embedextractor import EmbedExtractor
from ykdl.util.danmaku2ass import Danmaku2ASS
from ykdl.compact import compact_tempfile

import json

class Acfun(EmbedExtractor):

    def prepare(self):

        html = get_content(self.url)

        sourceVid = match1(html, "data-vid=\"([a-zA-Z0-9=]+)\" data-scode=")

        #process danmu:
        danmu = get_content('http://danmu.aixifan.com/V3/{}/1/500'.format(sourceVid))
        self.danmu = compact_tempfile(mode='w+t')
        self.danmu.write(danmu)
        self.ass = compact_tempfile(mode='w+t',suffix='.ass')
        Danmaku2ASS(self.danmu.name, self.ass.name, 1080, 720)
        self.subtitle = self.ass.name

        data = json.loads(get_content('http://www.acfun.tv/video/getVideo.aspx?id={}'.format(sourceVid)))

        sourceType = data['sourceType']
        sourceId = data['sourceId']

        if sourceType == 'zhuzhan':
            sourceType = 'acorig'
            sourceId = sourceId
        elif sourceType == 'letv':
            #workaround for letv, because it is letvcloud
            sourceType = 'letvcloud'
            sourceId = (sourceId, '2d8c027396')

        self.video_info=(sourceType, sourceId)

    def download_playlist(self, url, param):
        self.url = url

        html = get_content(self.url)

        videos = matchall(html, ['href="([\/a-zA-Z0-9_]+)" title="Part'])

        for v in videos:
            next_url = "http://www.acfun.tv/{}".format(v)
            self.download(next_url, param)

site = Acfun()
