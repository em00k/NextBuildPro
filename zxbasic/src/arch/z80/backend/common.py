#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim ts=4:et:sw=4:ai

import math
import re

from typing import Callable, Dict, List, NamedTuple, Set

import src.api.global_ as gl
import src.api.errors
import src.arch

from src.api import global_

from src.arch.z80.backend import errors
from src.arch.z80.backend.errors import InvalidICError as InvalidIC
from src.arch.z80.backend.runtime import RUNTIME_LABELS, LABEL_REQUIRED_MODULES, NAMESPACE, Labels as RuntimeLabel


# List of modules (in alphabetical order) that, if included, should call MEM_INIT
MEMINITS = {
    "alloc.asm",
    "loadstr.asm",
    "storestr2.asm",
    "storestr.asm",
    "strcat.asm",
    "strcpy.asm",
    "string.asm",
    "strslice.asm",
}

# Internal data types definition, with its size in bytes, or -1 if it is variable (string)
# Compound types are only arrays, and have the t
YY_TYPES = {
    "u8": 1,  # 8 bit unsigned integer
    "u16": 2,  # 16 bit unsigned integer
    "u32": 4,  # 32 bit unsigned integer
    "i8": 1,  # 8 bit SIGNED integer
    "i16": 2,  # 16 bit SIGNED integer
    "i32": 4,  # 32 bit SIGNED integer
    "f16": 4,  # -32768.9999 to 32767.9999 -aprox.- fixed point decimal (step = 1/2^16)
    "f": 5,  # Floating point
}

# Matches a boolean instruction like 'equ16' or 'andi32'
RE_BOOL = re.compile(r"^(eq|ne|lt|le|gt|ge|and|or|xor|not)(([ui](8|16|32))|(f16|f|str))$")

# Marches an hexadecimal number
RE_HEXA = re.compile(r"^[0-9A-F]+$")

# (ix +/- ...) regexp
RE_IX_IDX = re.compile(r"^\([ \t]*ix[ \t]*[-+][ \t]*.+\)$")

# Label for the program START end EXIT
START_LABEL = f"{NAMESPACE}.__START_PROGRAM"
END_LABEL = f"{NAMESPACE}.__END_PROGRAM"

CALL_BACK = f"{NAMESPACE}.__CALL_BACK__"
MAIN_LABEL = f"{NAMESPACE}.__MAIN_PROGRAM__"
DATA_LABEL = global_.ZXBASIC_USER_DATA
DATA_END_LABEL = f"{DATA_LABEL}_END"

# -------------------------------------------------------
# Runtime flags. Must be initialized on each compilation
# -------------------------------------------------------

# Whether the FunctionExit scheme has been already used or not
FLAG_use_function_exit = False

# Whether an 'end' has already been emitted or not
FLAG_end_emitted = False

# This will be appended at the end of code emission (useful for lvard, for example)
AT_END = []

# A table with ASM block entered by the USER (these won't be optimized)
ASMS = {}
ASMCOUNT = 0  # ASM blocks counter

MEMORY = []  # Must be initialized by with init()

# Counter for generated labels (__LABEL0, __LABEL1, __LABELN...)
LABEL_COUNTER = 0

# Counter for generated tmp labels (__TMP0, __TMP1, __TMPN)
TMP_COUNTER = 0
TMP_STORAGES: List[str] = []

# Set containing REQUIRED libraries
REQUIRES: Set[str] = set()  # Set of required libraries (included once)

# Set containing automatic on start called routines
INITS: Set[str] = set()  # Set of INIT routines

# CONSTANT LN(2)
__LN2 = math.log(2)

# GENERATED labels __LABELXX
TMP_LABELS: Set[str] = set()


# ---------------------------------------------------------------------------------------------


class Quad:
    """Implements a Quad code instruction."""

    def __init__(self, *args):
        """Creates a quad-uple checking it has the current params.
        Operators should be passed as Quad('+', tSymbol, val1, val2)
        """
        if not args:
            raise InvalidIC("<null>")

        if args[0] not in QUADS.keys():
            errors.throw_invalid_quad_code(args[0])

        if len(args) - 1 != QUADS[args[0]].nargs:
            errors.throw_invalid_quad_params(args[0], len(args) - 1, QUADS[args[0]].nargs)

        args = tuple([str(x) for x in args])  # Convert it to strings

        self.quad = args
        self.op = args[0]

    def __str__(self):
        """String representation"""
        return str(self.quad)


