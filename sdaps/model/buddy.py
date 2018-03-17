# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright(C) 2008, Benjamin Berg <benjamin@sipsolutions.net>
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

'''
    sdaps - scripts for data acquisition with paper based surveys

    model/buddy - Registration center for buddies


Defining a buddy
================

    from sdaps import model

    class QObject(model.buddy.Buddy):

        __metaclass__ = model.buddy.Register
        obj_class = object class
        name = 'my_buddy'

    The buddy will be available as object.my_buddy

    Inside buddy class, the object is available as self.obj

'''


class Object(object):
    '''class which can have buddies'''

    def get_buddy(self, name):
        try:
            return getattr(self, '_%s_object_' % name)
        except AttributeError:
            setattr(self, '_%s_object_' % name, getattr(self, '_%s_class_' % name)(self))
            return getattr(self, '_%s_object_' % name)


class Register(type):
    '''metaclass to register the class as a buddy'''

    def __init__(cls, name, bases, dict):
        type.__init__(cls, name, bases, dict)
        assert issubclass(cls.obj_class, Object)
        setattr(
            cls.obj_class,
            '_%s_class_' % cls.name,
            cls
        )
        setattr(
            cls.obj_class,
            cls.name,
            property(lambda self: self.get_buddy(cls.name))
        )


class Buddy(object, metaclass=Register):
    '''base class for buddies'''
    obj_class = Object
    name = 'my_buddy'

    def __init__(self, obj):
        if 0:
            assert isinstance(obj, self.obj_class)
        self.obj = obj

