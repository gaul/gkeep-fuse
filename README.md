# gkeep-fuse

FUSE interface for [Google Keep](https://www.google.com/keep/).  Supports
listing, creating, reading, writing, renaming, and removing notes.  Notes use
titles for the file names when present and an internal Keep identifier when
absent.

## Installation

```
pip install -r requirements.txt
```

## Usage

Create a file with your Google credentials:

```
<username> <password>
```

Then run via:

```
./gkeep_fuse.py --auth /path/to/auth.txt mnt/
```

You can also use the `GOOGLE_KEEP_USER` and `GOOGLE_KEEP_PASSWORD` environment
variables.

If you use two-factor authentication you should use an
[app password](https://myaccount.google.com/apppasswords), see
[kiwiz/gkeepapi#20](https://github.com/kiwiz/gkeepapi/issues/20).

## References

* [gkeep](https://github.com/Nekmo/gkeep) provides command-line access to Keep notes
* [gkeepapi](https://github.com/kiwiz/gkeepapi) provides Keep API access

## License

* MIT
