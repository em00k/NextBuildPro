#!/usr/bin/env python3

import os

from typing import List

import src.api.config
import src.api.global_ as gl

from src import arch

from src.api.utils import open_file
from src.api.config import OPTIONS
from src.zxbc import args_parser
from src.api import errmsg
from src.api import debug
from src.zxbpp import zxbpp
from src.zxbc import zxbparser

__all__ = ["FileType", "parse_options"]


class FileType:
    ASM = "asm"
    IC = "ic"
    TAP = "tap"
    TZX = "tzx"


def parse_options(args: List[str] = None):
    """Parses command line options and setup global Options container"""
    parser = args_parser.parser()
    options = parser.parse_args(args=args)

    if os.path.isfile(options.config_file):
        if src.api.config.load_config_from_file(options.config_file, src.api.config.ConfigSections.ZXBC):
            src.api.errmsg.info(f"Config file {options.config_file} loaded")

    # ------------------------------------------------------------
    # Setting of internal parameters according to command line
    # ------------------------------------------------------------
    OPTIONS.debug_level = options.debug
    OPTIONS.optimization_level = options.optimize
    OPTIONS.output_filename = options.output_file
    OPTIONS.stderr_filename = options.stderr
    OPTIONS.array_base = options.array_base
    OPTIONS.string_base = options.string_base
    OPTIONS.sinclair = options.sinclair
    OPTIONS.heap_size = options.heap_size
    OPTIONS.memory_check = options.debug_memory
    OPTIONS.strict_bool = options.strict_bool
    OPTIONS.array_check = options.debug_array
    OPTIONS.emit_backend = options.emit_backend
    OPTIONS.enable_break = options.enable_break
    OPTIONS.explicit = options.explicit
    OPTIONS.memory_map = options.memory_map
    OPTIONS.strict = options.strict
    OPTIONS.headerless = options.headerless
    OPTIONS.zxnext = options.zxnext
    OPTIONS.expected_warnings = gl.EXPECTED_WARNINGS = options.expect_warnings
    OPTIONS.hide_warning_codes = options.hide_warning_codes

    if options.arch not in arch.AVAILABLE_ARCHITECTURES:
        parser.error(f"Invalid architecture '{options.arch}'")
        return 2

    OPTIONS.architecture = options.arch

    # region [Enable/Disable Warnings]
    enabled_warnings = set(options.enable_warning or [])
    disabled_warnings = set(options.disable_warning or [])
    duplicated_options = [f"W{x}" for x in enabled_warnings.intersection(disabled_warnings)]

    if duplicated_options:
        parser.error(f"Warning(s) {', '.join(duplicated_options)} cannot be enabled " f"and disabled simultaneously")
        return 2

    for warn_code in enabled_warnings:
        errmsg.enable_warning(warn_code)

    for warn_code in disabled_warnings:
        errmsg.disable_warning(warn_code)

    # endregion

    OPTIONS.org = OPTIONS.org if options.org is None else src.api.utils.parse_int(options.org)
    if OPTIONS.org is None:
        parser.error(f"Invalid --org option '{options.org}'")

    if options.defines:
        for i in options.defines:
            macro = list(i.split("=", 1))
            name = macro[0]
            val = "".join(macro[1:])
            OPTIONS.__DEFINES[name] = val
            zxbpp.ID_TABLE.define(name, value=val, lineno=0)

    if OPTIONS.sinclair:
        OPTIONS.array_base = 1
        OPTIONS.string_base = 1
        OPTIONS.strict_bool = True
        OPTIONS.case_insensitive = True

    OPTIONS.case_insensitive = options.ignore_case
    debug.ENABLED = OPTIONS.debug_level > 0

    if options.basic and not options.tzx and not options.tap:
        parser.error("Option --BASIC and --autorun requires --tzx or tap format")
        return 4

    if options.append_binary and not options.tzx and not options.tap:
        parser.error("Option --append-binary needs either --tap or --tzx")
        return 5

    if options.asm and options.memory_map:
        parser.error("Option --asm and --mmap cannot be used together")
        return 6

    OPTIONS.use_basic_loader = options.basic
    OPTIONS.autorun = options.autorun

    if options.tzx:
        OPTIONS.output_file_type = FileType.TZX
    elif options.tap:
        OPTIONS.output_file_type = FileType.TAP
    elif options.asm:
        OPTIONS.output_file_type = FileType.ASM
    elif options.emit_backend:
        OPTIONS.output_file_type = FileType.IC

    args = [options.PROGRAM]
    if not os.path.exists(options.PROGRAM):
        parser.error("No such file or directory: '%s'" % args[0])
        return 2

    if OPTIONS.memory_check:
        OPTIONS.__DEFINES["__MEMORY_CHECK__"] = ""
        zxbpp.ID_TABLE.define("__MEMORY_CHECK__", lineno=0)

    if OPTIONS.array_check:
        OPTIONS.__DEFINES["__CHECK_ARRAY_BOUNDARY__"] = ""
        zxbpp.ID_TABLE.define("__CHECK_ARRAY_BOUNDARY__", lineno=0)

    if OPTIONS.enable_break:
        OPTIONS.__DEFINES["__ENABLE_BREAK__"] = ""
        zxbpp.ID_TABLE.define("__ENABLE_BREAK__", lineno=0)

    OPTIONS.include_path = options.include_path
    OPTIONS.input_filename = zxbparser.FILENAME = os.path.basename(args[0])

    if not OPTIONS.output_filename:
        OPTIONS.output_filename = (
            os.path.splitext(os.path.basename(OPTIONS.input_filename))[0] + os.path.extsep + OPTIONS.output_file_type
        )

    if OPTIONS.stderr_filename:
        OPTIONS.stderr = open_file(OPTIONS.stderr_filename, "wt", "utf-8")

    return options
