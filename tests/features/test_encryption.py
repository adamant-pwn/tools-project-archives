from archiver.archive import encrypt_existing_archive
from .archiving_helpers import add_prefix_to_list_elements, compare_listing_files, valid_md5_hash_in_file, compare_text_file_ignoring_order, compare_hash_files
from tests import helpers

import os
import shutil
import re

ENCRYPTION_PUBLIC_KEY_A = "public.gpg"
ENCRYPTION_PUBLIC_KEY_B = "public_second.pub"


def test_encrypt_regular_archive(tmp_path):
    FOLDER_NAME = "test-folder"

    archive_path = helpers.get_directory_with_name("normal-archive")
    copied_archive_path = tmp_path / FOLDER_NAME

    shutil.copytree(archive_path, copied_archive_path)

    # Get public keys
    key_directory = helpers.get_directory_with_name("encryption-keys")
    encryption_keys = [key_directory / ENCRYPTION_PUBLIC_KEY_A, key_directory / ENCRYPTION_PUBLIC_KEY_B]

    encrypt_existing_archive(copied_archive_path, encryption_keys)

    # Test if all files exist
    dir_listing = os.listdir(copied_archive_path)
    expected_listing = [".tar.lst", ".tar.lz.md5", ".md5", ".tar.lz.gpg", ".tar.lz", ".tar.lz.gpg.md5", ".tar.md5"]
    expected_named_listing = add_prefix_to_list_elements(expected_listing, FOLDER_NAME)
    helpers.compare_array_content_ignoring_order(dir_listing, expected_named_listing)

    # Test listing of tar
    compare_listing_files([archive_path.joinpath(FOLDER_NAME + ".tar.lst")], [copied_archive_path.joinpath(FOLDER_NAME + ".tar.lst")])

    # Test hash validity
    assert valid_md5_hash_in_file(copied_archive_path.joinpath(FOLDER_NAME + ".tar.md5"))
    assert valid_md5_hash_in_file(copied_archive_path.joinpath(FOLDER_NAME + ".tar.lz.md5"))
    assert valid_md5_hash_in_file(copied_archive_path.joinpath(FOLDER_NAME + ".tar.lz.gpg.md5"))

    # Test md5 of archive content
    compare_text_file_ignoring_order(archive_path.joinpath(FOLDER_NAME + ".md5"), copied_archive_path.joinpath(FOLDER_NAME + ".md5"))


def test_encrypt_regular_file(tmp_path):
    FOLDER_NAME = "test-folder"

    archive_path = helpers.get_directory_with_name("normal-archive")
    copied_archive_path = tmp_path / FOLDER_NAME
    archive_file = copied_archive_path / f"{FOLDER_NAME}.tar.lz"

    shutil.copytree(archive_path, copied_archive_path)

    # Get public keys
    key_directory = helpers.get_directory_with_name("encryption-keys")
    encryption_keys = [key_directory / ENCRYPTION_PUBLIC_KEY_A, key_directory / ENCRYPTION_PUBLIC_KEY_B]

    encrypt_existing_archive(archive_file, encryption_keys)

    # Test if all files exist
    dir_listing = os.listdir(copied_archive_path)
    expected_listing = [".tar.lst", ".tar.lz.md5", ".md5", ".tar.lz.gpg", ".tar.lz", ".tar.lz.gpg.md5", ".tar.md5"]
    expected_named_listing = add_prefix_to_list_elements(expected_listing, FOLDER_NAME)
    helpers.compare_array_content_ignoring_order(dir_listing, expected_named_listing)

    # Test listing of tar
    compare_listing_files([archive_path.joinpath(FOLDER_NAME + ".tar.lst")], [copied_archive_path.joinpath(FOLDER_NAME + ".tar.lst")])

    # Test hash validity
    assert valid_md5_hash_in_file(copied_archive_path.joinpath(FOLDER_NAME + ".tar.md5"))
    assert valid_md5_hash_in_file(copied_archive_path.joinpath(FOLDER_NAME + ".tar.lz.md5"))
    assert valid_md5_hash_in_file(copied_archive_path.joinpath(FOLDER_NAME + ".tar.lz.gpg.md5"))

    # Test md5 of archive content
    compare_text_file_ignoring_order(archive_path.joinpath(FOLDER_NAME + ".md5"), copied_archive_path.joinpath(FOLDER_NAME + ".md5"))


def test_encrypt_archive_split(tmp_path):
    FOLDER_NAME = "large-folder"

    archive_path = helpers.get_directory_with_name("split-archive")
    copied_archive_path = tmp_path / FOLDER_NAME

    shutil.copytree(archive_path, copied_archive_path)

    # Get public keys
    key_directory = helpers.get_directory_with_name("encryption-keys")
    encryption_keys = [key_directory / ENCRYPTION_PUBLIC_KEY_A, key_directory / ENCRYPTION_PUBLIC_KEY_B]

    encrypt_existing_archive(copied_archive_path, encryption_keys)

    dir_listing = os.listdir(copied_archive_path)

    # Test if all files exist
    expected_listing = [".part1.tar.lst", ".part1.tar.lz.md5", ".part1.md5", ".part1.tar.lz", ".part1.tar.lz.gpg", ".part1.tar.lz.gpg.md5", ".part1.tar.md5",
                        ".part2.tar.lst", ".part2.tar.lz.md5", ".part2.md5", ".part2.tar.lz", ".part2.tar.lz.gpg", ".part2.tar.lz.gpg.md5", ".part2.tar.md5",
                        ".part3.tar.lst", ".part3.tar.lz.md5", ".part3.md5", ".part3.tar.lz", ".part3.tar.lz.gpg", ".part3.tar.lz.gpg.md5", ".part3.tar.md5"]

    expected_named_listing = add_prefix_to_list_elements(expected_listing, FOLDER_NAME)

    # Directory listings
    helpers.compare_array_content_ignoring_order(dir_listing, expected_named_listing)

    # Tar listings
    expected_listing_file_paths = [archive_path.joinpath(FOLDER_NAME + ".part1.tar.lst"), archive_path.joinpath(FOLDER_NAME + ".part2.tar.lst")]
    actual_listing_file_paths = [copied_archive_path.joinpath(FOLDER_NAME + ".part1.tar.lst"), copied_archive_path.joinpath(FOLDER_NAME + ".part2.tar.lst")]
    compare_listing_files(expected_listing_file_paths, actual_listing_file_paths)

    # Test hashes
    assert valid_md5_hash_in_file(copied_archive_path.joinpath(FOLDER_NAME + ".part1.tar.md5"))
    assert valid_md5_hash_in_file(copied_archive_path.joinpath(FOLDER_NAME + ".part2.tar.md5"))
    assert valid_md5_hash_in_file(copied_archive_path.joinpath(FOLDER_NAME + ".part1.tar.lz.md5"))
    assert valid_md5_hash_in_file(copied_archive_path.joinpath(FOLDER_NAME + ".part2.tar.lz.md5"))

    # Test md5 of archive content
    expected_hash_file_paths = [archive_path.joinpath(FOLDER_NAME + ".part1.md5"), archive_path.joinpath(FOLDER_NAME + ".part2.md5")]
    actual_hash_file_paths = [copied_archive_path.joinpath(FOLDER_NAME + ".part1.md5"), copied_archive_path.joinpath(FOLDER_NAME + ".part2.md5")]
    compare_hash_files(expected_hash_file_paths, actual_hash_file_paths)