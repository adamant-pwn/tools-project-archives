import pytest
import os
import sys
import time
import filecmp
import re
from pathlib import Path

# sys.path.append(os.path.abspath('./archiver/'))
# run tests in project root using: python3 -m pytest

from archiver.archive import create_archive
from archiver.extract import extract_archive
from archiver.listing import create_listing
from archiver.integrity import check_integrity


def test_create_archive(tmp_path):
    folder_path = get_folder_path()
    archive_path = get_archive_path()

    tmp_path = tmp_path.joinpath("go-here")

    create_archive(folder_path, tmp_path, None, 5)

    dir_listing = os.listdir(tmp_path)

    # Test if all files exist
    expected_listing = ['test-folder.tar.lst', 'test-folder.tar.lz.md5', 'test-folder.md5', 'test-folder.tar.lz', 'test-folder.tar.md5']
    assert compare_array_content_ignoring_order(dir_listing, expected_listing)

    # Test listing of tar
    assert compare_listing_files(archive_path.joinpath("test-folder.tar.lst"), tmp_path.joinpath("test-folder.tar.lst"))

    # Test md5 hash validity for tar
    assert valid_md5_hash_in_file(tmp_path.joinpath("test-folder.tar.md5"))

    # Test md5 hash validity for tar.lz
    assert valid_md5_hash_in_file(tmp_path.joinpath("test-folder.tar.lz.md5"))

    # Assert content md5 of archive content
    assert compare_text_file(archive_path.joinpath("test-folder.md5"), tmp_path.joinpath("test-folder.md5"))


def test_extract_archive(tmp_path):
    # access existing archive dir
    archive_path = get_archive_path()
    folder_path = get_folder_path()
    extraction_path = tmp_path

    # wait until this aciton has completed
    extract_archive(archive_path, extraction_path)
    # TODO: Find fix for this
    time.sleep(0.1)

    dir_listing = os.listdir(extraction_path)

    # assert listing of extracted folder
    assert dir_listing == ["test-folder"]

    # assert content of extracted file
    assert filecmp.cmp(folder_path.joinpath("folder-in-archive/file2.txt"), tmp_path.joinpath("test-folder/folder-in-archive/file2.txt"))


def test_list_archive_content(capsys):
    archive_dir = get_archive_path()

    create_listing(archive_dir)

    captured_std_out = capsys.readouterr().out

    with open(archive_dir.joinpath("test-folder.tar.lst"), "r") as file:
        assert compare_listing_text(captured_std_out, file.read())


def test_list_archive_content_deep(capsys):
    archive_dir = get_archive_path()

    create_listing(archive_dir, None, True)

    captured_std_out = capsys.readouterr().out

    with open(archive_dir.joinpath("test-folder.tar.lst"), "r") as file:
        assert compare_listing_text(captured_std_out, file.read())


def test_list_archive_content_subpath(capsys):
    archive_dir = get_archive_path()
    tests_dir = get_test_ressources_path()

    create_listing(archive_dir, "test-folder/folder-in-archive")

    captured_std_out = capsys.readouterr().out

    with open(tests_dir.joinpath("listing-partial.lst"), "r") as file:
        assert compare_listing_text(captured_std_out, file.read())


def test_list_archive_content_subpath_deep(capsys):
    archive_dir = get_archive_path()
    tests_dir = get_test_ressources_path()

    create_listing(archive_dir, "test-folder/folder-in-archive", True)

    captured_std_out = capsys.readouterr().out

    with open(tests_dir.joinpath("listing-partial.lst"), "r") as file:
        assert compare_listing_text(captured_std_out, file.read())


def test_integrity_check_shallow(capsys):
    archive_dir = get_archive_path()

    check_integrity(archive_dir)

    captured_std_out = capsys.readouterr().out

    assert captured_std_out == "Starting integrity check...\nIntegrity check successful\n"


def test_integrity_check_shallow_corrupted(capsys):
    archive_dir = get_corrupted_archive_path()

    check_integrity(archive_dir)

    captured_std_out = capsys.readouterr().out

    expected_string = "Starting integrity check...\nIntegrity check unsuccessful. Archive has been changed since creation.\n"

    assert captured_std_out == expected_string


def test_integrity_check_deep(capsys):
    archive_dir = get_archive_path()

    check_integrity(archive_dir, True)

    captured_std_out = capsys.readouterr().out

    assert captured_std_out.startswith("Starting integrity check...") and captured_std_out.endswith("Deep integrity check successful\n")


def test_integrity_check_deep_corrupted(capsys):
    archive_dir = get_corrupted_archive_path()

    check_integrity(archive_dir)

    captured_std_out = capsys.readouterr().out

    expected_string_deep = "Starting integrity check...\nDeep integrity check unsuccessful. Archive has been changed since creation.\n"
    expected_string_shallow = "Starting integrity check...\nIntegrity check unsuccessful. Archive has been changed since creation.\n"

    assert captured_std_out == expected_string_deep or captured_std_out == expected_string_shallow


# MARK: Helpers

def get_test_ressources_path():
    """Get path of test directory"""
    return Path(os.path.dirname(os.path.realpath(__file__))).joinpath("test-ressources")


def get_archive_path():
    """Get path of archive used for tests"""
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    return Path(os.path.join(dir_path, "test-ressources/test-archive"))


def get_corrupted_archive_path():
    """Get path of corrupted archive used for tests"""
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    return Path(os.path.join(dir_path, "test-ressources/test-archive-corrupted"))


def get_folder_path():
    """Get path of folder for creating test archive"""
    dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
    return Path(os.path.join(dir_path, "test-ressources/test-folder"))


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

    return compare_array_content_ignoring_order(listing_a_path_array, listing_b_path_array)


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


def compare_array_content_ignoring_order(array_a, array_b):
    """Works for arrays that can be sorted"""
    return sorted(array_a) == sorted(array_b)


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
