import os
import re
from pathlib import Path

from archiver.archive import create_archive
from tests.generate_folder import directory_for_splitting
from . import helpers


def test_create_archive(tmp_path):
    FOLDER_NAME = "test-folder"
    folder_path = helpers.get_folder_path()
    archive_path = helpers.get_archive_path()

    tmp_path = tmp_path.joinpath("archive-normal")

    create_archive(folder_path, tmp_path, None, 5)

    dir_listing = os.listdir(tmp_path)

    # Test if all files exist
    expected_listing = ['.tar.lst', '.tar.lz.md5', '.md5', '.tar.lz', '.tar.md5']
    expected_named_listing = add_prefix_to_list_elements(expected_listing, FOLDER_NAME)

    assert helpers.compare_array_content_ignoring_order(dir_listing, expected_named_listing)

    # Test listing of tar
    assert compare_listing_files(archive_path.joinpath(FOLDER_NAME + ".tar.lst"), tmp_path.joinpath(FOLDER_NAME + ".tar.lst"))

    # Test hash validity
    assert valid_md5_hash_in_file(tmp_path.joinpath(FOLDER_NAME + ".tar.md5"))
    assert valid_md5_hash_in_file(tmp_path.joinpath(FOLDER_NAME + ".tar.lz.md5"))

    # Test md5 of archive content
    assert compare_text_file(archive_path.joinpath(FOLDER_NAME + ".md5"), tmp_path.joinpath(FOLDER_NAME + ".md5"))


def test_create_archive_splitted(tmp_path, directory_for_splitting):
    MAX_ARCHIVE_BYTE_SIZE = 1000 * 1000 * 50
    FOLDER_NAME = "large-test-folder"

    tmp_path = tmp_path.joinpath("archive-splitted")
    archive_path = helpers.get_splitted_ressources()

    create_archive(directory_for_splitting, tmp_path, None, 5, MAX_ARCHIVE_BYTE_SIZE)

    dir_listing = os.listdir(tmp_path)

    # Test if all files exist
    expected_listing = ['.part1.tar.lst', '.part1.tar.lz.md5', '.part1.md5', '.part1.tar.lz', '.part1.tar.md5',
                        '.part2.tar.lst', '.part2.tar.lz.md5', '.part2.md5', '.part2.tar.lz', '.part2.tar.md5']

    expected_named_listing = add_prefix_to_list_elements(expected_listing, FOLDER_NAME)

    assert helpers.compare_array_content_ignoring_order(dir_listing, expected_named_listing)

    # Tar listings
    assert compare_listing_files(archive_path.joinpath(FOLDER_NAME + ".part1.tar.lst"), tmp_path.joinpath(FOLDER_NAME + ".part1.tar.lst"))
    assert compare_listing_files(archive_path.joinpath(FOLDER_NAME + ".part2.tar.lst"), tmp_path.joinpath(FOLDER_NAME + ".part2.tar.lst"))

    # Test hashes
    assert valid_md5_hash_in_file(tmp_path.joinpath(FOLDER_NAME + ".part1.tar.md5"))
    assert valid_md5_hash_in_file(tmp_path.joinpath(FOLDER_NAME + ".part2.tar.md5"))
    assert valid_md5_hash_in_file(tmp_path.joinpath(FOLDER_NAME + ".part1.tar.lz.md5"))
    assert valid_md5_hash_in_file(tmp_path.joinpath(FOLDER_NAME + ".part2.tar.lz.md5"))

    # Test md5 of archive content
    assert compare_text_file(archive_path.joinpath(FOLDER_NAME + ".part1.md5"), tmp_path.joinpath(FOLDER_NAME + ".part1.md5"))
    assert compare_text_file(archive_path.joinpath(FOLDER_NAME + ".part2.md5"), tmp_path.joinpath(FOLDER_NAME + ".part2.md5"))


# MARK: Test helpers

def add_prefix_to_list_elements(element_list, prefix):
    return list(map(lambda element_content: prefix + element_content, element_list))


def compare_text_file(file_a_path, file_b_path):
    try:
        with open(file_a_path, "r") as file1, open(file_b_path, "r") as file2:
            return file1.read().rstrip() == file2.read().rstrip()
    except:
        return False


def compare_listing_files(listing_file_path_a, listing_file_path_b):
    try:
        with open(listing_file_path_a, "r") as file1, open(listing_file_path_b, "r") as file2:
            return compare_listing_text(file1.read(), file2.read())
    except:
        return False


def compare_listing_text(listing_a, listing_b):
    listing_a_path_array = get_array_of_last_multiline_text_parts(listing_a)
    listing_b_path_array = get_array_of_last_multiline_text_parts(listing_b)

    return helpers.compare_array_content_ignoring_order(listing_a_path_array, listing_b_path_array)


def get_array_of_last_multiline_text_parts(multiline_text):
    parts_array = []

    for line in multiline_text.splitlines():
        # ignore empty lines
        try:
            path = line.split()[-1]
            parts_array.append(path)
        except:
            pass

    return parts_array


def valid_md5_hash_in_file(hash_file_path):
    """Returns true if file contains valid md5 hash"""
    try:
        with open(hash_file_path, "r") as file:
            file_content = file.read().rstrip()
            if re.search(r"([a-fA-F\d]{32})", file_content):
                return True

            return False
    except:
        return False
