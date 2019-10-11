#!/usr/bin/env python3

import errno
import os
import stat

import fuse
import gkeepapi
from typing import Any, Iterator, Optional, Dict, Union
from fuse import Fuse

fuse.fuse_python_api = (0, 2)

class MyStat(fuse.Stat):
    def __init__(self) -> None:
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class GKeepFuse(Fuse):
    def __init__(self, keep: gkeepapi.Keep, *args: Any, **kwargs: str) -> None:
        super().__init__(*args, **kwargs)
        self.keep = keep
        self.buffers: Dict[str, bytearray] = {}

    def _get_note_by_path(self, path: str) -> Optional[gkeepapi.node.TopLevelNode]:
        note = self.keep.get(path[1:])
        if note is None:
            notes = self.keep.find(query=path[1:])
            for note in notes:
                if note.title == path[1:]:
                    break
        if note is not None and (not note.deleted or not note.trashed):
            return note
        return None

    def getattr(self, path: str) -> Union[int, MyStat]:
        print("getattr: " + path)
        st = MyStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
            return st

        note = self._get_note_by_path(path)
        if note is None:
            return -errno.ENOENT

        st.st_mode = stat.S_IFREG | 0o444
        st.st_nlink = 1
        st.st_size = len(bytes(note.text, 'utf-8'))
        st.st_mtime = note.timestamps.edited.timestamp()
        st.st_ctime = note.timestamps.updated.timestamp()
        return st

    def readdir(self, path: str, offset: int) -> Iterator[fuse.Direntry]:
        print("readdir: " + path)
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        for note in self.keep.all():
            if note.deleted or note.trashed:
                continue
            # TODO: use modification date instead of id?
            entry = fuse.Direntry(note.title if note.title != '' else note.id)
            yield entry

    def create(self, path: str, flags: int, mode: int) -> Optional[int]:
        print("create: " + path + " " + hex(flags) + " " + hex(mode))
        note = self._get_note_by_path(path)
        if note is None:
            note = self.keep.createNote(path[1:], "")
            self.keep.sync()
        return None

    def open(self, path: str, flags: int) -> Optional[int]:
        print("open: " + path + " " + hex(flags))
        note = self._get_note_by_path(path)
        if note is None:
            return -errno.ENOENT

        if (flags & (os.O_WRONLY | os.O_RDWR)) != 0:
            self.buffers[path] = bytearray(bytes(note.text, "utf-8"))

        return None

    def read(self, path: str, size: int, offset: int) -> Union[int, bytes]:
        print("read: " + path + " " + str(size) + " " + str(offset))
        note = self._get_note_by_path(path)
        if note is None:
            return -errno.ENOENT

        slen = len(note.text)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = bytes(note.text, 'utf-8')[offset:offset+size]
        else:
            buf = b''
        print("returning: " + str(len(buf)))
        return buf

    def unlink(self, path: str) -> Optional[int]:
        print("unlink: " + path)
        note = self._get_note_by_path(path)
        if note is None:
            return -errno.ENOENT
        note.trashed = True
        self.keep.sync()
        return None

    def rename(self, oldpath: str, newpath: str) -> Optional[int]:
        print("rename: " + oldpath + " " + newpath)
        note = self._get_note_by_path(oldpath)
        if note is None:
            return -errno.ENOENT
        note.title = newpath[1:]
        self.keep.sync()
        return None

    def truncate(self, path: str, size: int) -> Optional[int]:
        print("truncate: " + path + " " + str(size))
        self.buffers[path] = bytearray()
        return None

    def write(self, path: str, buf: bytes, offset: int) -> int:
        print("write: " + path + " " + str(len(buf)) + " " + str(offset))
        array = self.buffers.get(path, bytearray())
        if offset != len(array):
            return -errno.EINVAL
        array[offset:offset+len(buf)] = buf
        return len(buf)

    def release(self, path: str, flags: int) -> None:
        print("release: " + path + " " + hex(flags))
        buf = self.buffers.get(path)
        if buf is None:
            return
        text = str(buf, 'utf-8')
        note = self._get_note_by_path(path)
        if note is None:
            note = self.keep.createNote(path[1:], text)
        else:
            note.title = path[1:]
            note.text = text
        self.keep.sync()
        del self.buffers[path]

def main() -> None:
    USER = os.environ['GOOGLE_KEEP_USER']
    PASSWORD = os.environ['GOOGLE_KEEP_PASSWORD']

    keep = gkeepapi.Keep()
    success = keep.login(USER, PASSWORD)

    usage="""
Google Keep filesystem

""" + Fuse.fusage
    server = GKeepFuse(keep, version="%prog " + fuse.__version__, usage=usage, dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
