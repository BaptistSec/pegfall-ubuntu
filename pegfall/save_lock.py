from contextlib import contextmanager
import errno
import os
import threading
import time
_local = threading.RLock()

@contextmanager
def profile_write_lock(path, timeout=0.25):
    deadline = time.monotonic() + timeout
    if not _local.acquire(timeout=timeout):
        raise OSError(errno.EBUSY, 'Progress is being saved by another writer')
    handle = None
    locked = False
    try:
        folder = os.path.dirname(path) or '.'
        os.makedirs(folder, exist_ok=True)
        handle = open(os.fspath(path) + '.lock', 'a+b')
        if os.name == 'nt':
            import msvcrt
            if os.fstat(handle.fileno()).st_size == 0:
                handle.write(b'\x00')
                handle.flush()

            def acquire():
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)

            def release():
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            def acquire():
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            def release():
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        while True:
            try:
                acquire()
                locked = True
                break
            except OSError as exc:
                if exc.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK) and (not (os.name == 'nt' and exc.errno == 0)):
                    raise
                if time.monotonic() >= deadline:
                    raise OSError(errno.EBUSY, 'Progress is being saved by another writer') from exc
                time.sleep(min(0.01, max(0, deadline - time.monotonic())))
        yield
    finally:
        try:
            if locked:
                release()
        finally:
            if handle is not None:
                handle.close()
            _local.release()
