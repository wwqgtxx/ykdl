#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import ykdl
except(ImportError):
    import sys
    import os
    _base_len = len('bin/ykdl')
    _filepath = sys.argv[0][:-_base_len]
    sys.path.insert(1, _filepath)
    sys.path.insert(1, os.path.join(_filepath, '../lib/requests_lib/'))
    import ykdl
    
from cykdl.__main__ import main

if __name__ == '__main__':
    main()
