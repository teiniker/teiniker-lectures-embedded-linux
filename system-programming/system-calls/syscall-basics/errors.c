#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/*
 * Write all bytes of a buffer: write() may write fewer bytes than requested
 * (partial write), and it may be interrupted by a signal (EINTR).
 * Returns 0 on success, -1 on error (errno is set).
 */
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
