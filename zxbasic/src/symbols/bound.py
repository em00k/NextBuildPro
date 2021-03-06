#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:et:sw=4:

# ----------------------------------------------------------------------
# Copyleft (K), Jose M. Rodriguez-Rosa (a.k.a. Boriel)
#
# This program is Free Software and is released under the terms of
#                    the GNU General License
# ----------------------------------------------------------------------

from src.api import check
from src.api.errmsg import error

from .symbol_ import Symbol
from .number import SymbolNUMBER
from .var import SymbolVAR


class SymbolBOUND(Symbol):
    """Defines an array bound.
    Eg.:
    DIM a(1 TO 10, 3 TO 5, 8) defines 3 bounds,
      1..10, 3..5, and 0..8
    """

    def __init__(self, lower, upper):
        if isinstance(lower, SymbolNUMBER):
            lower = lower.value
        if isinstance(upper, SymbolNUMBER):
            upper = upper.value

        assert isinstance(lower, int)
        assert isinstance(upper, int)
        assert upper >= lower >= 0

        super(SymbolBOUND, self).__init__()
        self.lower = lower
        self.upper = upper

    @property
    def count(self):
        return self.upper - self.lower + 1

    @staticmethod
    def make_node(lower, upper, lineno):
        """Creates an array bound"""
        if not check.is_static(lower, upper):
            error(lineno, "Array bounds must be constants")
            return None

        if isinstance(lower, SymbolVAR):
            lower = lower.value
            if lower is None:  # semantic error
                error(lineno, "Unknown lower bound for array dimension")
                return

        if isinstance(upper, SymbolVAR):
            upper = upper.value
            if upper is None:  # semantic error
                error(lineno, "Unknown upper bound for array dimension")
                return

        lower.value = int(lower.value)
        upper.value = int(upper.value)

        if lower.value < 0:
            error(lineno, "Array bounds must be greater than 0")
            return None

        if lower.value > upper.value:
            error(lineno, "Lower array bound must be less or equal to upper one")
            return None

        return SymbolBOUND(lower.value, upper.value)

    def __str__(self):
        if self.lower == 0:
            return "({})".format(self.upper)

        return "({} TO {})".format(self.lower, self.upper)

    def __repr__(self):
        return self.token + str(self)