class ICInfo(NamedTuple):
    nargs: int
    func: Callable[[Quad], List[str]]


# ---------------------------------------------------
#  Table describing operations
# 'OPERATOR' -> (Number of arguments, emitting func)
# ---------------------------------------------------

QUADS: Dict[str, ICInfo] = {}


# ---------------------------------------------------
# Shared functions
# ---------------------------------------------------


def log2(x: float) -> float:
    """Returns log2(x)"""
    return math.log(x) / __LN2


def is_2n(x: float) -> bool:
    """Returns true if x is an exact
    power of 2
    """
    if x < 1 or x != int(x):
        return False

    n = log2(x)
    return n == int(n)


def tmp_label() -> str:
    global LABEL_COUNTER
    global TMP_LABELS

    result = f"{gl.LABELS_NAMESPACE}.__LABEL{LABEL_COUNTER}"
    TMP_LABELS.add(result)
    LABEL_COUNTER += 1

    return result


def tmp_remove(label: str):
    if label not in TMP_STORAGES:
        raise src.api.errors.TempAlreadyFreedError(label)

    TMP_STORAGES.pop(TMP_STORAGES.index(label))


def runtime_call(label):
    assert label in RUNTIME_LABELS, f"Invalid runtime label '{label}'"
    if label in LABEL_REQUIRED_MODULES:
        REQUIRES.add(LABEL_REQUIRED_MODULES[label])

    return f"call {label}"


# ------------------------------------------------------------------
# Operands checking
# ------------------------------------------------------------------


def is_int(op):
    """Returns True if the given operand (string)
    contains an integer number
    """
    try:
        int(op)
        return True

    except ValueError:
        pass

    return False


def is_float(op):
    """Returns True if the given operand (string)
    contains a floating point number
    """
    try:
        float(op)
        return True

    except ValueError:
        pass

    return False


def _int_ops(op1, op2, swap=True):
    """Receives a list with two strings (operands).
    If none of them contains integers, returns None.
    Otherwise, returns a t-uple with (op[0], op[1]),
    where op[1] is the integer one (the list is swapped)
    unless swap is False (e.g. sub and div used this
    because they're not commutative).

    The integer operand is always converted to int type.
    """
    if is_int(op1):
        if swap:
            return op2, int(op1)
        else:
            return int(op1), op2

    if is_int(op2):
        return op1, int(op2)

    return None


def _f_ops(op1, op2, swap=True):
    """Receives a list with two strings (operands).
    If none of them contains integers, returns None.
    Otherwise, returns a t-uple with (op[0], op[1]),
    where op[1] is the integer one (the list is swapped)
    unless swap is False (e.g. sub and div used this
    because they're not commutative).

    The integer operand is always converted to int type.
    """
    if is_float(op1):
        if swap:
            return op2, float(op1)
        else:
            return float(op1), op2

    if is_float(op2):
        return op1, float(op2)

    return None


def is_int_type(stype: str) -> bool:
    """Returns whether a given type is integer"""
    return stype[0] in ("u", "i")


def init():
    global LABEL_COUNTER
    global TMP_COUNTER
    global ASMCOUNT
    global FLAG_end_emitted
    global FLAG_use_function_exit

    LABEL_COUNTER = 0
    TMP_COUNTER = 0
    ASMCOUNT = 0

    MEMORY.clear()
    TMP_STORAGES.clear()
    REQUIRES.clear()
    INITS.clear()
    TMP_LABELS.clear()
    ASMS.clear()
    AT_END.clear()

    FLAG_use_function_exit = False
    FLAG_end_emitted = False


# ------------------------------------------------------------------
# Typecast conversions
# ------------------------------------------------------------------


def get_bytes(elements: List[str]) -> List[str]:
    """Returns a list a default set of bytes/words in hexadecimal
    (starting with an hex number) or literals (starting with #).
    Numeric values with more than 2 digits represents a WORD (2 bytes) value.
    E.g. '01' => 01h, '001' => 1, 0 bytes (0001h)
    Literal values starts with # (1 byte) or ## (2 bytes)
    E.g. '#label + 1' => (label + 1) & 0xFF
         '##(label + 1)' => (label + 1) & 0xFFFF
    """
    output = []

    for x in elements:
        if x.startswith("##"):  # 2-byte literal
            output.append("({}) & 0xFF".format(x[2:]))
            output.append("(({}) >> 8) & 0xFF".format(x[2:]))
            continue

        if x.startswith("#"):  # 1-byte literal
            output.append("({}) & 0xFF".format(x[1:]))
            continue

        # must be an hex number
        assert RE_HEXA.match(x), 'expected an hex number, got "%s"' % x
        output.append("%02X" % int(x[-2:], 16))
        if len(x) > 2:
            output.append("%02X" % int(x[-4:-2:], 16))

    return output


