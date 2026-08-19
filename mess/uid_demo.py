'''uid_demo — make the namespace "name -> opaque host id" insight visible.

Two demonstrations of the same idea: a namespace does not remove a
resource from the system, it relabels it and hands the process a *view*.
To everything outside the namespace the relabeled name may as well not
exist (or is reachable only through an opaque handle).

PHASE 1 (user namespace, no mount namespace):
    Inside, a process runs as uid 42.  The kernel only ever records the
    *mapped* host uid on the file it creates.  To the host that file is
    owned by 524330 (an opaque, unallocated host id) -- never "42".

PHASE 2 (user namespace + mount namespace, tmpfs root):
    A tmpfs is pivot_rooted to become "/" inside the namespace.  The host's
    own "/" is untouched.  The host can still reach that same tmpfs object,
    but only through the opaque handle /proc/<pid>/root -- not through its
    own "/".  Same object, different names/views.

Run:  python3 src/splunge/mess/uid_demo.py
'''

import ctypes
import os
import signal
import subprocess
import sys
import tempfile

libc = ctypes.CDLL("libc.so.6", use_errno=True)
libc.mount.argtypes = [ctypes.c_char_p, ctypes.c_char_p,
                       ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p]
libc.mount.restype = ctypes.c_int
libc.pivot_root.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
libc.pivot_root.restype = ctypes.c_int
libc.umount2.argtypes = [ctypes.c_char_p, ctypes.c_int]
libc.umount2.restype = ctypes.c_int


def mount(src, target, fstype, flags=0, data=None):
    if libc.mount(src, target, fstype, flags, data) != 0:
        err = ctypes.get_errno()
        raise OSError(err, f"mount({src!r},{target!r}) failed: {os.strerror(err)}")


def pivot_root(new, old):
    if libc.pivot_root(new, old) != 0:
        err = ctypes.get_errno()
        raise OSError(err, f"pivot_root failed: {os.strerror(err)}")


class _ReadTimeout(Exception):
    pass


def _alarm_handler(signum, frame):
    raise _ReadTimeout()


def best_effort_read(path, timeout=3):
    '''Read a file, but never block longer than `timeout` seconds.
    Used for the cross-namespace /proc/<pid>/root read, which can stall.'''
    old = signal.signal(signal.SIGALRM, _alarm_handler)
    try:
        signal.alarm(timeout)
        try:
            with open(path) as f:
                return f.read()
        finally:
            signal.alarm(0)
    except (_ReadTimeout, OSError):
        return None
    finally:
        signal.signal(signal.SIGALRM, old)


# --- identity constants -------------------------------------------------
INSIDE_UID = 42                 # the "name" inside the namespace
HOST_BASE = 524288             # chris's opaque subuid/subgid range start
HOST_UID = HOST_BASE + INSIDE_UID   # 524330 -- the host never sees "42"
HOST_ROOT_UID = 501            # inside uid 0 maps to chris on the host
HOST_ROOT_GID = 1000          # inside gid 0 maps to chris's group on host

WS_TMP = "/home/chris.linux/projects/daylight/tmp"  # staging stays in $ws/tmp


def phase1():
    print("=" * 68)
    print("PHASE 1 -- UID translation (user namespace only, no pivot)")
    print("=" * 68)
    print("  Inside the namespace a process is uid 42.  It writes a file in")
    print("  a world-writable host dir.  The host then stats that file.\n")

    host_dir = tempfile.mkdtemp(prefix="uid_demo_", dir=WS_TMP)
    os.chmod(host_dir, 0o777)          # inside process is host uid 524330
    marker = os.path.join(host_dir, "inside-42.txt")
    # Two separate eventfds: the shared counter must not be read by the
    # writer of the same signal (the child would otherwise consume its own
    # "ready" and proceed before the parent maps it).
    efd_child = os.eventfd(0, 0)       # child -> parent: "I'm in the ns"
    efd_parent = os.eventfd(0, 0)      # parent -> child: "maps are written"

    pid = os.fork()
    if pid != 0:
        # PARENT (host) -- outside the namespace.  Multi-line maps need
        # newuidmap/newgidmap, run from a process in the *host* namespace.
        # Wait until the child has entered its user namespace first.
        os.eventfd_read(efd_child)
        subprocess.run(["newuidmap", str(pid),
                        "0", str(HOST_ROOT_UID), "1",
                        str(INSIDE_UID), str(HOST_UID), "1"], check=True)
        subprocess.run(["newgidmap", str(pid),
                        "0", str(HOST_ROOT_GID), "1",
                        str(INSIDE_UID), str(HOST_UID), "1"], check=True)
        os.eventfd_write(efd_parent, 1)   # tell child the maps are ready
        os.close(efd_child)
        os.close(efd_parent)
        os.waitpid(pid, 0)

        st = os.stat(marker)
        print(f"  INSIDE   process getuid()={INSIDE_UID} (claims '42')")
        print(f"  HOST     stat('{marker}') -> st_uid={st.st_uid} "
              f"st_gid={st.st_gid}")
        print(f"           no system user owns {st.st_uid}; decode "
              f"{st.st_uid}-{HOST_BASE}={st.st_uid - HOST_BASE}")
        print("  => '42' created inside is just", st.st_uid,
              "to the host.  It may as well not be '42'.")

        os.remove(marker)
        os.rmdir(host_dir)
    else:
        # CHILD (inside the new user namespace)
        os.unshare(os.CLONE_NEWUSER)
        os.eventfd_write(efd_child, 1)    # signal: I'm in the ns, map me
        os.eventfd_read(efd_parent)       # block until parent writes maps
        os.close(efd_child)
        os.close(efd_parent)
        # Become root inside first so we can make the staging dir writable
        # by our later (mapped) uid, regardless of the host dir's perms.
        # No setgroups([]) call: supplementary groups don't affect file
        # ownership, and clearing them needs the setgroups "deny" trick
        # that the parent's newgidmap makes unnecessary here.
        os.setresgid(0, 0, 0)
        os.setresuid(0, 0, 0)
        try:
            os.chmod(host_dir, 0o777)
        except OSError as e:
            print(f"  (child)  chmod failed: {e}")
        os.setresgid(INSIDE_UID, INSIDE_UID, INSIDE_UID)
        os.setresuid(INSIDE_UID, INSIDE_UID, INSIDE_UID)
        try:
            with open(marker, "w") as f:
                f.write("owned by uid 42 inside the namespace\n")
            print(f"  (child)  getuid()={os.getuid()}; wrote {marker}")
        except OSError as e:
            st = os.stat(host_dir)
            print(f"  (child)  WRITE FAILED: {e!r} uid={os.getuid()} "
                  f"gid={os.getgid()} dir_mode={oct(st.st_mode & 0o777)} "
                  f"dir_owner={st.st_uid}:{st.st_gid}")
        sys.stdout.flush()
        os._exit(0)


