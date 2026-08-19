#include <errno.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int append_if_missing(const char *path, const char *user,
                              unsigned long start, unsigned long count) {
    char line[1024];
    snprintf(line, sizeof(line), "%s:%lu:%lu\n", user, start, count);

    FILE *f = fopen(path, "r");
    if (f) {
        char buf[1024];
        while (fgets(buf, sizeof(buf), f))
            if (strcmp(buf, line) == 0) { fclose(f); return 0; }
        fclose(f);
    }

    f = fopen(path, "a");
    if (!f) { perror(path); return 1; }
    fputs(line, f);
    fclose(f);
    return 0;
}

static int parse_range(const char *arg, unsigned long *first,
                        unsigned long *last) {
    char *dash = strchr(arg, '-');
    if (!dash) return 1;
    *dash = '\0';
    *first = strtoul(arg, NULL, 10);
    *last = strtoul(dash + 1, NULL, 10);
    *dash = '-';
    if (*first > *last) return 1;
    return 0;
}

int main(int argc, char *argv[]) {
    const char *user = NULL;
    int do_all = 0;
    int do_subuid = 0;
    int do_subgid = 0;
    unsigned long uid_first = 0, uid_last = 0;
    unsigned long gid_first = 0, gid_last = 0;

    if (argc < 2) {
        fprintf(stderr,
            "idid — update /etc/subuid and /etc/subgid\n"
            "  idid --all [USER]\n"
            "  idid USER --add-subuids FIRST-LAST\n"
            "  idid USER --add-subgids FIRST-LAST\n");
        return 1;
    }

    int i = 1;

    if (strcmp(argv[i], "--all") == 0) {
        do_all = 1;
        i++;
    }

    if (i < argc && argv[i][0] != '-') {
        user = argv[i];
        i++;
    }

    if (!user) {
        uid_t uid = getuid();
        struct passwd *pw = getpwuid(uid);
        if (!pw) { fprintf(stderr, "cannot determine user\n"); return 1; }
        user = pw->pw_name;
    }

    struct passwd *pw = getpwnam(user);
    if (!pw) { fprintf(stderr, "no such user: %s\n", user); return 1; }

    uid_t caller = getuid();
    if (caller != 0 && strcmp(user, getpwuid(caller)->pw_name) != 0) {
        fprintf(stderr, "not permitted to modify %s\n", user);
        return 1;
    }

    if (do_all) {
        return append_if_missing("/etc/subuid", user, 0, 65536)
            || append_if_missing("/etc/subgid", user, 0, 65536);
    }

    while (i < argc) {
        if (strcmp(argv[i], "--add-subuids") == 0 && i + 1 < argc) {
            if (parse_range(argv[i + 1], &uid_first, &uid_last)) {
                fprintf(stderr, "bad range: %s\n", argv[i + 1]);
                return 1;
            }
            do_subuid = 1;
            i += 2;
        } else if (strcmp(argv[i], "--add-subgids") == 0 && i + 1 < argc) {
            if (parse_range(argv[i + 1], &gid_first, &gid_last)) {
                fprintf(stderr, "bad range: %s\n", argv[i + 1]);
                return 1;
            }
            do_subgid = 1;
            i += 2;
        } else {
            fprintf(stderr, "unknown argument: %s\n", argv[i]);
            return 1;
        }
    }

    int rc = 0;
    if (do_subuid)
        rc |= append_if_missing("/etc/subuid", user, uid_first,
                                 uid_last - uid_first + 1);
    if (do_subgid)
        rc |= append_if_missing("/etc/subgid", user, gid_first,
                                 gid_last - gid_first + 1);
    return rc;
}
