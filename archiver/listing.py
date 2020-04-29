import subprocess
from pathlib import Path

import archiver.helpers as helpers


def create_listing(source_path, subdir_path=None):
    source_file_path = ""

    if source_path.is_dir():
        source_file_path = helpers.get_file_with_type_in_directory_or_terminate(source_path, ".tar.lz")
    else:
        helpers.terminate_if_path_not_file_of_type(source_path, ".tar.lz")
        source_file_path = source_path

    if subdir_path:
        subprocess.run(["tar", "-tvf", source_file_path, subdir_path])
        return

    subprocess.run(["tar", "-tvf", source_file_path])
