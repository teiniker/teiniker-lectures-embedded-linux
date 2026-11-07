# Example: System Calls and Error Handling

The two examples show how a system call is executed and how errors are
reported:

* `syscall.c` executes the same `write()` system call in three different
  ways: through the glibc wrapper, through `syscall()`, and directly with
  the trap instruction of the CPU.
* `errors.c` provokes typical errors and shows how to handle them with
  `errno`, `perror()` and `strerror()`.

## syscall.c

```c
#define _GNU_SOURCE         /* for syscall() */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>    /* SYS_write */

static long raw_write(int fd, const void *buf, size_t count)
{
#if defined(__aarch64__)
    /* ARM64 (Raspberry Pi OS 64-bit): number in x8, arguments in x0..x5,
       trap with "svc #0", result in x0 */
    register long x8 __asm__("x8") = SYS_write;
    register long x0 __asm__("x0") = fd;
    register long x1 __asm__("x1") = (long) buf;
    register long x2 __asm__("x2") = (long) count;
    __asm__ volatile ("svc #0"
                      : "+r"(x0)
                      : "r"(x8), "r"(x1), "r"(x2)
                      : "memory");
    return x0;
#elif defined(__x86_64__)
    /* x86-64: number in rax, arguments in rdi, rsi, rdx, r10, r8, r9,
       trap with "syscall", result in rax (rcx and r11 are overwritten) */
    long ret;
    __asm__ volatile ("syscall"
                      : "=a"(ret)
                      : "a"((long) SYS_write), "D"((long) fd), "S"(buf), "d"(count)
                      : "rcx", "r11", "memory");
    return ret;
#else
#error "raw_write() is only implemented for ARM64 and x86-64"
#endif
}

int main(void)
{
    printf("SYS_write = %d\n", SYS_write);
    fflush(stdout);     /* don't mix buffered output with write() */

    const char *msg1 = "1. Hello from the write() wrapper\n";
    if (write(STDOUT_FILENO, msg1, strlen(msg1)) == -1)
    {
        perror("write");
        exit(EXIT_FAILURE);
    }

    const char *msg2 = "2. Hello from syscall(SYS_write, ...)\n";
    if (syscall(SYS_write, STDOUT_FILENO, msg2, strlen(msg2)) == -1)
    {
        perror("syscall");
        exit(EXIT_FAILURE);
    }

    const char *msg3 = "3. Hello from the trap instruction\n";
    long ret = raw_write(STDOUT_FILENO, msg3, strlen(msg3));
    if (ret < 0)
    {
        /* The kernel itself does not know errno: it returns -errno */
        fprintf(stderr, "raw_write: %s\n", strerror((int) -ret));
        exit(EXIT_FAILURE);
    }

    /* The same trap with an invalid file descriptor: no errno, just -EBADF */
    ret = raw_write(42, msg3, strlen(msg3));
    printf("raw_write(42, ...) returned %ld (%s)\n", ret, strerror((int) -ret));

    return 0;
}
```

* **`write()`**: the normal way. The glibc wrapper loads the registers,
  executes the trap instruction, and converts errors into `-1` and `errno`.

* **`syscall(SYS_write, ...)`**: a generic glibc function that takes the
  system call number as its first argument. It also sets `errno`. It is used
  for system calls without a glibc wrapper.

* **`raw_write()`**: does what the wrapper does internally, using **inline
  assembly**. The `register ... __asm__("x8")` variables place the values in
  the registers required by the ARM64 calling convention, and `svc #0`
  switches to the kernel. The result comes back in `x0`. Since there is no
  wrapper, an error is not reported via `errno`, but as a **negative error
  code**: `raw_write(42, ...)` returns `-9`, i.e. `-EBADF`.

  The x86-64 variant is included so that the example can also be built on a
  PC. The register constraints `"a"`, `"D"`, `"S"`, `"d"` stand for `rax`,
  `rdi`, `rsi` and `rdx`.

> Inline assembly is used here to make the mechanism visible. In real
> programs, always use the glibc wrappers.


## errors.c

