#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from archive import create_archive
from extract import extract_archive
from listing import create_listing
from integrity import check_integrity


def main():
    parsed_arguments = parse_arguments(sys.argv[1:])

    if parsed_arguments.func:
        parsed_arguments.func(parsed_arguments)
    else:
        sys.exit("Unknown function call")


def parse_arguments(args):
    # Main parser
    parser = argparse.ArgumentParser(prog="archiver", description='Handles the archiving of large project data')
    subparsers = parser.add_subparsers(help="Available actions", required=True, dest="command")

    # Archiving parser
    parser_archive = subparsers.add_parser("archive", help="Create archive")
    parser_archive.add_argument("source", type=str, help="Source input file or directory")
    parser_archive.add_argument("archive_dir", type=str, help="Path to directory which will be created")
    parser_archive.add_argument("-n", "--threads", type=int, help="Set the number of worker threads, overriding the system's default")
    parser_archive.add_argument("-c", "--compression", type=int, help="Compression level between 0 (fastest) to 9 (slowest), default is 6")
    parser_archive.set_defaults(func=handle_archive)

    # Extraction parser
    parser_extract = subparsers.add_parser("extract", help="Extract archive")
    parser_extract.add_argument("archive_dir", type=str, help="Select source archive tar.lz file")
    parser_extract.add_argument("destination", type=str, help="Path to directory where archive will be extracted")
    parser_extract.add_argument("-s", "--subpath", type=str, help="Directory or file inside archive to extract")
    parser_extract.add_argument("-n", "--threads", type=int, help="Set the number of worker threads, overriding the system's default")
    parser_extract.set_defaults(func=handle_extract)

    # List parser
    parser_list = subparsers.add_parser("list", help="List content of archive")
    parser_list.add_argument("archive_dir", type=str, help="Select source archive directory or .tar.lz file")
    parser_list.add_argument("subpath", type=str, nargs="?", help="Only list selected subpath inside archive")
    parser_list.add_argument("-d", "--deep", action="store_true", help="Query actual archive instead of relying on existing listing file")
    parser_list.set_defaults(func=handle_list)
    
    # Integrity check
    parser_list = subparsers.add_parser("check", help="Check integrity of archive")
    parser_list.add_argument("archive_dir", type=str, help="Select source archive directory or .tar.lz file")
    parser_list.set_defaults(func=handle_check)

    return parser.parse_args()


def handle_archive(args):
    # Path to a file or directory which will be archives
    source_path = Path(args.source)
    # Path to a directory which will be created (if it does yet exist)
    destination_path = Path(args.archive_dir)
    compression_level = args.compression

    if compression_level:
        create_archive(source_path, destination_path, args.threads, compression_level)
    else:
        create_archive(source_path, destination_path, args.threads)



def handle_extract(args):
    # Path to archive file *.tar.lz
    source_path = Path(args.archive_dir)
    destination_directory_path = Path(args.destination)

    extract_archive(source_path, destination_directory_path, args.subpath, args.threads)


def handle_list(args):
    # Path to archive file *.tar.lz
    source_path = Path(args.archive_dir)

    create_listing(source_path, args.subpath, args.deep)

def handle_check(args):
    # Path to archive file *.tar.lz
    source_path = Path(args.archive_dir)

    check_integrity(source_path)


if __name__ == "__main__":
    main()
