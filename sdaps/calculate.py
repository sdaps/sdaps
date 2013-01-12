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

u"""This module contains buddy objects to calculate statistics from the data.

It is possible to search for large changes between different filters by calling
the "reference" function after a calculation. After this the significant boolean
will be set for new calculations (with different filters) if there is a large
deviation from the old value."""

import math

from sdaps import model


class Questionnaire(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'calculate'
    obj_class = model.questionnaire.Questionnaire

    def init(self):
        self.count = 0
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.calculate.init()

    def read(self):
        self.count += 1
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.calculate.read()

    def calculate(self):
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.calculate.calculate()

    def reference(self):
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.calculate.reference()


class QObject(model.buddy.Buddy):

    __metaclass__ = model.buddy.Register
    name = 'calculate'
    obj_class = model.questionnaire.QObject

    def init(self):
        pass

    def read(self):
        pass

    def calculate(self):
        pass

    def reference(self):
        pass


class Question(QObject):

    __metaclass__ = model.buddy.Register
    name = 'calculate'
    obj_class = model.questionnaire.Question


class Choice(Question):

    __metaclass__ = model.buddy.Register
    name = 'calculate'
    obj_class = model.questionnaire.Choice

    def init(self):
        self.count = 0
        self.values = dict([(box.value, 0) for box in self.obj.boxes])
        self.significant = dict([(box.value, 0) for box in self.obj.boxes])

    def read(self):
        self.count += 1
        for item in self.obj.get_answer():
            self.values[item] += 1

    def calculate(self):
        if self.count:
            for value in self.values:
                self.values[value] = self.values[value] / float(self.count)
                if hasattr(self, 'ref_count'):
                    self.significant[value] = (
                        abs(self.values[value] - self.ref_values[value]) > 0.1)

    def reference(self):
        self.ref_count = self.count
        self.ref_values = self.values


class Mark(Question):

    __metaclass__ = model.buddy.Register
    name = 'calculate'
    obj_class = model.questionnaire.Mark

    def init(self):
        self.count = 0
        self.values = dict([(x, 0) for x in range(1, 6)])
        self.significant = 0
        self.mean = 0
        self.standard_derivation = 0

    def read(self):
        answer = self.obj.get_answer()
        if answer:
            self.count += 1
            self.values[answer] += 1

    def calculate(self):
        if self.count:
            for mark in self.values:
                self.values[mark] = self.values[mark] / float(self.count)
            self.mean = sum(
                [mark * value for mark, value in self.values.items()])
            self.standard_derivation = math.sqrt(sum([
                value * pow(mark - self.mean, 2)
                for mark, value in self.values.items()]))
            if hasattr(self, 'ref_count'):
                self.significant = abs(self.mean - self.ref_mean) > 0.1

    def reference(self):
        self.ref_count = self.count
        self.ref_mean = self.mean


class Additional_FilterHistogram(Question):

    __metaclass__ = model.buddy.Register
    name = 'calculate'
    obj_class = model.questionnaire.Additional_FilterHistogram

    def init(self):
        self.count = 0
        self.values = [0] * len(self.obj.answers)
        self.significant = [0] * len(self.obj.answers)

    def read(self):
        self.count += 1
        for i in range(len(self.obj.answers)):
            filter = clifilter.clifilter(
                self.obj.questionnaire.survey, self.obj.filters[i])
            if filter():
                self.values[i] += 1

    def calculate(self):
        if self.count:
            self.significant = dict()
            for i in range(len(self.values)):
                self.values[i] = self.values[i] / float(self.count)
                if hasattr(self, 'ref_count'):
                    self.significant[i] = (
                        abs(self.values[i] - self.ref_values[i]) > 0.1)

    def reference(self):
        self.ref_count = self.count
        self.ref_values = self.values

