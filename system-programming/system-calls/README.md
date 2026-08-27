# System Calls

## What is a System Call?

A **system call** is the controlled entry point through which a user-space
program requests a service from the kernel - reading a file, allocating
memory, creating a process, sending a signal, and so on. It is the only
legitimate way to cross from **User Space** to **Kernel Space**: user code
runs unprivileged and has no direct access to hardware or to another
process' memory, so anything that touches a shared or protected resource
has to go through the kernel.

* **Mechanism**: Invoking a system call is not a normal function call. The
  process places the syscall number and its arguments into CPU registers
  and executes a special trapping instruction (`syscall` on x86-64, `svc`
  on ARM). This raises the processor's privilege level, transfers control
  to a fixed entry point inside the kernel, and lets the kernel execute the
  requested operation on the program's behalf. Once it is done, the kernel
  returns control (and a result value) to user space and the privilege
  level drops back down. This is a **context switch**, which is
  considerably more expensive than an ordinary function call.

* **glibc wrappers**: Application code almost never issues the trapping
  instruction directly. Instead it calls a small C library wrapper function
  with the same name as the system call (e.g. `open()`, `read()`,
  `fork()`). The wrapper takes care of loading the syscall number and
  arguments into the right registers, trapping into the kernel, and - by
  convention - translating a negative return value into a return value of
  `-1` together with a code stored in the global `errno` variable, which
  `perror()`/`strerror()` can turn into a human-readable message.

* **Kernel vs. library functions**: Not every function in `<stdio.h>` etc.
  is a system call. `printf()`, for example, is a pure user-space library
  function that formats and buffers its output and only issues an
  underlying `write()` system call once the buffer needs to be flushed.
  System calls are the small, well-defined set of operations the kernel
  actually implements (see `man 2 syscalls` for the full list on Linux);
  everything else in the standard library is built on top of them.

* **Categories**: System calls broadly fall into groups such as file and
  IO operations (`open()`, `read()`, `write()`, `close()`, `lseek()`),
  process management (`fork()`, `execve()`, `wait()`, `exit()`), memory
  management (`brk()`, `mmap()`), signal handling (`sigaction()`,
  `kill()`), and inter-process communication (`pipe()`, `socket()`).

## Analyzing System Calls with `strace`

[`strace`](https://strace.io/) is a diagnostic tool that intercepts and
records every system call a process makes (using the kernel's `ptrace()`
facility), together with its arguments and return value. It is one of the
most useful tools for understanding what a program is *actually* doing at
the kernel boundary, independent of what its source code claims to do.

* **Basic usage** - run a program under `strace` and print every system
  call to `stderr`:

  ```bash
  $ strace ./program arg1 arg2
  ```

* **Useful options**:
    - `-o file` - write the trace to `file` instead of `stderr`.
    - `-e trace=openat,read,write,close` - only trace the listed system
      calls; indispensable for filtering out the (often long) sequence of
      calls made by the dynamic linker before `main()` even runs.
    - `-f` - also trace child processes created with `fork()`/`clone()`.
    - `-T` - show the time spent inside each system call.
    - `-c` - instead of a full trace, print a summary table with the
      number of calls, errors, and total time per system call.
    - `-p PID` - attach to and trace an already running process.

* **Reading the output**: Each line has the form
  `syscall(argument, ...) = return_value`, for example:

  ```
  openat(AT_FDCWD, "/etc/hostname", O_RDONLY) = 3
  read(3, "debian13\n", 262144)           = 9
  write(1, "debian13\n", 9)               = 9
  read(3, "", 262144)                     = 0
  close(3)                                = 0
  ```

  This is the trace of `cat /etc/hostname`: the file is opened and gets
  file descriptor `3`, its 9 bytes are `read()` into a buffer and then
  `write()`-ten to file descriptor `1` (stdout), a second `read()` returns
  `0` to signal end-of-file, and the descriptor is `close()`d. The same
  technique applied to the [`text-files`](../files/text-files/README.md)
  example shows exactly which `open()`/`read()`/`write()`/`close()` calls
  the low-level IO functions translate into.

* **Summary mode** (`strace -c`) is useful for a quick overview of which
  system calls a program relies on most and how much time is spent in
  each of them:

  ```
  % time     seconds  usecs/call     calls    errors syscall
  ------ ----------- ----------- --------- --------- ----------------
   21.52    0.000366          36        10           mmap
   16.28    0.000277          46         6           close
   12.40    0.000211          52         4           openat
    9.23    0.000157          31         5           fstat
    ...
  100.00    0.001701          35        48         1 total
  ```

## References

* [YouTube (Brian Will): Unix system calls (1/2)](https://youtu.be/xHu7qI1gDPA?si=PpqFVFRK7RlNnBz2)
* [YouTube (Brian Will): Unix system calls (2/2)](https://youtu.be/2DrjQBL5FMU?si=IqChNcv1gZj_8cPd)
