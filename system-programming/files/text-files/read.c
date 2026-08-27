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
