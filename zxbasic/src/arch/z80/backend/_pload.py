#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: et:ts=4:sw=4

# --------------------------------------------------------------
# Copyleft (k) 2008, by Jose M. Rodriguez-Rosa
# (a.k.a. Boriel, http://www.boriel.com)
#
# This module contains parameter load
# intermediate-code translations
# --------------------------------------------------------------

from typing import List

from src.arch.z80.backend.runtime import Labels as RuntimeLabel
from src.arch.z80.backend.common import is_int, runtime_call, Quad

from src.arch.z80.backend._8bit import int8, _8bit_oper
from src.arch.z80.backend._16bit import int16, _16bit_oper
from src.arch.z80.backend._32bit import _32bit_oper
from src.arch.z80.backend._f16 import _f16_oper
from src.arch.z80.backend._float import _fpush, _float_oper


def _paddr(ins: Quad) -> List[str]:
    """Returns code sequence which points to
    local variable or parameter (HL)
    """
    output = []

    oper = ins.quad[1]
    indirect = oper[0] == "*"
    if indirect:
        oper = oper[1:]

    i = int(oper)
    if i >= 0:
        i += 4  # Return Address + "push IX"

    output.append("push ix")
    output.append("pop hl")
    output.append("ld de, %i" % i)
    output.append("add hl, de")

    if indirect:
        output.append("ld e, (hl)")
        output.append("inc hl")
        output.append("ld h, (hl)")
        output.append("ld l, e")

    output.append("push hl")
    return output


def _pload(offset, size: int) -> List[str]:
    """Generic parameter loading.
    Emits output code for loading at (IX + offset).
    size = Number of bytes to load:
        1 => 8 bit value   # A register
        2 => 16 bit value / string  # HL register
        4 => 32 bit value / f16 value  # DE (HI), HL (LO) register
        5 => 40 bit value / float value  # A (exp) BC (HI), DE (LO) mantissa (as ZX Spectrum ROM)
    """
    output = []

    indirect = offset[0] == "*"
    if indirect:
        offset = offset[1:]

    i = int(offset)
    if i >= 0:  # If it is a parameter, round up to even bytes
        i += 4 + (size % 2 if not indirect else 0)  # Return Address + "push IX"

    ix_changed = (indirect or size < 5) and (abs(i) + size) > 127  # Offset > 127 bytes. Need to change IX
    if ix_changed:  # more than 1 byte
        output.append("push ix")
        output.append("ld de, %i" % i)
        output.append("add ix, de")
        i = 0
    elif size == 5:  # For floating point numbers we always use DE as IX offset
        output.append("push ix")
        output.append("pop hl")
        output.append("ld de, %i" % i)
        output.append("add hl, de")
        i = 0

    if indirect:
        output.append("ld h, (ix%+i)" % (i + 1))
        output.append("ld l, (ix%+i)" % i)

        if size == 1:
            output.append("ld a, (hl)")
        elif size == 2:
            output.append("ld c, (hl)")
            output.append("inc hl")
            output.append("ld h, (hl)")
            output.append("ld l, c")
        elif size == 4:
            output.append(runtime_call(RuntimeLabel.ILOAD32))
        else:  # Floating point
            output.append(runtime_call(RuntimeLabel.ILOADF))
    else:
        if size == 1:
            output.append("ld a, (ix%+i)" % i)
        else:
            if size <= 4:  # 16/32bit integer, low part
                output.append("ld l, (ix%+i)" % i)
                output.append("ld h, (ix%+i)" % (i + 1))

                if size > 2:  # 32 bit integer, high part
                    output.append("ld e, (ix%+i)" % (i + 2))
                    output.append("ld d, (ix%+i)" % (i + 3))

            else:  # Floating point
                output.append(runtime_call(RuntimeLabel.PLOADF))

    if ix_changed:
        output.append("pop ix")

    return output


def _pload8(ins: Quad) -> List[str]:
    """Loads from stack pointer (SP) + X, being
    X 2st parameter.

    2st operand must be a SIGNED integer.
    1nd operand cannot be an immediate nor an address, but
    can be an indirect (*) parameter, for function 'ByRef' implementation.
    """
    output = _pload(ins.quad[2], 1)
    output.append("push af")
    return output


def _pload16(ins: Quad) -> List[str]:
    """Loads from stack pointer (SP) + X, being
    X 2st parameter.

    1st operand must be a SIGNED integer.
    2nd operand cannot be an immediate nor an address.
    """
    output = _pload(ins.quad[2], 2)
    output.append("push hl")
    return output


