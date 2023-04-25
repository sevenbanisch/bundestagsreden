#!/usr/bin/env python

# from src.parser import parser
from src.mdb_parser import parse_mdb_data
from src.speech_parser_with_mdbs import parse_speeches

parse_mdb_data()
parse_speeches()
