# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2018, Benjamin Berg <benjamin@sipsolutions.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from types import ModuleType


def toJson(obj):

    if hasattr(obj, '__slots__'):
        res = dict()
        for slot in getattr(obj, '__slots__'):
            res[slot] = getattr(obj, slot)

    else:
        if hasattr(obj, '_save_attrs'):
            attrs = getattr(obj, '_save_attrs')
            res = dict()
            for attr in attrs:
                res[attr] = getattr(obj, attr)
        else:
            if hasattr(obj, '_save_skip'):
                skip = getattr(obj, '_save_skip')
            else:
                skip = set()

            res = obj.__dict__.copy()
            keys = list(res.keys())
            for key in keys:
               if key.startswith('_') or key in skip:
                   del res[key]

    if hasattr(obj, '__to_json_state__'):
        obj.__to_json_state__(res)

    res['_class'] = obj.__class__.__name__
    return res

def fromJson(data, module_or_class):
    if isinstance(module_or_class, ModuleType):
        cls = getattr(module_or_class, data['_class'])
    else:
        cls = module_or_class

    obj = cls.__new__(cls)
    del data['_class']

    if hasattr(cls, '__setstate__'):
        getattr(cls, '__setstate__')
        cls.__setstate__(obj, data)

    elif hasattr(obj, '__slots__'):
        for k, v in data.items():
            setattr(obj, k, v)

    else:
        obj.__dict__ = data

    return obj


