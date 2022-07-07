#!/usr/bin/env python

import sys
from src.parser import parser

if len(sys.argv) != 2:
    raise ValueError("Enter number of legislative Period as integer. E.g.: 19")

parser(sys.argv[1])