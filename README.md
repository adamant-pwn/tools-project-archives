# tools-project-archives

Simple and easy command line tool a researcher can use to archive files at the end of a project.

## Requirements

- python >= 3.6
- plzip
- gnupg

## Usage

```
$ archiver archive [src] [archive_dir] [-p --part <maximum size of each archive part>] [-n --threads] [-k --key <public key>] [-c --compression] # Create a new archive
$ archiver extract [archive_dir] [dest] [--subdir <path in archive>] [-n --threads] # Extract archive
$ archiver list [archive_dir] [<subdir>] [-d --deep] # List content of archive
$ archiver check [archive_dir] [-d --deep] # Check integrity of archive
$ archiver encrypt [archive_dir] [-k --key <public key>] # Encrypts existing archive. When creating new archive, use 'archive' command
```

### GPG encryption

All key-handling is done by the user using GPG. This tool assumes a private key to decrypt an archive exists in the GPG keychain.

### Archive Package structure

An archive generated with this CLI-Tool will constist of the following files:

- Base archive: project_name.tar.lz
- Content listing: project_name.tar.lst
- Content md5 hashes: project_name.md5
- Archive md5 hash: project_name.tar.md5
- Compressed archive hash: project_name.tar.lz.md5

## Testing

```
# run in project root
python3 -m pytest tests/ -s
```
