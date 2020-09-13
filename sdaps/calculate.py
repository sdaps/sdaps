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

"""This module contains buddy objects to calculate statistics from the data.

It is possible to search for large changes between different filters by calling
the "reference" function after a calculation. After this the significant boolean
will be set for new calculations (with different filters) if there is a large
deviation from the old value."""

import math

from sdaps import model


class Questionnaire(model.buddy.Buddy, metaclass=model.buddy.Register):

    name = 'calculate'
    obj_class = model.questionnaire.Questionnaire

    def init(self):
        """Initialize or reset the state of the calculate module."""
        self.count = 0
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.calculate.init()

    def read(self):
        """The function collects the data from a sheet. You should use
        :py:meth:`Survey.iterate` to call it for each sheet that needs to be
        counted."""
        self.count += 1
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.calculate.read()

    def calculate(self):
        """Call once after :py:meth:`Questionnaire.calculate.read` to calculate
        statistical values like the standard deviation."""
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.calculate.calculate()

    def reference(self):
        """Can be used to calculate a reference value. You can later check
        whether there was a significant difference to the previous run. The
        `significant` property will be set accordingly."""
        # iterate over qobjects
        for qobject in self.obj.qobjects:
            qobject.calculate.reference()


class QObject(model.buddy.Buddy, metaclass=model.buddy.Register):

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


class Question(QObject, metaclass=model.buddy.Register):

    name = 'calculate'
    obj_class = model.questionnaire.Question


class Choice(Question, metaclass=model.buddy.Register):
    """
    :ivar count: Number of times the question was answered.
    :ivar values: Dictionary for each box with the ratio the answer was choosen.
    :ivar significant: Whether there was a significant difference to the reference run.
    """
    name = 'calculate'
    obj_class = model.questionnaire.Choice

    def init(self):
        self.count = 0
        self.values = {box.value: 0 for box in self.obj.boxes}
        self.significant = {box.value: 0 for box in self.obj.boxes}

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

class Option(Choice, metaclass=model.buddy.Register):

    name = 'calculate'
    obj_class = model.questionnaire.Option

    def read(self):
        answer = self.obj.get_answer()

        # NOTE: We don't count invalid answers at all currently
        if answer != self.obj.value_none and answer != self.obj.value_invalid:
            self.count += 1
            self.values[answer] += 1

class Range(Option, metaclass=model.buddy.Register):
    """
    :ivar count: Number of times the question was answered.
    :ivar values: Dictionary for each box with the ratio the value was choosen.
    :ivar mean: The average value that was choosen.
    :ivar standard_deviation: The average value that was choosen.
    :ivar significant: Whether there was a significant difference to the reference run.
    """
    name = 'calculate'
    obj_class = model.questionnaire.Range

    def init(self):
        Option.init(self)

        self.significant = 0
        self.mean = 0
        self.standard_deviation = 0
        self.range_count = 0

        self.range_values = {}
        for box in self.obj.boxes[self.obj.range[0]:self.obj.range[1] + 1]:
            self.range_values[box.value] = 0

        self.range_min = min(self.range_values)
        self.range_max = max(self.range_values)

    def calculate(self):
        self.mean = 0
        self.range_count = 0

        if self.count:
            for key in self.range_values:
                self.range_count += self.values[key]

                self.range_values[key] = self.values[key]
                del self.values[key]

            for key in self.values:
                self.values[key] = self.values[key] / float(self.count)

            if self.range_count > 0:
                # First calculate the mean
                for key in self.range_values:
                    self.mean += key * self.range_values[key]
                self.mean = self.mean / float(self.range_count)

                # Now we can calculate the standard deviation
                for key in self.range_values:
                    self.standard_deviation += self.range_values[key] * pow(key - self.mean, 2)
                self.standard_deviation = math.sqrt(self.standard_deviation / float(self.range_count))

                # And finally store the percentage rather than count for each answer
                for key in self.range_values:
                    self.range_values[key] = self.range_values[key] / float(self.count)

                if hasattr(self, 'ref_count'):
                    self.significant = abs(self.mean - self.ref_mean) > 0.1


    def reference(self):
        self.ref_count = self.count
        self.ref_mean = self.mean


class Additional_FilterHistogram(Question, metaclass=model.buddy.Register):

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

