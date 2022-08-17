#!/usr/bin/env python

# from src.parser import parser
from src.speech_parser_with_mdbs import parse_speeches
from src.mdb_parser import parse_mdb_data

parse_mdb_data()
parse_speeches()
