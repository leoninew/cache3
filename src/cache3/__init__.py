#!/usr/bin/python
# -*- coding: utf-8 -*-
# DATE: 2021/7/24
# Author: clarkmonkey@163.com

"""
Cache3 is a MIT licensed  safe and lightweight cache library, written in pure-Python.
"""

from typing import List
from cache3.utils import lazy, LazyObject
from cache3.disk import DiskCache, LazyDiskCache
from cache3.memory import Cache, MiniCache
from cache3.setting import PROJECT, VERSION

__author__: str = 'St. Kali'
__name__: str = PROJECT
__email__: str = 'clarkmonkey@163.com'
__version__: str = '.'.join(map(str, VERSION))

__all__: List[str] = [
    'DiskCache', 'LazyDiskCache',
    'Cache', 'MiniCache',
    'LazyObject', 'lazy',
]

