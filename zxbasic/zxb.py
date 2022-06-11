#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:et:

import sys

from src import zxbc

if __name__ == "__main__":
    print("-" * 48 + "\n* WARNING: zxb is deprecated! Use zxbc instead *\n" + "-" * 48, file=sys.stderr)
    sys.exit(zxbc.main())  # Exit
