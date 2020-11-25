import subprocess
import os
import sys
from pathlib import Path
import logging

from . import helpers
from .encryption import decrypt_list_of_archives
from .constants import COMPRESSED_ARCHIVE_SUFFIX, ENCRYPTED_ARCHIVE_SUFFIX, REQUIRED_SPACE_MULTIPLIER

# Should there be a flag or automatically recongnize encrypted archives?
# Ensure gpg key is available


def decrypt_existing_archive(archive_path, destination_dir=None, remove_unencrypted=False, force=False):
    if destination_dir:
        helpers.handle_destination_directory_creation(destination_dir, force)

    if archive_path.is_dir():
        if helpers.get_files_with_type_in_directory(archive_path, COMPRESSED_ARCHIVE_SUFFIX):
            helpers.terminate_with_message("Unencrypted archvies present. Doing nothing.")

        archive_files = helpers.get_files_with_type_in_directory_or_terminate(archive_path, ENCRYPTED_ARCHIVE_SUFFIX)

        decrypt_list_of_archives(archive_files, destination_dir, delete=remove_unencrypted)
        return

    helpers.terminate_if_path_not_file_of_type(archive_path, ENCRYPTED_ARCHIVE_SUFFIX)

    logging.info("Start decryption of existing archive " + helpers.get_absolute_path_string(archive_path))
    decrypt_list_of_archives([archive_path], destination_dir, delete=remove_unencrypted)


def extract_archive(source_path, destination_directory_path, partial_extraction_path=None, threads=None, force=False, extract_at_destination=False):
    # Create destination folder if nonexistent or overwrite if --force option used
    helpers.handle_destination_directory_creation(destination_directory_path, force)

    is_encrypted = helpers.path_target_is_encrypted(source_path)
    archive_files = helpers.get_archives_from_path(source_path, is_encrypted)

    if is_encrypted:
        # It might make sense to check that enough space is available for:
        # archive encryption (encrypted archive size * multiplier) AND unencrypted archive size -> hard to estimate on encrypted archive
        # Workaround would be to require enough space for  "encrypted archive size" * 2
        ensure_sufficient_disk_capacity_for_encryption(archive_files, destination_directory_path)

        # Only pass destination path if encryption output was stored at destination
        # For example: deep integrity check should decrypt the archive in the tmp folder, in order to not touch the archive folder
        destination_path = destination_directory_path if extract_at_destination else None

        decrypt_list_of_archives(archive_files, destination_path)
        archive_files = get_archive_names_after_encryption(archive_files, destination_path)

    ensure_sufficient_disk_capacity_for_extraction(archive_files, destination_directory_path)

    if partial_extraction_path:
        partial_extraction(archive_files, destination_directory_path, partial_extraction_path)
    else:
        uncompress_and_extract(archive_files, destination_directory_path, threads)

    logging.info("Archive extracted to: " + helpers.get_absolute_path_string(destination_directory_path))
    return destination_directory_path / helpers.filename_without_extensions(source_path)


def uncompress_and_extract(archive_file_paths, destination_directory_path, threads, encrypted=False):
    for archive_path in archive_file_paths:
        logging.info(f"Extract archive {helpers.get_absolute_path_string(archive_path)}")

        additional_arguments = []

        if threads:
            additional_arguments.extend(["--threads", str(threads)])

        try:
            p1 = subprocess.Popen(["plzip", "-dc", archive_path] + additional_arguments, stdout=subprocess.PIPE)
            p2 = subprocess.Popen(["tar", "-x", "-C", destination_directory_path], stdin=p1.stdout)
            p1.stdout.close()
            p2.wait()
        except subprocess.CalledProcessError:
            helpers.terminate_with_message(f"Extraction of archive {archive_path} failed.")

        destination_directory_path_string = helpers.get_absolute_path_string(destination_directory_path)

        logging.info(f"Extracted archive {archive_path.stem} to {destination_directory_path_string}")


def partial_extraction(archive_file_paths, destination_directory_path, partial_extraction_path):
    # TODO: Make this more efficient. No need to decompress every single archive
    logging.info(f"Start extracting {partial_extraction_path} from archive...")

    for archive_path in archive_file_paths:
        subprocess.run(["tar", "-xvf", archive_path, "-C", destination_directory_path, partial_extraction_path])

        logging.info(f"Extracted {partial_extraction_path} from {archive_path.stem}")


def get_archive_names_after_encryption(archive_files, destination_path=None):
    if destination_path:
        return [destination_path / path.with_suffix("").name for path in archive_files]

    return [path.with_suffix("") for path in archive_files]


def ensure_sufficient_disk_capacity_for_extraction(archive_files, extraction_path):
    archives_total_uncompressed_byte_size = 0
    available_bytes = helpers.get_device_available_capacity_from_path(extraction_path)

    for archive_path in archive_files:
        archives_total_uncompressed_byte_size += helpers.get_uncompressed_archive_size_in_bytes(archive_path)

    # multiply by REQUIRED_SPACE_MULTIPLIER for margin
    if available_bytes < archives_total_uncompressed_byte_size * REQUIRED_SPACE_MULTIPLIER:
        helpers.terminate_with_message("Not enough space available for archive extraction.")


def ensure_sufficient_disk_capacity_for_encryption(archive_files, extraction_path):
    total_archive_byte_size = 0
    available_bytes = helpers.get_device_available_capacity_from_path(extraction_path)

    for archive_path in archive_files:
        total_archive_byte_size += helpers.get_size_of_file(archive_path)

    if available_bytes < total_archive_byte_size * REQUIRED_SPACE_MULTIPLIER:
        helpers.terminate_with_message("Not enough space available for archive encryption.")
