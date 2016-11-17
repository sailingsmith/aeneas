#!/usr/bin/env python
# coding=utf-8

# aeneas is a Python/C library and a set of tools
# to automagically synchronize audio and text (aka forced alignment)
#
# Copyright (C) 2012-2013, Alberto Pettarin (www.albertopettarin.it)
# Copyright (C) 2013-2015, ReadBeyond Srl   (www.readbeyond.it)
# Copyright (C) 2015-2016, Alberto Pettarin (www.albertopettarin.it)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module contains the following classes:

* :class:`~aeneas.exacttiming.TimeValue`,
  a numeric type to represent time values with arbitrary precision.
* :class:`~aeneas.exacttiming.TimeInterval`,
  representing a time interval, that is,
  a pair ``(begin, end)`` of time points.
* :class:`~aeneas.exacttiming.TimeIntervalList`,
  representing a list of time intervals.

.. versionadded:: 1.5.0
"""

from __future__ import absolute_import
from __future__ import print_function
from decimal import Decimal
from decimal import InvalidOperation
import sys


PY2 = (sys.version_info[0] == 2)


class TimeValue(Decimal):
    """
    A numeric type to represent time values with arbitrary precision.
    """

    TAG = u"TimeValue"

    def __repr__(self):
        return super(TimeValue, self).__repr__().replace("Decimal", "TimeValue")

    # NOTE overriding so that the result
    #      is still an instance of TimeValue

    def __add__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__add__(self, other, context))
        return TimeValue(Decimal.__add__(self, other))

    def __div__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__div__(self, other, context))
        return TimeValue(Decimal.__div__(self, other))

    def __floordiv__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__floordiv__(self, other, context))
        return TimeValue(Decimal.__floordiv__(self, other))

    def __mod__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__mod__(self, other, context))
        return TimeValue(Decimal.__mod__(self, other))

    def __mul__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__mul__(self, other, context))
        return TimeValue(Decimal.__mul__(self, other))

    def __radd__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__radd__(self, other, context))
        return TimeValue(Decimal.__radd__(self, other))

    def __rdiv__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__rdiv__(self, other, context))
        return TimeValue(Decimal.__rdiv__(self, other))

    def __rfloordiv__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__rfloordiv__(self, other, context))
        return TimeValue(Decimal.__rfloordiv__(self, other))

    def __rmod__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__rmod__(self, other, context))
        return TimeValue(Decimal.__rmod__(self, other))

    def __rmul__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__rmul__(self, other, context))
        return TimeValue(Decimal.__rmul__(self, other))

    def __rsub__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__rsub__(self, other, context))
        return TimeValue(Decimal.__rsub__(self, other))

    def __rtruediv__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__rtruediv__(self, other, context))
        return TimeValue(Decimal.__rtruediv__(self, other))

    def __sub__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__sub__(self, other, context))
        return TimeValue(Decimal.__sub__(self, other))

    def __truediv__(self, other, context=None):
        if PY2:
            return TimeValue(Decimal.__truediv__(self, other, context))
        return TimeValue(Decimal.__truediv__(self, other))


class TimeInterval(object):
    """
    A type representing a time interval, that is,
    a pair ``(begin, end)`` of time points.

    This class has some convenience methods for calculating
    the length of interval,
    whether a given time point belongs to it, etc.

    .. versionadded:: 1.7.0

    :param begin: the begin time
    :type  begin: :class:`~aeneas.exacttiming.TimeValue`
    :param end: the end time
    :type  end: :class:`~aeneas.exacttiming.TimeValue`
    :raises TypeError: if ``begin`` or ``end`` are not instances of :class:`~aeneas.exacttiming.TimeValue`
    :raises ValueError: if ``begin`` is negative or if ``begin`` is bigger than ``end``
    """

    # Relative positions of two intervals
    # XX_Y or XX_Z or XX_WV
    # X = P (point, i.e., zero-length interval) or I (non-zero-length interval)
    # Y = L (less), C (coincide), G (greater)
    # Z = L (less), B (begin), I (inside), E (end), G (greater)
    # WV = each W and V takes value in L, C, G, B, I, E as above
    #
    # TABLE 1          |
    #        self:     *
    # other:           |
    # PP_L           * |
    # PP_C             *
    # PP_G             | *
    #                  |
    #
    #
    # TABLE 2          |
    #        self:     *
    # other:           |
    # PI_LL      ***** |
    # PI_LC        *****
    # PI_LG          *****
    # PI_CG            *****
    # PI_GG            | *****
    #                  |
    #
    #
    # TABLE 3        |   |
    #        self:   *****
    # other:         |   |
    # IP_L         * |   |
    # IP_B           *   |
    # IP_I           | * |
    # IP_E           |   *
    # IP_G           |   | *
    #                |   |
    #
    #
    # TABLE 4        |   |
    #        self:   *****
    # other:         |   |
    # II_LL   *****  |   |
    # II_LB   ********   |
    # II_LI   ********** |
    # II_LE   ************
    # II_LG   **************
    #                |   |
    #
    #
    # TABLE 5        |   |
    #        self:   *****
    # other:         |   |
    # II_BI          *** |
    # II_BE          *****
    # II_BG          *******
    #                |   |
    #
    #
    # TABLE 6        |   |
    #        self:   *****
    # other:         |   |
    # II_II          |***|
    # II_IE          | ***
    # II_IG          |  ***
    #                |   |
    #
    #
    # TABLE 7        |   |
    #        self:   *****
    # other:         |   |
    # II_EG          |   ***
    #                |   |
    #
    #
    # TABLE 8        |   |
    #        self:   *****
    # other:         |   |
    # II_GG          |   |  ***
    #                |   |
    #
    #

    RELATIVE_POSITION_PP_L = 0
    RELATIVE_POSITION_PP_C = 1
    RELATIVE_POSITION_PP_G = 2
    RELATIVE_POSITION_PI_LL = 3
    RELATIVE_POSITION_PI_LC = 4
    RELATIVE_POSITION_PI_LG = 5
    RELATIVE_POSITION_PI_CG = 6
    RELATIVE_POSITION_PI_GG = 7
    RELATIVE_POSITION_IP_L = 8
    RELATIVE_POSITION_IP_B = 9
    RELATIVE_POSITION_IP_I = 10
    RELATIVE_POSITION_IP_E = 11
    RELATIVE_POSITION_IP_G = 12
    RELATIVE_POSITION_II_LL = 13
    RELATIVE_POSITION_II_LB = 14
    RELATIVE_POSITION_II_LI = 15
    RELATIVE_POSITION_II_LE = 16
    RELATIVE_POSITION_II_LG = 17
    RELATIVE_POSITION_II_BI = 18
    RELATIVE_POSITION_II_BE = 19
    RELATIVE_POSITION_II_BG = 20
    RELATIVE_POSITION_II_II = 21
    RELATIVE_POSITION_II_IE = 22
    RELATIVE_POSITION_II_IG = 23
    RELATIVE_POSITION_II_EG = 24
    RELATIVE_POSITION_II_GG = 25

    INVERSE_RELATIVE_POSITION = {
        RELATIVE_POSITION_PP_L: RELATIVE_POSITION_PP_G,
        RELATIVE_POSITION_PP_C: RELATIVE_POSITION_PP_C,
        RELATIVE_POSITION_PP_G: RELATIVE_POSITION_PP_L,
        RELATIVE_POSITION_PI_LL: RELATIVE_POSITION_IP_G,
        RELATIVE_POSITION_PI_LC: RELATIVE_POSITION_IP_E,
        RELATIVE_POSITION_PI_LG: RELATIVE_POSITION_IP_I,
        RELATIVE_POSITION_PI_CG: RELATIVE_POSITION_IP_B,
        RELATIVE_POSITION_PI_GG: RELATIVE_POSITION_IP_L,
        RELATIVE_POSITION_IP_L: RELATIVE_POSITION_PI_GG,
        RELATIVE_POSITION_IP_B: RELATIVE_POSITION_PI_CG,
        RELATIVE_POSITION_IP_I: RELATIVE_POSITION_PI_LG,
        RELATIVE_POSITION_IP_E: RELATIVE_POSITION_PI_LC,
        RELATIVE_POSITION_IP_G: RELATIVE_POSITION_PI_LL,
        RELATIVE_POSITION_II_LL: RELATIVE_POSITION_II_GG,
        RELATIVE_POSITION_II_LB: RELATIVE_POSITION_II_EG,
        RELATIVE_POSITION_II_LI: RELATIVE_POSITION_II_IG,
        RELATIVE_POSITION_II_LE: RELATIVE_POSITION_II_IE,
        RELATIVE_POSITION_II_LG: RELATIVE_POSITION_II_II,
        RELATIVE_POSITION_II_BI: RELATIVE_POSITION_II_BG,
        RELATIVE_POSITION_II_BE: RELATIVE_POSITION_II_BE,
        RELATIVE_POSITION_II_BG: RELATIVE_POSITION_II_BI,
        RELATIVE_POSITION_II_II: RELATIVE_POSITION_II_LG,
        RELATIVE_POSITION_II_IE: RELATIVE_POSITION_II_LE,
        RELATIVE_POSITION_II_IG: RELATIVE_POSITION_II_LI,
        RELATIVE_POSITION_II_EG: RELATIVE_POSITION_II_LB,
        RELATIVE_POSITION_II_GG: RELATIVE_POSITION_II_LL,
    }

    REGULAR = 0
    """ Regular interval """

    HEAD = 1
    """ Head interval """

    TAIL = 2
    """ Tail interval """

    SILENCE = 3
    """ (Long) Silence interval """

    TAG = u"TimeInterval"

    def __init__(self, begin, end, interval_type=REGULAR):
        if not isinstance(begin, TimeValue):
            raise TypeError(u"begin is not an instance of TimeValue")
        if not isinstance(end, TimeValue):
            raise TypeError(u"end is not an instance of TimeValue")
        if begin < 0:
            raise ValueError(u"begin is negative")
        if begin > end:
            raise ValueError(u"begin is bigger than end")
        self.begin = begin
        self.end = end
        self.interval_type = interval_type

    def __eq__(self, other):
        if not isinstance(other, TimeInterval):
            return False
        return (self.begin, self.end) == (other.begin, other.end)

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        if not isinstance(other, TimeInterval):
            return False
        return (self.begin, self.end) > (other.begin, other.end)

    def __lt__(self, other):
        if not isinstance(other, TimeInterval):
            return False
        return (self.begin, self.end) < (other.begin, other.end)

    def __ge__(self, other):
        return (self > other) or (self == other)

    def __le__(self, other):
        return (self < other) or (self == other)

    def __repr__(self):
        return u"%s %s" % (self.begin, self.end)

    @property
    def length(self):
        """
        Return the length of this interval,
        that is, the difference between its end and begin values.

        :rtype: :class:`~aeneas.exacttiming.TimeValue`
        """
        return self.end - self.begin

    @property
    def has_zero_length(self):
        """
        Returns ``True`` if this interval has zero length,
        that is, if its begin and end values coincide.

        :rtype: bool
        """
        return self.end == self.begin

    def starts_at(self, time_point):
        """
        Returns ``True`` if this interval starts at the given time point.

        :param time_point: the time point to test
        :type  time_point: :class:`~aeneas.exacttiming.TimeValue`
        :raises TypeError: if ``time_point`` is not an instance of ``TimeValue``
        :rtype: bool
        """
        if not isinstance(time_point, TimeValue):
            raise TypeError(u"time_point is not an instance of TimeValue")
        return self.begin == time_point

    def ends_at(self, time_point):
        """
        Returns ``True`` if this interval ends at the given time point.

        :param time_point: the time point to test
        :type  time_point: :class:`~aeneas.exacttiming.TimeValue`
        :raises TypeError: if ``time_point`` is not an instance of ``TimeValue``
        :rtype: bool
        """
        if not isinstance(time_point, TimeValue):
            raise TypeError(u"time_point is not an instance of TimeValue")
        return self.end == time_point

    def offset(self, offset, allow_negative=False, min_begin_value=None, max_end_value=None):
        """
        Move this interval by the given shift ``offset``.

        The begin and end time points of the translated interval
        are ensured to be non-negative
        (i.e., they are maxed with ``0.000``),
        unless ``allow_negative`` is set to ``True``.

        :param offset: the shift to be applied
        :type  offset: :class:`~aeneas.exacttiming.TimeValue`
        :param allow_negative: if ``True``, allow the translated interval to have negative extrema
        :type  allow_negative: bool
        :param min_begin_value: if not ``None``, specify the minimum value for the begin of the translated interval
        :type  min_begin_value: :class:`~aeneas.exacttiming.TimeValue`
        :param max_begin_value: if not ``None``, specify the maximum value for the end of the translated interval
        :type  max_begin_value: :class:`~aeneas.exacttiming.TimeValue`
        :raises TypeError: if ``offset`` is not an instance of ``TimeValue``
        :rtype: :class:`~aeneas.exacttiming.TimeInterval`
        """
        if not isinstance(offset, TimeValue):
            raise TypeError(u"offset is not an instance of TimeValue")
        self.begin += offset
        self.end += offset
        if not allow_negative:
            self.begin = max(self.begin, TimeValue("0.000"))
            self.end = max(self.end, TimeValue("0.000"))
        if (min_begin_value is not None) and (max_end_value is not None):
            self.begin = min(max(self.begin, min_begin_value), max_end_value)
            self.end = min(self.end, max_end_value)
        return self

    def contains(self, time_point):
        """
        Returns ``True`` if this interval contains the given time point.

        :param time_point: the time point to test
        :type  time_point: :class:`~aeneas.exacttiming.TimeValue`
        :rtype: bool
        """
        if not isinstance(time_point, TimeValue):
            raise TypeError(u"time_point is not an instance of TimeValue")
        return (self.begin <= time_point) and (time_point <= self.end)

    def inner_contains(self, time_point):
        """
        Returns ``True`` if this interval contains the given time point,
        excluding its extrema (begin and end).

        :param time_point: the time point to test
        :type  time_point: :class:`~aeneas.exacttiming.TimeValue`
        :rtype: bool
        """
        if not isinstance(time_point, TimeValue):
            raise TypeError(u"time_point is not an instance of TimeValue")
        return (self.begin < time_point) and (time_point < self.end)

    def relative_position_of(self, other):
        """
        Return the position of the given other time interval,
        relative to this time interval,
        as a ``RELATIVE_POSITION_*`` constant.

        :param other: the other interval
        :type  other: :class:`~aeneas.exacttiming.TimeInterval`
        :rtype: int
        """
        if not isinstance(other, TimeInterval):
            raise TypeError(u"other is not an instance of TimeInterval")
        if self.has_zero_length:
            if other.has_zero_length:
                # TABLE 1
                if other.begin < self.begin:
                    return self.RELATIVE_POSITION_PP_L
                elif other.begin == self.begin:
                    return self.RELATIVE_POSITION_PP_C
                else:
                    # other.begin > self.begin
                    return self.RELATIVE_POSITION_PP_G
            else:
                # TABLE 2
                if other.end < self.begin:
                    return self.RELATIVE_POSITION_PI_LL
                elif other.end == self.begin:
                    return self.RELATIVE_POSITION_PI_LC
                elif other.begin < self.begin:
                    return self.RELATIVE_POSITION_PI_LG
                elif other.begin == self.begin:
                    return self.RELATIVE_POSITION_PI_CG
                else:
                    # other.begin > self.begin
                    return self.RELATIVE_POSITION_PI_GG
        else:
            if other.has_zero_length:
                # TABLE 3
                if other.begin < self.begin:
                    return self.RELATIVE_POSITION_IP_L
                elif other.begin == self.begin:
                    return self.RELATIVE_POSITION_IP_B
                elif other.begin < self.end:
                    return self.RELATIVE_POSITION_IP_I
                elif other.begin == self.end:
                    return self.RELATIVE_POSITION_IP_E
                else:
                    # other.begin > self.end
                    return self.RELATIVE_POSITION_IP_G
            else:
                if other.begin < self.begin:
                    # TABLE 4
                    if other.end < self.begin:
                        return self.RELATIVE_POSITION_II_LL
                    elif other.end == self.begin:
                        return self.RELATIVE_POSITION_II_LB
                    elif other.end < self.end:
                        return self.RELATIVE_POSITION_II_LI
                    elif other.end == self.end:
                        return self.RELATIVE_POSITION_II_LE
                    else:
                        # other.end > self.end
                        return self.RELATIVE_POSITION_II_LG
                elif other.begin == self.begin:
                    # TABLE 5
                    if other.end < self.end:
                        return self.RELATIVE_POSITION_II_BI
                    elif other.end == self.end:
                        return self.RELATIVE_POSITION_II_BE
                    else:
                        # other.end > self.end
                        return self.RELATIVE_POSITION_II_BG
                elif other.begin < self.end:
                    # TABLE 6
                    if other.end < self.end:
                        return self.RELATIVE_POSITION_II_II
                    elif other.end == self.end:
                        return self.RELATIVE_POSITION_II_IE
                    else:
                        # other.end > self.end
                        return self.RELATIVE_POSITION_II_IG
                elif other.begin == self.end:
                    # TABLE 7
                    return self.RELATIVE_POSITION_II_EG
                else:
                    # other.begin > self.end
                    # TABLE 8
                    return self.RELATIVE_POSITION_II_GG

    def relative_position_wrt(self, other):
        """
        Return the position of this interval,
        relative to the given other time interval,
        as a ``RELATIVE_POSITION_*`` constant.

        :param other: the other interval
        :type  other: :class:`~aeneas.exacttiming.TimeInterval`
        :rtype: int
        """
        return self.INVERSE_RELATIVE_POSITION[self.relative_position_of(other)]

    def intersection(self, other):
        """
        Return the intersection between this time interval
        and the given time interval, or
        ``None`` if the two intervals do not overlap.

        :rtype: :class:`~aeneas.exacttiming.TimeInterval` or ``NoneType``
        """
        relative_position = self.relative_position_of(other)
        if relative_position in [
            self.RELATIVE_POSITION_PP_C,
            self.RELATIVE_POSITION_PI_LC,
            self.RELATIVE_POSITION_PI_LG,
            self.RELATIVE_POSITION_PI_CG,
            self.RELATIVE_POSITION_IP_B,
            self.RELATIVE_POSITION_II_LB,
        ]:
            return TimeInterval(begin=self.begin, end=self.begin)
        if relative_position in [
            self.RELATIVE_POSITION_IP_E,
            self.RELATIVE_POSITION_II_EG,
        ]:
            return TimeInterval(begin=self.end, end=self.end)
        if relative_position in [
            self.RELATIVE_POSITION_II_BI,
            self.RELATIVE_POSITION_II_BE,
            self.RELATIVE_POSITION_II_II,
            self.RELATIVE_POSITION_II_IE,
        ]:
            return TimeInterval(begin=other.begin, end=other.end)
        if relative_position in [
            self.RELATIVE_POSITION_IP_I,
            self.RELATIVE_POSITION_II_LI,
            self.RELATIVE_POSITION_II_LE,
            self.RELATIVE_POSITION_II_LG,
            self.RELATIVE_POSITION_II_BG,
            self.RELATIVE_POSITION_II_IG,
        ]:
            begin = max(self.begin, other.begin)
            end = min(self.end, other.end)
            return TimeInterval(begin=begin, end=end)
        return None

    def overlaps(self, other):
        """
        Return ``True`` if the given time interval
        overlaps this time interval (possibly only at an extremum).

        :param other: the other interval
        :type  other: :class:`~aeneas.exacttiming.TimeInterval`
        :rtype: bool
        """
        return self.intersection(other) is not None

    def adjacent_before(self, other):
        """
        Return ``True`` if this time interval ends
        when the given other time interval begins.

        :param other: the other interval
        :type  other: :class:`~aeneas.exacttiming.TimeInterval`
        :rtype: bool
        """
        if not isinstance(other, TimeInterval):
            raise TypeError(u"other is not an instance of TimeInterval")
        return self.end == other.begin

    def adjacent_after(self, other):
        """
        Return ``True`` if this time interval begins
        when the given other time interval ends.

        :param other: the other interval
        :type  other: :class:`~aeneas.exacttiming.TimeInterval`
        :rtype: bool
        """
        if not isinstance(other, TimeInterval):
            raise TypeError(u"other is not an instance of TimeInterval")
        return self.begin == other.end

    def shrink(self, quantity, from_begin=True):
        if quantity <= 0:
            raise ValueError(u"quantity is not positive")
        if quantity > self.length:
            raise ValueError(u"quantity is greater than length")
        if from_begin:
            self.begin = self.end - self.length + quantity
        else:
            self.end = self.begin + self.length - quantity

    def enlarge(self, quantity, from_begin=True):
        if quantity <= 0:
            raise ValueError(u"quantity is not positive")
        if from_begin:
            self.begin -= quantity
        else:
            self.end += quantity

    def move_end_at(self, point):
        if point < self.begin:
            raise ValueError(u"point is before begin")
        length = self.length
        self.end = point
        self.begin = self.end - length

    def move_begin_at(self, point):
        if point > self.end:
            raise ValueError(u"point is after end")
        length = self.length
        self.begin = point
        self.end = self.begin + length


class TimeIntervalList(object):
    """
    A type representing a list of time intervals,
    with some constraints:

    * the begin and end time of each interval should be within the list begin and end times;
    * two time intervals can only overlap at the boundary;
    * the list is kept sorted.

    This class has some convenience methods for
    clipping, offsetting, moving time interval boundaries,
    and fixing time intervals with zero length.

    .. versionadded:: 1.7.0

    :param begin: the begin time
    :type  begin: :class:`~aeneas.exacttiming.TimeValue`
    :param end: the end time
    :type  end: :class:`~aeneas.exacttiming.TimeValue`
    :raises TypeError: if ``begin`` or ``end`` are not ``Non`` and not instances of :class:`~aeneas.exacttiming.TimeValue`
    :raises ValueError: if ``begin`` is negative or if ``begin`` is bigger than ``end``

    .. versionadded:: 1.7.0
    """

    ALLOWED_POSITIONS = [
        TimeInterval.RELATIVE_POSITION_PP_L,
        TimeInterval.RELATIVE_POSITION_PP_C,
        TimeInterval.RELATIVE_POSITION_PP_G,
        TimeInterval.RELATIVE_POSITION_PI_LL,
        TimeInterval.RELATIVE_POSITION_PI_LC,
        TimeInterval.RELATIVE_POSITION_PI_CG,
        TimeInterval.RELATIVE_POSITION_PI_GG,
        TimeInterval.RELATIVE_POSITION_IP_L,
        TimeInterval.RELATIVE_POSITION_IP_B,
        TimeInterval.RELATIVE_POSITION_IP_E,
        TimeInterval.RELATIVE_POSITION_IP_G,
        TimeInterval.RELATIVE_POSITION_II_LL,
        TimeInterval.RELATIVE_POSITION_II_LB,
        TimeInterval.RELATIVE_POSITION_II_EG,
        TimeInterval.RELATIVE_POSITION_II_GG,
    ]
    """ Allowed positions for any pair of time intervals in the list """

    TAG = u"TimeIntervalList"

    def __init__(self, begin=TimeValue("0.000"), end=None):
        if (begin is not None) and (not isinstance(begin, TimeValue)):
            raise TypeError(u"begin is not an instance of TimeValue")
        if (end is not None) and (not isinstance(end, TimeValue)):
            raise TypeError(u"end is not an instance of TimeValue")
        if (begin is not None):
            if begin < 0:
                raise ValueError(u"begin is negative")
            if (end is not None) and (begin > end):
                raise ValueError(u"begin is bigger than end")
        self.begin = begin
        self.end = end
        self.__intervals = []

    def __len__(self):
        return len(self.__intervals)

    def __getitem__(self, index):
        return self.__intervals[index]

    def __setitem__(self, index, value):
        self.__intervals[index] = value

    def _check_boundaries(self, interval):
        """
        Check that the given interval
        is within the boundaries of the list.
        Raises an error if not OK.
        """
        if not isinstance(interval, TimeInterval):
            raise TypeError(u"interval is not an instance of TimeInterval")
        if (self.begin is not None) and (interval.begin < self.begin):
            raise ValueError(u"interval.begin is before self.begin")
        if (self.end is not None) and (interval.end > self.end):
            raise ValueError(u"interval.end is after self.end")

    def _check_overlap(self, interval):
        """
        Check that the given interval does not overlap
        any existing interval in the list (except at its boundaries).
        Raises an error if not OK.
        """
        # TODO log search
        for i in self.intervals:
            rel_pos = i.relative_position_of(interval)
            if rel_pos not in self.ALLOWED_POSITIONS:
                raise ValueError(u"interval overlaps another already present interval")

    def add(self, interval, sort=True):
        """
        Add the given interval to the list (and keep the latter sorted).

        An error is raised if the interval cannot be added.

        :param interval: the interval to be added
        :type  interval: :class:`~aeneas.exacttiming.TimeInterval`
        :param bool sort: if ``True`` ensure that after the insertion the list is kept sorted
        :raises TypeError: if ``interval`` is not an instance of ``TimeInterval``
        :raises ValueError: if ``interval`` does not respect the boundaries of the list
                            or if it overlaps an existing interval
        """
        self._check_boundaries(interval)
        self._check_overlap(interval)
        # TODO log insertion
        self.__intervals.append(interval)
        if sort:
            self.__intervals = sorted(self.__intervals)

    @property
    def intervals(self):
        """
        Iterates through the intervals in the list
        (which are sorted).

        :rtype: generator of :class:`~aeneas.exacttiming.TimeInterval`
        """
        for interval in self.__intervals:
            yield interval

    def offset(self, offset):
        """
        Move all the intervals in the list by the given ``offset``.

        :param offset: the shift to be applied
        :type  offset: :class:`~aeneas.exacttiming.TimeValue`
        :raises TypeError: if ``offset`` is not an instance of ``TimeValue``
        """
        for interval in self.intervals:
            interval.offset(
                offset=offset,
                allow_negative=False,
                min_begin_value=self.begin,
                max_end_value=self.end
            )

    def fix_zero_length_intervals(self, offset=TimeValue("0.001"), min_index=None, max_index=None):
        """
        min_index included, max_index excluded.

        Note: this function assumes that intervals are consecutive.
        """
        min_index = min_index or 0
        max_index = max_index or len(self)
        i = min_index
        while i < max_index:
            if self[i].has_zero_length:
                moves = [(i, "E", offset)]
                slack = offset
                j = i + 1
                while (j < max_index) and (self[j].length < slack):
                    if self[j].has_zero_length:
                        moves.append((j, "E", offset))
                        slack += offset
                    else:
                        moves.append((j, "M", None))
                    j += 1
                fixable = True
                if (j == max_index) and (self[j - 1].end + slack <= self.end):
                    current_time = self[j - 1].end + slack
                    fixable = True
                elif j < max_index:
                    self[j].shrink(slack)
                    current_time = self[j].begin
                    fixable = True
                if fixable:
                    for index, t, q in moves[::-1]:
                        if t == "M":
                            self[index].move_end_at(current_time)
                        else:
                            self[index].move_end_at(current_time)
                            self[index].enlarge(q)
                        current_time = self[index].begin
                else:
                    # TODO log?
                    pass
                i = j - 1
            i += 1
