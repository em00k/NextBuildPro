#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4:et:sw=4:

# ----------------------------------------------------------------------
# Copyleft (K), Jose M. Rodriguez-Rosa (a.k.a. Boriel)
#
# This program is Free Software and is released under the terms of
#                    the GNU General License
# ----------------------------------------------------------------------

from typing import List

from src.api import global_
from src.api.config import OPTIONS
from src.api.constants import SCOPE
from src.api.constants import CLASS

from .symbol_ import Symbol
from .type_ import SymbolTYPE


# ----------------------------------------------------------------------
# Identifier Symbol object
# ----------------------------------------------------------------------


class SymbolVAR(Symbol):
    """Defines an VAR (Variable) symbol.
    These class and their children classes are also stored in the symbol
    table as table entries to store variable data
    """

    _class: CLASS = CLASS.unknown

    def __init__(self, varname: str, lineno: int, offset=None, type_=None, class_: CLASS = CLASS.unknown):
        super().__init__()

        self.name = varname
        self.filename = global_.FILENAME  # In which file was first used
        self.lineno = lineno  # In which line was first used
        self.class_ = class_  # variable "class": var, label, function, etc.
        self.mangled = "%s%s" % (global_.MANGLE_CHR, varname)  # This value will be overridden later
        self.declared = False  # if explicitly declared (DIM var AS <type>)
        self.type_ = type_  # if None => unknown type (yet)
        self.offset = offset  # If local variable or parameter, +/- offset from top of the stack
        self.default_value = None  # If defined, variable will be initialized with this value (Arrays = List of Bytes)
        self.scope = SCOPE.global_  # One of 'global', 'parameter', 'local'
        self.byref = False  # By default, it's a global var
        self.addr = None  # If not None, the address of this symbol (string)
        self.alias = None  # If not None, this var is an alias of another
        self.aliased_by: List[Symbol] = []  # Which variables are an alias of this one
        self._accessed = False  # Where this object has been accessed (if false it might be not compiled)
        self.caseins = OPTIONS.case_insensitive  # Whether this ID is case insensitive or not
        self._t = global_.optemps.new_t()
        self.scopeRef = None  # Must be set by the Symbol Table. PTR to the scope
        self.callable = None  # For functions, subs, arrays and strings this will be True
        self.forwarded = False  # True if declared (with DECLARE) in advance (functions or subs)

    @property
    def size(self):
        if self.type_ is None:
            return 0
        return self.type_.size

    @property
    def class_(self) -> CLASS:
        return self._class

    @class_.setter
    def class_(self, value: CLASS):
        assert isinstance(value, CLASS) and CLASS.is_valid(value)
        assert self._class == CLASS.unknown or self._class == value
        self._class = value

    @property
    def byref(self):
        return self.__byref

    @byref.setter
    def byref(self, value):
        assert isinstance(value, bool)
        self.__byref = value

    def add_alias(self, entry):
        """Adds id to the current list 'aliased_by'"""
        assert isinstance(entry, SymbolVAR)
        self.aliased_by.append(entry)

    def make_alias(self, entry):
        """Make this variable an alias of another one"""
        entry.add_alias(self)
        self.alias = entry
        self.scope = entry.scope  # Local aliases can be "global" (static)
        self.byref = entry.byref
        self.offset = entry.offset
        self.addr = entry.addr

    @property
    def is_aliased(self):
        """Return if this symbol is aliased by another"""
        return len(self.aliased_by) > 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return "ID:%s" % str(self)

    @property
    def t(self):
        # HINT: Parameters and local variables must have it's .t member as '$name'
        if self.class_ == CLASS.const:
            return str(self.value)

        if self.scope == SCOPE.global_:
            if self.class_ == CLASS.array:
                return self.data_label
            else:
                return self.mangled

        if self.type_ is None or not self.type_.is_dynamic:
            return self._t

        return "$" + self._t  # Local string variables (and parameters) use '$' (see backend)

    @property
    def type_(self):
        return self._type

    @type_.setter
    def type_(self, value):
        assert (value is None) or isinstance(value, SymbolTYPE)
        self._type = value

    @staticmethod
    def to_label(var_instance):
        """Converts a var_instance to a label one"""
        # This can be done 'cause LABEL is just a dummy descent of VAR
        assert isinstance(var_instance, SymbolVAR)
        from src.symbols import LABEL

        var_instance.__class__ = LABEL
        var_instance.class_ = CLASS.label
        var_instance._scope_owner = []
        return var_instance

    @staticmethod
    def to_function(var_instance, lineno=None, class_=CLASS.function):
        """Converts a var_instance to a function one"""
        assert isinstance(var_instance, SymbolVAR)
        from src.symbols import FUNCTION

        var_instance.__class__ = FUNCTION
        var_instance.class_ = class_
        var_instance.reset(lineno=lineno)
        return var_instance

    @staticmethod
    def to_vararray(var_instance, bounds):
        """Converts a var_instance to a var array one"""
        assert isinstance(var_instance, SymbolVAR)
        from src.symbols import BOUNDLIST
        from src.symbols import VARARRAY

        assert isinstance(bounds, BOUNDLIST)
        var_instance.__class__ = VARARRAY
        var_instance.class_ = CLASS.array
        var_instance.bounds = bounds
        return var_instance

    @property
    def value(self):
        """An alias of default value, only available is class_ is CONST"""
        assert self.class_ == CLASS.const
        if isinstance(self.default_value, SymbolVAR):
            return self.default_value.value

        return self.default_value

    @value.setter
    def value(self, val):
        assert self.class_ == CLASS.const
        self.default_value = val

    @property
    def accessed(self):
        return self._accessed

    @accessed.setter
    def accessed(self, value):
        self._accessed = bool(value)
