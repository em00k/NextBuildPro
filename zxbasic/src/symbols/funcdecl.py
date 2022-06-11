#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:et:sw=4:

# ----------------------------------------------------------------------
# Copyleft (K), Jose M. Rodriguez-Rosa (a.k.a. Boriel)
#
# This program is Free Software and is released under the terms of
#                    the GNU General License
# ----------------------------------------------------------------------
import src.api.symboltable.scope
from src.api import global_
from src.api.constants import CLASS

from src.symbols.symbol_ import Symbol
from src.symbols.function import SymbolFUNCTION


class SymbolFUNCDECL(Symbol):
    """Defines a Function or Sub declaration"""

    def __init__(self, entry, lineno):
        super(SymbolFUNCDECL, self).__init__()
        self.entry = entry  # Symbol table entry
        self.lineno = lineno  # Line of this function declaration

    @property
    def entry(self):
        return self.children[0]

    @entry.setter
    def entry(self, value):
        assert isinstance(value, SymbolFUNCTION)
        self.children = [value]

    @property
    def name(self):
        return self.entry.name

    @property
    def locals_size(self):
        return self.entry.locals_size

    @locals_size.setter
    def locals_size(self, value):
        self.entry.locals_size = value

    @property
    def local_symbol_table(self):
        return self.entry.local_symbol_table

    @local_symbol_table.setter
    def local_symbol_table(self, value):
        assert isinstance(value, src.api.symboltable.scope.Scope)
        self.entry.local_symbol_table = value

    @property
    def type_(self):
        return self.entry.type_

    @type_.setter
    def type_(self, value):
        self.entry.type_ = value

    @property
    def size(self):
        return self.type_.size

    @property
    def mangled(self):
        return self.entry.mangled

    @classmethod
    def make_node(cls, func_name: str, lineno: int, class_: CLASS, type_=None):
        """This will return a node with the symbol as a function."""
        assert class_ in (CLASS.sub, CLASS.function)
        entry = global_.SYMBOL_TABLE.declare_func(func_name, lineno, type_=type_, class_=class_)
        if entry is None:
            return None

        entry.declared = True
        return cls(entry, lineno)
