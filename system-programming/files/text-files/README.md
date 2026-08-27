# Example: Reading and Writing Text Files (Low-level IO)

Both examples use the low-level, unbuffered file IO system calls `open()`,
`read()`, `write()`, and `close()` instead of the buffered `stdio.h`
functions.

## write.c

Opens (or creates) a file and writes a fixed text to it.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s <file>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int fd = open(argv[1], O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd == -1)
    {
        perror("open");
        exit(EXIT_FAILURE);
    }

    const char *text = "Hello, low-level IO!\nThis text was written with write().\n";
    ssize_t len = (ssize_t) strlen(text);

    ssize_t n = write(fd, text, len);
    if (n == -1)
    {
        perror("write");
        exit(EXIT_FAILURE);
    }
    if (n != len)
    {
        fprintf(stderr, "Incomplete write: %zd of %zd bytes\n", n, len);
        exit(EXIT_FAILURE);
    }

    if (close(fd) == -1)
    {
        perror("close");
        exit(EXIT_FAILURE);
    }

    return 0;
}
```

## read.c

Opens a file and reads it chunk by chunk into a buffer, writing each chunk
to standard output.

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

#define BUFFER_SIZE 1024

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s <file>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd == -1)
    {
        perror("open");
        exit(EXIT_FAILURE);
    }

    char buffer[BUFFER_SIZE];
    ssize_t n;
    while ((n = read(fd, buffer, BUFFER_SIZE)) > 0)
    {
        if (write(STDOUT_FILENO, buffer, n) != n)
        {
            perror("write");
            exit(EXIT_FAILURE);
        }
    }
    if (n == -1)
    {
        perror("read");
        exit(EXIT_FAILURE);
    }

    if (close(fd) == -1)
    {
        perror("close");
        exit(EXIT_FAILURE);
    }

    return 0;
}
```

## Build and Run

To build the examples with the help of CMake:

```bash
$ cmake -S . -B build
$ cd build/
$ make

$ ./write test.txt
$ ./read test.txt
```

## System Calls

Both programs are built on exactly four system calls: `open()`, `read()`,
`write()`, and `close()`. There is no buffering involved — every call to
`read()`/`write()` in the source is a 1:1 request to the kernel.

* **`open(const char *path, int flags, ...)`**: Asks the kernel to
  create/locate an entry in its open file table and returns the smallest
  unused **file descriptor** (a small non-negative `int`) referring to it.
  `flags` selects the access mode (`O_RDONLY`, `O_WRONLY`, `O_RDWR`) and can
  be OR'ed with behaviour flags such as `O_CREAT` (create the file if it
  does not exist), `O_TRUNC` (truncate an existing file to length 0), or
  `O_APPEND`. When `O_CREAT` is given, a third argument (the `mode`, e.g.
  `0644`) sets the permission bits of a newly created file, subject to the
  process' `umask`. On error `open()` returns `-1` and sets `errno`.
  On Linux, glibc actually implements `open()` on top of the `openat()`
  system call (visible in the `strace` output below) - `open(path, ...)` is
  equivalent to `openat(AT_FDCWD, path, ...)`.

* **`read(int fd, void *buf, size_t count)`**: Copies up to `count` bytes
  from the file/kernel buffer associated with `fd` into `buf`, advancing the
  file's read/write offset by the number of bytes actually read. It returns
  the number of bytes read, `0` at end-of-file, or `-1` on error. A short
  read (fewer bytes than requested) is normal and must be handled by the
  caller - `read.c` loops until `read()` returns `0`.

* **`write(int fd, const void *buf, size_t count)`**: Copies up to `count`
  bytes from `buf` to the file/device referred to by `fd`, advancing the
  offset accordingly, and returns the number of bytes actually written (or
  `-1` on error). Just like `read()`, a `write()` may write fewer bytes than
  requested, which is why `write.c` checks `n != len`.

* **`close(int fd)`**: Releases the file descriptor and the kernel's
  reference to the open file description. Once every process sharing the
  underlying open file description has closed it, the kernel drops it; if
  it was the last link and the file was unlinked, its data is freed.

Every process already starts with three open file descriptors, which is
why `read.c` can just write to `STDOUT_FILENO` (`1`) without opening
anything: `0` = `STDIN_FILENO`, `1` = `STDOUT_FILENO`, `2` = `STDERR_FILENO`.


### Tracing the system calls with `strace`

After building the examples, the actual system calls (and their arguments
and return values) can be observed with `strace`:

```bash
$ strace -e trace=openat,read,write,close ./write test.txt
$ strace -e trace=openat,read,write,close ./read test.txt
```

`-e trace=...`: restricts the output to the file-related system calls;
otherwise the trace would also show the dynamic linker loading `libc.so.6`
before `main()` even runs. The relevant lines for `./write test.txt` are:

```
openat(AT_FDCWD, "test.txt", O_WRONLY|O_CREAT|O_TRUNC, 0644) = 3
write(3, "Hello, low-level IO!\nThis text w"..., 57) = 57
close(3)                                = 0
```

`open()` is traced as `openat(AT_FDCWD, ...)`, and the flags/mode passed in
the source (`O_WRONLY|O_CREAT|O_TRUNC`, `0644`) show up verbatim as
arguments. It returns file descriptor `3` - `0`, `1`, and `2` are already
taken by stdin/stdout/stderr. `write()` reports it wrote all `57` bytes,
matching `strlen(text)`, and `close()` returns `0` for success.

For `./read test.txt`:

```
openat(AT_FDCWD, "test.txt", O_RDONLY)  = 3
read(3, "Hello, low-level IO!\nThis text w"..., 1024) = 57
write(1, "Hello, low-level IO!\nThis text w"..., 57) = 57
read(3, "", 1024)                       = 0
close(3)                                = 0
```

The file is opened read-only and, again, gets descriptor `3`. The first
`read()` fills the 1024-byte buffer with the 57 bytes that are actually in
the file and returns `57`; that data is then forwarded with `write(1, ...)`
to file descriptor `1` (stdout). The loop calls `read()` again, which now
returns `0` (end-of-file) with an empty buffer, causing `read.c` to exit
the `while` loop before it finally calls `close()`.