def _pload32(ins: Quad) -> List[str]:
    """Loads from stack pointer (SP) + X, being
    X 2st parameter.

    1st operand must be a SIGNED integer.
    2nd operand cannot be an immediate nor an address.
    """
    output = _pload(ins.quad[2], 4)
    output.append("push de")
    output.append("push hl")
    return output


def _ploadf(ins: Quad) -> List[str]:
    """Loads from stack pointer (SP) + X, being
    X 2st parameter.

    1st operand must be a SIGNED integer.
    """
    output = _pload(ins.quad[2], 5)
    output.extend(_fpush())
    return output


def _ploadstr(ins: Quad) -> List[str]:
    """Loads from stack pointer (SP) + X, being
    X 2st parameter.

    1st operand must be a SIGNED integer.
    2nd operand cannot be an immediate nor an address.
    """
    output = _pload(ins.quad[2], 2)
    if ins.quad[1][0] != "$":
        output.append(runtime_call(RuntimeLabel.LOADSTR))

    output.append("push hl")
    return output


def _fploadstr(ins: Quad) -> List[str]:
    """Loads from stack pointer (SP) + X, being
    X 2st parameter.

    1st operand must be a SIGNED integer.
    Unlike ploadstr, this version does not push the result
    back into the stack.
    """
    output = _pload(ins.quad[2], 2)
    if ins.quad[1][0] != "$":
        output.append(runtime_call(RuntimeLabel.LOADSTR))

    return output


def _pstore8(ins: Quad) -> List[str]:
    """Stores 2nd parameter at stack pointer (SP) + X, being
    X 1st parameter.

    1st operand must be a SIGNED integer.
    """
    value = ins.quad[2]
    offset = ins.quad[1]
    indirect = offset[0] == "*"
    size = 0
    if indirect:
        offset = offset[1:]
        size = 1

    I = int(offset)
    if I >= 0:
        I += 4  # Return Address + "push IX"
        if not indirect:
            I += 1  # F flag ignored

    if is_int(value):
        output = []
    else:
        output = _8bit_oper(value)

    ix_changed = not (-128 + size <= I <= 127 - size)  # Offset > 127 bytes. Need to change IX
    if ix_changed:  # more than 1 byte
        output.append("push ix")
        output.append("pop hl")
        output.append("ld de, %i" % I)
        output.append("add hl, de")

    if indirect:
        if ix_changed:
            output.append("ld c, (hl)")
            output.append("inc hl")
            output.append("ld h, (hl)")
            output.append("ld l, c")
        else:
            output.append("ld h, (ix%+i)" % (I + 1))
            output.append("ld l, (ix%+i)" % I)

        if is_int(value):
            output.append("ld (hl), %i" % int8(value))
        else:
            output.append("ld (hl), a")

        return output

    # direct store
    if ix_changed:
        if is_int(value):
            output.append("ld (hl), %i" % int8(value))
        else:
            output.append("ld (hl), a")

        return output

    if is_int(value):
        output.append("ld (ix%+i), %i" % (I, int8(value)))
    else:
        output.append("ld (ix%+i), a" % I)

    return output


def _pstore16(ins: Quad) -> List[str]:
    """Stores 2nd parameter at stack pointer (SP) + X, being
    X 1st parameter.

    1st operand must be a SIGNED integer.
    """
    value = ins.quad[2]
    offset = ins.quad[1]
    indirect = offset[0] == "*"
    size = 1
    if indirect:
        offset = offset[1:]

    i = int(offset)
    if i >= 0:
        i += 4  # Return Address + "push IX"

    if is_int(value):
        output = []
    else:
        output = _16bit_oper(value)

    ix_changed = not (-128 + size <= i <= 127 - size)  # Offset > 127 bytes. Need to change IX

    if indirect:
        if is_int(value):
            output.append("ld hl, %i" % int16(value))

        output.append("ld bc, %i" % i)
        output.append(runtime_call(RuntimeLabel.PISTORE16))
        return output

    # direct store
    if ix_changed:  # more than 1 byte
        if not is_int(value):
            output.append("ex de, hl")

        output.append("push ix")
        output.append("pop hl")
        output.append("ld bc, %i" % i)
        output.append("add hl, bc")

        if is_int(value):
            v = int16(value)
            output.append("ld (hl), %i" % (v & 0xFF))
            output.append("inc hl")
            output.append("ld (hl), %i" % (v >> 8))
            return output
        else:
            output.append("ld (hl), e")
            output.append("inc hl")
            output.append("ld (hl), d")
            return output

    if is_int(value):
        v = int16(value)
        output.append("ld (ix%+i), %i" % (i, v & 0xFF))
        output.append("ld (ix%+i), %i" % (i + 1, v >> 8))
    else:
        output.append("ld (ix%+i), l" % i)
        output.append("ld (ix%+i), h" % (i + 1))

    return output


