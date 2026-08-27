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
