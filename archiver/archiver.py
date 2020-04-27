import os
import subprocess
import hashlib
from pathlib import Path

import helpers


def archive(args):
    # Path to a file or directory which will be archives
    source_path = Path(args.source)
    # Path to a directory which will be created (if it does yet exist)
    destination_path = Path(args.archive_dir)

    # Argparse already checks if arguments are present, so only argument format needs to be validated
    helpers.terminate_if_path_nonexistent(source_path)

    # Check if destination parent directory exist but not actual directory
    helpers.terminate_if_partent_directory_nonexistent(destination_path)
    helpers.terminate_if_path_exists(destination_path)

    source_name = source_path.name

    destination_path.mkdir()
    create_file_listing_hash(source_path, destination_path, source_name)
    create_tar_archive(source_path, destination_path, source_name)
    create_archive_listing(destination_path, source_name)
    compress_using_lzip(destination_path, source_name)
    create_archive_hash(destination_path, source_name)

    print("Archive created: " + destination_path.absolute().as_posix())


# TODO: parallelization
def create_file_listing_hash(source_path, destination_path, source_name):
    for root, _, files in os.walk(source_path):
        hashes = []
        for file in files:
            # Read file content as binary for hash
            with open(os.path.join(root, file), "rb") as read_file:
                hashes.append([root, file, hashlib.md5(read_file.read()).hexdigest()])

        write_hash_list_to_file(Path.joinpath(destination_path, source_name + ".md5"), hashes)


def create_tar_archive(source_path, destination_path, source_name):
    path = Path.joinpath(destination_path, source_name + ".tar")
    subprocess.run(["tar", "-cf", path, source_path])


def create_archive_listing(destination_path, source_name):
    listing_path = Path.joinpath(destination_path, source_name + ".tar.lst")
    tar_path = Path.joinpath(destination_path, source_name + ".tar")

    archive_listing_file = open(listing_path, "w")
    subprocess.run(["tar", "-tvf", tar_path], stdout=archive_listing_file)


def compress_using_lzip(destination_path, source_name):
    path = Path.joinpath(destination_path, source_name + ".tar")
    subprocess.run(["plzip", path])


def create_archive_hash(destination_path, source_name):
    path = Path.joinpath(destination_path, source_name + ".tar.lz")

    hasher = hashlib.md5()
    # Read file content as binary for hash
    with open(path, 'rb') as read_file:
        buf = read_file.read()
        hasher.update(buf)

    hash_file = open(Path.joinpath(destination_path, source_name + ".tar.lz.md5"), "w")
    hash_file.write(hasher.hexdigest())


def write_hash_list_to_file(file_path, hashes):
    hash_file = open(file_path, "a")
    for file in hashes:
        path = os.path.join(file[0], file[1])
        hash_file.write(file[2] + " " + path + "\n")