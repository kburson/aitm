#include <arpa/inet.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

#include "qualification.h"

static int access_denied(const char *path, int flags)
{
    int file = open(path, flags);
    if (file >= 0) {
        close(file);
        return 0;
    }
    return errno == EACCES || errno == EPERM;
}

static int check(int argc, char **argv)
{
    if ((argc != 10 && argc != 11) || getuid() == 0) {
        return 64;
    }

    int input = open(argv[2], O_RDONLY);
    char value = 0;
    if (input < 0 || read(input, &value, 1) != 1 || value != 'p') {
        return 65;
    }
    close(input);
    puts("ALLOW admitted input read");

    int scratch = open(argv[3], O_WRONLY | O_CREAT | O_EXCL, 0600);
    if (scratch < 0 || write(scratch, "worker scratch\n", 15) != 15) {
        return 66;
    }
    close(scratch);
    puts("ALLOW scratch write");

    if (!access_denied(argv[2], O_WRONLY) || !access_denied(argv[4], O_WRONLY)) {
        return 67;
    }
    puts("DENY admitted and out-of-scratch writes");

    if (!access_denied(argv[5], O_RDONLY) || !access_denied(argv[5], O_WRONLY)
        || !access_denied(argv[6], O_RDONLY) || !access_denied(argv[6], O_WRONLY)) {
        return 68;
    }
    puts("DENY controller evidence and credential marker read and write");
    if (!access_denied(argv[8], O_RDONLY) || !access_denied(argv[8], O_WRONLY)
        || !access_denied(argv[9], O_RDONLY) || !access_denied(argv[9], O_WRONLY)) {
        return 75;
    }
    puts("DENY checkout and controller home markers read and write");

    if (!access_denied("/dev/dtrace", O_RDONLY) || !access_denied("/dev/dtrace", O_RDWR)) {
        return 76;
    }
    puts("DENY controller trace device");
    if (argc == 11) {
        struct stat directory;
        if (stat(argv[10], &directory) != 0 || !S_ISDIR(directory.st_mode)) {
            return 78;
        }
        DIR *listing = opendir(argv[10]);
        if (listing != NULL) {
            errno = 0;
            struct dirent *next = readdir(listing);
            int error = errno;
            closedir(listing);
            if (next != NULL || (error != EACCES && error != EPERM)) {
                return 79;
            }
        } else if (errno != EACCES && errno != EPERM) {
            return 79;
        }
        puts("ALLOW admission root metadata");
        puts("DENY admission root listing");
    }

    struct sockaddr_in listener = {0};
    listener.sin_family = AF_INET;
    listener.sin_port = htons((unsigned short)strtoul(argv[7], NULL, 10));
    if (inet_pton(AF_INET, "127.0.0.1", &listener.sin_addr) != 1) {
        return 69;
    }
    int result = socket(AF_INET, SOCK_STREAM, 0);
    if (result >= 0) {
        int connected = connect(result, (struct sockaddr *)&listener, sizeof(listener));
        int error = errno;
        close(result);
        if (connected == 0 || (error != EACCES && error != EPERM)) {
            return 70;
        }
        puts("DENY loopback connect");
    } else {
        if (errno != EACCES && errno != EPERM) {
            return 71;
        }
        puts("DENY socket creation");
    }
    return 0;
}

static int trace(const char *program)
{
    printf("TARGET %d\n", getpid());
    fflush(stdout);
    if (getchar() != '\n') {
        return 71;
    }
    AITMQUAL_PHASE(368);
    pid_t child = fork();
    if (child < 0) {
        return 72;
    }
    if (child == 0) {
        execl(program, program, "child", (char *)NULL);
        _exit(73);
    }
    int status = 0;
    pid_t observed;
    do {
        observed = waitpid(child, &status, 0);
    } while (observed < 0 && errno == EINTR);
    if (observed != child || !WIFEXITED(status)) {
        return 74;
    }
    printf("WAIT %d %d %d\n", getpid(), child, WEXITSTATUS(status));
    return WEXITSTATUS(status);
}

int main(int argc, char **argv)
{
    if (argc == 3 && strcmp(argv[1], "refuse-exec") == 0) {
        execl(argv[2], argv[2], "child", (char *)NULL);
        if (errno != EACCES && errno != EPERM) {
            return 77;
        }
        puts("DENY unadmitted executable");
        return 0;
    }
    if (argc == 2 && strcmp(argv[1], "trace") == 0) {
        return trace(argv[0]);
    }
    if (argc == 2 && strcmp(argv[1], "child") == 0) {
        return 0;
    }
    if (argc > 1 && strcmp(argv[1], "check") == 0) {
        return check(argc, argv);
    }
    return 64;
}