def _pstore32(ins: Quad) -> List[str]:
    """Stores 2nd parameter at stack pointer (SP) + X, being
    X 1st parameter.

    1st operand must be a SIGNED integer.
    """
    value = ins.quad[2]
    offset = ins.quad[1]
    indirect = offset[0] == "*"
    if indirect:
        offset = offset[1:]

    i = int(offset)
    if i >= 0:
        i += 4  # Return Address + "push IX"

    output = _32bit_oper(value)

    if indirect:
        output.append("ld bc, %i" % i)
        output.append(runtime_call(RuntimeLabel.PISTORE32))
        return output

    # direct store
    output.append("ld bc, %i" % i)
    output.append(runtime_call(RuntimeLabel.PSTORE32))

    return output


def _pstoref16(ins: Quad) -> List[str]:
    """Stores 2nd parameter at stack pointer (SP) + X, being
    X 1st parameter.

    1st operand must be a SIGNED integer.
    """
    value = ins.quad[2]
    offset = ins.quad[1]
    indirect = offset[0] == "*"
    if indirect:
        offset = offset[1:]

    i = int(offset)
    if i >= 0:
        i += 4  # Return Address + "push IX"

    output = _f16_oper(value)

    if indirect:
        output.append("ld bc, %i" % i)
        output.append(runtime_call(RuntimeLabel.PISTORE32))
        return output

    # direct store
    output.append("ld bc, %i" % i)
    output.append(runtime_call(RuntimeLabel.PSTORE32))

    return output


def _pstoref(ins: Quad) -> List[str]:
    """Stores 2nd parameter at stack pointer (SP) + X, being
    X 1st parameter.

    1st operand must be a SIGNED integer.
    """
    value = ins.quad[2]
    offset = ins.quad[1]
    indirect = offset[0] == "*"
    if indirect:
        offset = offset[1:]

    i = int(offset)
    if i >= 0:
        i += 4  # Return Address + "push IX"

    output = _float_oper(value)

    if indirect:
        output.append("ld hl, %i" % i)
        output.append(runtime_call(RuntimeLabel.PISTOREF))
        return output

    # direct store
    output.append("ld hl, %i" % i)
    output.append(runtime_call(RuntimeLabel.PSTOREF))

    return output


def _pstorestr(ins: Quad) -> List[str]:
    """Stores 2nd parameter at stack pointer (SP) + X, being
    X 1st parameter.

    1st operand must be a SIGNED integer.

    Note: This procedure proceeds as _pstore16, since STRINGS are 16bit pointers.
    """
    output = []
    temporal = False

    # 2nd operand first, because must go into the stack
    value = ins.quad[2]

    if value[0] == "*":
        value = value[1:]
        indirect = True
    else:
        indirect = False

    if value[0] == "_":
        output.append("ld de, (%s)" % value)

        if indirect:
            output.append(runtime_call(RuntimeLabel.LOAD_DE_DE))

    elif value[0] == "#":
        output.append("ld de, %s" % value[1:])
    else:
        output.append("pop de")
        temporal = value[0] != "$"
        if indirect:
            output.append(runtime_call(RuntimeLabel.LOAD_DE_DE))

    # Now 1st operand
    value = ins.quad[1]
    if value[0] == "*":
        value = value[1:]
        indirect = True
    else:
        indirect = False

    i = int(value)
    if i >= 0:
        i += 4  # Return Address + "push IX"

    output.append("ld bc, %i" % i)

    if not temporal:
        if indirect:
            output.append(runtime_call(RuntimeLabel.PISTORE_STR))
        else:
            output.append(runtime_call(RuntimeLabel.PSTORE_STR))
    else:
        if indirect:
            output.append(runtime_call(RuntimeLabel.PISTORE_STR2))
        else:
            output.append(runtime_call(RuntimeLabel.PSTORE_STR2))

    return output
