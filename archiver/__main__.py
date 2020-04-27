#!/usr/bin/env python3

import argparse
import sys

import archiver
import unarchiver
import listing

# Main parser
parser = argparse.ArgumentParser(prog="archiver", description='Handles the archiving of large project data')
subparsers = parser.add_subparsers(help="Available actions", required=True, dest="command")

# Archiving parser
parser_archive = subparsers.add_parser("archive", help="Create archive")
parser_archive.add_argument("source", type=str, help="Source input file or directory")
parser_archive.add_argument("archive_dir", type=str, help="Path to directory which will be created")
parser_archive.set_defaults(func=archiver.archive)

# Extraction parser
parser_extract = subparsers.add_parser("extract", help="Extract archive")
parser_extract.add_argument("archive_dir", type=str, help="Select source archive tar.lz file")
parser_extract.add_argument("destination", type=str, help="Path to directory where archive will be extracted")
parser_extract.add_argument("-s", "--subdir", type=str, help="Directory or file inside archive to extract")
parser_extract.set_defaults(func=unarchiver.extract)

# List parser
parser_list = subparsers.add_parser("list", help="List content of archive")
parser_list.add_argument("archive_dir", type=str, help="Select source archive directory or .tar.lz file")
parser_list.add_argument("subdir", type=str, nargs="?", help="(Optional): Select subdir as path inside of archive")
parser_list.set_defaults(func=listing.list)


args = parser.parse_args()

if args.func:
    args.func(args)
else:
    print("Unknown function call", file=sys.stderr)