```c
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int write_all(int fd, const void *buf, size_t count)
{
    const char *p = buf;

    while (count > 0)
    {
        ssize_t n = write(fd, p, count);
        if (n == -1)
        {
            if (errno == EINTR)
                continue;       /* interrupted before anything was written: retry */
            return -1;          /* real error: errno is set by write() */
        }
        p += n;
        count -= (size_t) n;
    }
    return 0;
}

static void try_open(const char *path)
{
    int fd = open(path, O_RDONLY);
    if (fd == -1)
    {
        /* Save errno immediately: the next library call may change it */
        int err = errno;
        printf("open(\"%s\") = -1, errno = %d (%s)\n", path, err, strerror(err));
        return;
    }
    printf("open(\"%s\") = %d\n", path, fd);
    close(fd);
}

int main(void)
{
    try_open("/etc/hostname");      /* OK */
    try_open("/no/such/file");      /* ENOENT: No such file or directory */
    try_open("/etc/shadow");        /* EACCES: Permission denied (if not root) */

    /* EBADF: file descriptor 42 is not open */
    if (close(42) == -1)
        perror("close(42)");        /* prints "close(42): Bad file descriptor" */

    fflush(stdout);     /* don't mix buffered printf() output with write() */
    const char *text = "write_all() wrote this line\n";
    if (write_all(STDOUT_FILENO, text, strlen(text)) == -1)
    {
        perror("write_all");
        exit(EXIT_FAILURE);
    }

    return 0;
}
```

* **`try_open()`** saves `errno` in a local variable right after the failed
  `open()`, before calling `printf()`, which could change `errno`.
* **`perror()`** prints the given text, a colon, and the message for the
  current `errno` to `stderr`.
* **`write_all()`** handles partial writes and `EINTR` (see
  [Error Handling](../README.md#error-handling)).


## Build and Run

To build the examples with the help of CMake:

```bash
$ cmake -S . -B build
$ cd build/
$ make
```

On a Raspberry Pi (ARM64):

```bash
$ ./syscall
SYS_write = 64
1. Hello from the write() wrapper
2. Hello from syscall(SYS_write, ...)
3. Hello from the trap instruction
raw_write(42, ...) returned -9 (Bad file descriptor)
```

On an x86-64 PC, the first line is `SYS_write = 1`; everything else is the
same.

```bash
$ ./errors
open("/etc/hostname") = 3
open("/no/such/file") = -1, errno = 2 (No such file or directory)
open("/etc/shadow") = -1, errno = 13 (Permission denied)
close(42): Bad file descriptor
write_all() wrote this line
```


## Tracing the System Calls

`strace` shows that all three variants in `syscall.c` result in the same
`write` system call, and it shows the error returned by the kernel:

```bash
$ strace -e trace=write ./syscall > /dev/null
write(1, "SYS_write = 64\n", 15)        = 15
write(1, "1. Hello from the write() wrappe"..., 34) = 34
write(1, "2. Hello from syscall(SYS_write,"..., 38) = 38
write(1, "3. Hello from the trap instructi"..., 35) = 35
write(42, "3. Hello from the trap instructi"..., 35) = -1 EBADF (Bad file descriptor)
write(1, "raw_write(42, ...) returned -9 ("..., 53) = 53
+++ exited with 0 +++
```

`ltrace` only shows the first two variants, because the trap instruction is
not a library call:

```bash
$ ltrace -e write+syscall ./syscall > /dev/null
syscall->write(1, "1. Hello from the write() wrappe"..., 34) = 34
syscall->syscall(64, 1, 0x5581d6a0a048, 38)      = 38
+++ exited (status 0) +++
```

(`syscall->` is the name of the calling program; the address varies.)

For `errors.c`, `strace` shows the failing calls with their error codes:

```bash
$ strace -e trace=openat,close ./errors > /dev/null
...
openat(AT_FDCWD, "/etc/hostname", O_RDONLY) = 3
close(3)                                = 0
openat(AT_FDCWD, "/no/such/file", O_RDONLY) = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/etc/shadow", O_RDONLY) = -1 EACCES (Permission denied)
close(42)                               = -1 EBADF (Bad file descriptor)
+++ exited with 0 +++
```

*Egon Teiniker, 2025-2026, GPL v3.0*
