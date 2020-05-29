import os
from pathlib import Path

from . import helpers


def split_directory(directory_path, max_package_size):
    # all file sizes are in bytes
    current_archive = []
    archive_size = 0

    for root, dirs, files in os.walk(directory_path):
        # removing path for directory index will exclude directory content from os.walk
        # See: https://docs.python.org/3/library/os.html#os.walk
        excluded_dirs = []

        for directory in dirs:
            # if the folder fits into an archive package, the content of the folder not be looked at
            dir_path = Path(root).joinpath(directory)
            dir_size = helpers.get_size_of_path(dir_path)

            if archive_size + dir_size < max_package_size:
                current_archive.append(dir_path)
                archive_size += dir_size

                excluded_dirs.append(directory)
            # for creating new package for directory that doesn't fit in current directory
            # See commit: #22d5fb7

        dirs[:] = [dir_path for dir_path in dirs if dir_path not in excluded_dirs]

        for file in files:
            file_path = Path(root).joinpath(file)
            file_size = file_path.stat().st_size

            if archive_size + file_size < max_package_size:
                current_archive.append(file_path)
                archive_size += file_size
            elif file_size < max_package_size:
                yield current_archive

                current_archive = [file_path]
                archive_size = file_size
            else:
                raise ValueError(f"File {file_path.as_posix()} is larger than the maximum package size")

    yield current_archive
