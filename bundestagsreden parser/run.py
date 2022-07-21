#!/usr/bin/env python

import sys
from src.parser import parser

#if len(sys.argv) != 2:
#    raise ValueError("Enter number of legislative Period as integer. E.g.: 19")


period = input("Select legislative period (19 or 20): ")

withcomments = input("Shall comments be included? (y or n): ")

parser(period,withcomments)