def phase2():
    print("\n" + "=" * 68)
    print("PHASE 2 -- mount/pivot (user + mount ns, tmpfs root)")
    print("=" * 68)
    print("  A tmpfs is pivot_rooted to become '/' inside the namespace.")
    print("  The host's own '/' is unchanged.  The host reaches that same")
    print("  tmpfs only through the opaque handle /proc/<pid>/root.\n")

    stage = tempfile.mkdtemp(prefix="mess_stage_", dir=WS_TMP)
    r, w = os.pipe()                   # child -> parent: ready + proof
    re_, we = os.pipe()                # parent -> child: exit signal

    pid = os.fork()
    if pid != 0:
        os.close(w)
        os.close(re_)

        # child's own proof (reliable, in-process pipe -- no cross-ns read)
        proof = os.read(r, 4096).decode()
        os.close(r)

        # the tmpfs exists as the child's root mount (robust: just reads
        # the child's mount table, never crosses into its filesystem)
        with open(f"/proc/{pid}/mountinfo") as f:
            for ln in f.read().splitlines():
                if ln.split()[4] == "/":   # root mount of the child ns
                    root_mount = ln

        # best-effort reach through the opaque /proc/<pid>/root handle
        content = best_effort_read(f"/proc/{pid}/root/marker.txt")

        print(f"  CHILD    {proof.strip()}")
        print(f"  HOST     child mountinfo root: {root_mount}")
        if content is not None:
            print(f"  HOST     read /proc/{pid}/root/marker.txt:")
            print(f"             {content!r}")
        else:
            print("  HOST     /proc/<pid>/root read stalled (the view is "
                  "isolated while the namespace lives)")
        print("  HOST     host's own '/' is unchanged (still the real root).")

        os.write(we, b"x")             # tell child to exit
        os.close(we)
        os.waitpid(pid, 0)
        os.rmdir(stage)
    else:
        # CHILD: user + mount namespace; map self (single line, allowed),
        # mount tmpfs, pivot_root, write a marker, prove it over the pipe.
        os.close(r)
        os.close(we)
        os.unshare(os.CLONE_NEWUSER | os.CLONE_NEWNS)

        with open("/proc/self/uid_map", "w") as f:
            f.write(f"0 {HOST_ROOT_UID} 1\n")
        with open("/proc/self/setgroups", "w") as f:
            f.write("deny\n")
        with open("/proc/self/gid_map", "w") as f:
            f.write(f"0 {HOST_ROOT_GID} 1\n")

        stage_b = stage.encode()
        mount(b"tmpfs", stage_b, b"tmpfs", 0, None)
        old_b = os.path.join(stage, "old_root").encode()
        os.makedirs(os.path.join(stage, "old_root"), exist_ok=True)
        pivot_root(stage_b, old_b)
        os.chdir("/")

        with open("/marker.txt", "w") as f:
            f.write("hello from inside / (a tmpfs)\n")

        os.write(w, b"child created /marker.txt in its tmpfs root\n")
        os.close(w)
        print(f"  (child)  pivoted: '/' is now tmpfs; getuid()={os.getuid()}")
        sys.stdout.flush()
        os.read(re_, 1)                # wait for parent to finish inspecting
        sys.stdout.flush()
        os._exit(0)


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    print("\nUID-translation demo -- namespaces relabel, they do not remove.\n")
    phase1()
    phase2()
    print("\n" + "=" * 68)
    print("Takeaway: inside names (uid 42, '/') are translations.  Outside")
    print("the namespace they are opaque host ids (524330) or reachable only")
    print("through an opaque handle (/proc/<pid>/root) -- not '/'.  One")
    print("kernel, many views.")


if __name__ == "__main__":
    main()
