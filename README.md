# gkeep-fuse

FUSE interface for [Google Keep](https://www.google.com/keep/).  Currently
supports listing, creating, reading, writing, renaming, and removing notes.

## Installation

```
pip install -r requirements.txt
```

## Usage

```
 export GOOGLE_KEEP_USER=yourname@gmail.com
 export GOOGLE_KEEP_PASSWORD=xxxxxxxxxxxxxxxx
./gkeep_fuse.py mnt/
```

If you use two-factor authentication you should use an
[app password](https://myaccount.google.com/apppasswords), see
[kiwiz/gkeepapi#20](https://github.com/kiwiz/gkeepapi/issues/20).

## References

* [gkeep](https://github.com/Nekmo/gkeep) provides command-line access to Keep notes
* [gkeepapi](https://github.com/kiwiz/gkeepapi) provides Keep API access

## License

* MIT
