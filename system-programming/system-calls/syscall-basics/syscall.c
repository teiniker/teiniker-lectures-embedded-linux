#define _GNU_SOURCE         /* for syscall() */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>    /* SYS_write */

/*
 * Three ways to execute the same write() system call:
 *
 *   1. the glibc wrapper function write()
 *   2. the generic glibc function syscall() with the system call number
 *   3. directly with the trap instruction (inline assembly)
 */

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
