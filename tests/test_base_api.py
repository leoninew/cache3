#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# date: 2023/2/15

import pytest
from cache3.utils import empty
from cache3 import MiniCache, Cache, DiskCache
from shutil import rmtree
from utils import rand_strings, rand_string

params = pytest.mark.parametrize
raises = pytest.raises

key_types_cases = [
    # string
    ('key', 'value'),

    # float
    (3.3, 'float1'),
    (.3, 'float2'),
    (3., 'float'),

    # integer
    (3, 'integer'),

    # empty
    (empty, 'empty'),

    # bool
    (True, 'bool-true'),
    (1, 'bool-true-mess-1'),
    ('true', 'bool-true-mess-2'),
    (False, 'bool-false'),
    (0, 'bool-false-mess-1'),
    ('false', 'bool-false-mess-2'),
]


class TestGeneralCacheApi:

    def setup_class(self):
        self.mini_cache = MiniCache(f'mini-{rand_string()}')
        self.mem_cache = Cache(f'mem-{rand_string()}')
        self.disk_cache = DiskCache(f'disk-{rand_string()}')
        
        self.caches = [
            self.mini_cache,
            self.mem_cache,
            self.disk_cache,
        ]
    
    def teardown_class(self):
        self.disk_cache.sqlite.close()
        rmtree(self.disk_cache.directory)

    def setup_method(self):
        assert all((cache.clear() for cache in self.caches))

    @params('key, value', key_types_cases)
    def test_set_get(self, key, value):
        for cache in self.caches:
            cache.set(key, value)
            assert cache.pop(key) == value
            cache.set(value, key)
            assert cache.pop(value) == key

    @params('key, value', key_types_cases)
    def test_item_set_get(self, key, value):
        for cache in self.caches:
            assert key not in cache
            cache[key] = value
            assert key in cache
            assert cache[key] == value

    # def test_set_get_tag(self):
    #     for cache in self.caches:
    #         cache.set('name', 'value', tag='1')
    #         assert cache.get('name', empty) == empty
    #         assert cache.get('name', tag='1') == 'value'

    def test_clear(self):
        for cache in self.caches:
            cache.clear()
            cache.set('k', 'v')
            assert len(cache) == 1
            assert cache.clear()
            assert len(cache) == 0

    def test_ex_set(self):
        for cache in self.caches:
            assert cache.ex_set('name', None)
            assert not cache.ex_set('name', None)

    def test_incr_decr(self):
        count = 'count'
        for cache in self.caches:
            assert cache.set(count, 0)
            assert cache.incr(count, 1) == 1
            assert cache.decr(count, 1) == 0
            
            with raises(KeyError, match='key .* not found in cache'):
                cache.incr('no-existed')
            
            cache.set('not-number', 'a')
            with raises(TypeError, match='unsupported operand type'):
                cache.incr('not-number') 

    # @params('key, value, tag', [
    #     ('name', 'value', None),
    #     (empty, 'empty', None),
    #     (1111, 1111, None),
    #     (1111, 1111, 'tag-1'),
    #     ('empty', empty, 'tag-1'),
    #     ('empty', 'empty', 'tag-2'),
    # ])
    # def test_has_key(self, key, value, tag):
    #     for cache in self.caches:
    #         cache.set(key, value, tag=tag)
    #         assert cache.has_key(key, tag=tag)
    #         cache.delete(key, tag=tag)
    #         assert not cache.has_key(key, tag=tag)

    def test_touch(self):
        for cache in self.caches:
            cache.set('name', 'value', timeout=10)
            assert cache.touch('name', 100)
            assert cache.ttl('name') > 99
            assert not cache.touch('not-existed')

    def test_pop(self):
        for cache in self.caches:
            cache.set('key', 'value')
            assert cache.has_key('key')
            assert cache.pop('key') == 'value'
            value = cache.pop('key', default=None)
            assert value is None
            try:
                cache.pop('key')
            except KeyError:
                ...

    def test_ttl(self):
        for cache in self.caches:
            cache.set('key1', 'value', timeout=100)
            assert cache.ttl('key1') > 99
            assert not cache.has_key('key2')
            cache.set('key2', 'value')
            assert cache.ttl('key2') is None
            assert cache.ttl('not-existed') == -1

    def test_keys(self):

        count = 104
        keys = list(rand_strings(count, 4, 20))
        for cache in self.caches:
            for key in keys:
                cache.set(key, rand_string(4, 20))
            assert len(cache) == count
            assert list(cache.keys()).sort() == keys.sort()

        # assert list(cache.keys(tag='not-exited-tag')) == []
        # assert list(cache.keys(tag=None)) != []

    def test_values(self):
        count = 104
        values = list(rand_strings(count, 4, 20))
        for cache in self.caches:
            for value in values:
                cache.set(value, rand_string(4, 20))
            assert len(cache) == count
            assert list(cache.values()).sort() == values.sort()

        # assert list(cache.values(tag='not-exited-tag')) == []
        # assert list(cache.values(tag=None)) != []
    
    # def test_items(self):
    #     count = 104
    #     keys = list(rand_strings(count, 4, 20))
    #     values = list(rand_strings(count, 4, 20))
    #     for cache in self.caches:
    #         for k, v in zip(keys, values):
    #             cache.set(k, v)
    #         items_data = list(cache.items())
    #         assert len(items_data) == count 
    #         assert len(items_data[0]) == 2

    def test_memoize(self):

        import time
        for cache in self.caches:
            count = 1    
            @cache.memoize(1)
            def cal():
                nonlocal count
                count += 1
                return count

            assert cal() == 2
            assert cal() == 2
            assert cal() == 2
            time.sleep(1)
            assert cal() == 3