def get_bytes_size(elements: List[str]) -> int:
    """Defines a memory space with a default set of bytes/words in hexadecimal
    (starting with an hex number) or literals (starting with #).
    Numeric values with more than 2 digits represents a WORD (2 bytes) value.
    E.g. '01' => 01h, '001' => 1, 0 bytes (0001h)
    Literal values starts with # (1 byte) or ## (2 bytes)
    E.g. '#label + 1' => (label + 1) & 0xFF
         '##(label + 1)' => (label + 1) & 0xFFFF
    """
    return len(get_bytes(elements))


def to_byte(stype):
    """Returns the instruction sequence for converting from
    the given type to byte.
    """
    output = []

    if stype in ("i8", "u8"):
        return []

    if is_int_type(stype):
        output.append("ld a, l")
    elif stype == "f16":
        output.append("ld a, e")
    elif stype == "f":  # Converts C ED LH to byte
        output.append(runtime_call(RuntimeLabel.FTOU32REG))
        output.append("ld a, l")

    return output


def to_word(stype):
    """Returns the instruction sequence for converting the given
    type stored in DE,HL to word (unsigned) HL.
    """
    output = []  # List of instructions

    if stype == "u8":  # Byte to word
        output.append("ld l, a")
        output.append("ld h, 0")

    elif stype == "i8":  # Signed byte to word
        output.append("ld l, a")
        output.append("add a, a")
        output.append("sbc a, a")
        output.append("ld h, a")

    elif stype == "f16":  # Must MOVE HL into DE
        output.append("ex de, hl")

    elif stype == "f":
        output.append(runtime_call(RuntimeLabel.FTOU32REG))

    return output


def to_long(stype):
    """Returns the instruction sequence for converting the given
    type stored in DE,HL to long (DE, HL).
    """
    output = []  # List of instructions

    if stype in ("i8", "u8", "f16"):  # Byte to word
        output = to_word(stype)

        if stype != "f16":  # If its a byte, just copy H to D,E
            output.append("ld e, h")
            output.append("ld d, h")

    if stype in ("i16", "f16"):  # Signed byte or fixed to word
        output.append("ld a, h")
        output.append("add a, a")
        output.append("sbc a, a")
        output.append("ld e, a")
        output.append("ld d, a")

    elif stype == "u16":
        output.append("ld de, 0")

    elif stype == "f":
        output.append(runtime_call(RuntimeLabel.FTOU32REG))

    return output


def to_fixed(stype):
    """Returns the instruction sequence for converting the given
    type stored in DE,HL to fixed DE,HL.
    """
    output = []  # List of instructions

    if is_int_type(stype):
        output = to_word(stype)
        output.append("ex de, hl")
        output.append("ld hl, 0")  # 'Truncate' the fixed point
    elif stype == "f":
        output.append(runtime_call(RuntimeLabel.FTOF16REG))

    return output


def to_float(stype: str) -> List[str]:
    """Returns the instruction sequence for converting the given
    type stored in DE,HL to fixed DE,HL.
    """
    output: List[str] = []  # List of instructions

    if stype == "f":
        return output  # Nothing to do

    if stype == "f16":
        output.append(runtime_call(RuntimeLabel.F16TOFREG))
        return output

    # If we reach this point, it's an integer type
    if stype == "u8":
        output.append(runtime_call(RuntimeLabel.U8TOFREG))
    elif stype == "i8":
        output.append(runtime_call(RuntimeLabel.I8TOFREG))
    else:
        output = to_long(stype)
        if stype in ("i16", "i32"):
            output.append(runtime_call(RuntimeLabel.I32TOFREG))
        else:
            output.append(runtime_call(RuntimeLabel.U32TOFREG))

    return output


def new_ASMID():
    """Returns a new unique ASM block id"""

    result = "##ASM%i" % src.arch.z80.backend.common.ASMCOUNT
    src.arch.z80.backend.common.ASMCOUNT += 1
    return result
