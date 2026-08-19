import ctypes
import os
import shutil
import subprocess
import sys
import tempfile

# Staging dirs live in the workspace tmp folder, never system /tmp.
WS_TMP = "/home/chris.linux/projects/daylight/tmp"


def become_root():
    ''' become root - userid/groupid == 0/0
    possible inside an ns if shadow id maps support it
    '''
    os.setresuid(0, 0, 0)
    os.setresgid(0, 0, 0)

def check_id_map():
    """Verify /etc/subuid and /etc/subgid contain an entry for the current
    user with range 0:65536.  Exit with rc=1 if missing."""
    me = os.getlogin()
    for fname in ('/etc/subuid', '/etc/subgid'):
        try:
            with open(fname) as f:
                if f'{me}:0:65536' not in f.read():
                    sys.exit(f'{fname}: missing entry {me}:0:65536')
        except FileNotFoundError:
            sys.exit(f'{fname}: file not found')

MS_BIND = 4096
MS_REC = 0x4000


def drop_privs(uid, gid):
    """Drop to the target uid/gid inside the namespace.

    GID is set before UID because dropping UID strips CAP_SETGID, after
    which the GID change would fail.  We do NOT call setgroups([]): the
    gid_map is written by the privileged newgidmap, which leaves
    /proc/self/setgroups in "allow" mode, and an unprivileged child in a
    user namespace cannot call setgroups() in "allow" mode (EPERM).  The
    supplementary group list does not affect file ownership, so clearing it
    is unnecessary here.
    """
    os.setresgid(gid, gid, gid)   # GID first — still root, have CAP_SETGID
    os.setresuid(uid, uid, uid)   # drop root — capabilities gone


def main():
    check_id_map()

    libc = ctypes.CDLL('libc.so.6', use_errno=True)
    bash = shutil.which('bash')
    # Two separate eventfds: the shared counter must not be read by the
    # writer of the same signal (a child would otherwise consume its own
    # "entered" signal and proceed before the parent maps it).
    efd_child = os.eventfd(0, 0)   # child -> parent: entered user ns
    efd_parent = os.eventfd(0, 0)  # parent -> child: maps written

    # Staging dir is created in the PARENT (in $ws/tmp) so the parent can
    # clean it up after the child's namespace is torn down on exit.
    td = tempfile.mkdtemp(dir=WS_TMP)    # staging area — will become /

    # --- fork: parent writes uid/gid mappings, child enters the namespace ---
    pid = os.fork()
    if pid != 0:
        # Wait for the child to actually enter its user namespace before
        # writing the maps: newuidmap/newgidmap operate on /proc/<pid>/uid_map,
        # which only exists once the child has called unshare(CLONE_NEWUSER).
        os.eventfd_read(efd_child)
        # sets the mapping to 0 0 65536 (run from OUTSIDE the namespace, so
        # the setuid helpers can authorize against the parent ns)
        subprocess.run(['newuidmap', str(pid), '0', '0', '65536'], check=True)
        subprocess.run(['newgidmap', str(pid), '0', '0', '65536'], check=True)
        os.eventfd_write(efd_parent, 1)   # tell child mappings are ready
        os.close(efd_child)
        os.close(efd_parent)
        os.waitpid(pid, 0)
        shutil.rmtree(td, ignore_errors=True)   # drop the staging dir
        sys.exit(0)

    # child continues — enter a fresh user + mount namespace
    os.unshare(os.CLONE_NEWUSER | os.CLONE_NEWNS)
    os.eventfd_write(efd_child, 1)   # signal: I'm in the ns, map me
    os.eventfd_read(efd_parent)      # block until parent writes mappings
    os.close(efd_child)
    os.close(efd_parent)

    # bind-mount system directories into the staging area
    for d in ['/bin', '/lib', '/usr/bin', '/usr/lib', '/dev', '/etc']:
        target = os.path.join(td, d.lstrip('/'))
        os.makedirs(target, exist_ok=True)
        libc.mount(d.encode(), target.encode(), None, MS_BIND, None)

    # pivot_root: staging area becomes /, old root moves to /old_root
    cwd = td.encode()
    old = os.path.join(td, 'old_root').encode()
    os.makedirs(os.path.join(td, 'old_root'), exist_ok=True)
    libc.mount(cwd, cwd, None, MS_BIND | MS_REC, None)  # make staging a mount point
    libc.pivot_root(cwd, old)                            # swap roots
    os.chdir('/')

    # become myself — all UIDs display correctly thanks to 1:1 mapping
    drop_privs(501, 1000)

    os.environ['PS1'] = '[mess] $ '
    os.execve(bash, ['bash', '--norc'], os.environ)


if __name__ == '__main__':
    main()
