import ctypes
import os

import syscalls

### shortcuts for ctypes type constants
n = ctypes.c_int
s = ctypes.c_char_p
u = ctypes.c_uint
u64 = ctypes.c_uint64
p = ctypes.c_void_p

libcso = ctypes.CDLL(None, use_errno=True)


def get_syscall_number(name):
	table = syscalls.load_syscall_table()
	unameMachine = os.uname().machine
	machine = syscalls.machineMappings[unameMachine]
	syscallNum = table[name][machine]
	return syscallNum


###
#
# existing libc wrappers
#

# move_mount
#
# int move_mount(int from_dirfd,
#                const char *from_path,
#                int to_dirfd,
#				 const char *to_path,
#				 unsigned int flags);
_move_mount = libcso.move_mount
_move_mount.restype = n
_move_mount.argtypes = [n, s, n, s, u]


def move_mount(from_dirfd: int, from_path: str, to_dirfd: int, to_path: str, flags: int=0) -> int:
	if from_path is not None:
		from_path = from_path.encode()
	if to_path is not None:
		to_path = to_path.encode()
	rc =_move_mount(from_dirfd, from_path, to_dirfd, to_path, flags)
	if rc < 0:
		errno = ctypes.get_errno()
		raise OSError(errno, os.strerror(errno))
	return rc


###
#
# raw syscalls
#

# open_tree_attr
#
# int syscall(SYS_open_tree_attr,
#             int dirfd,
#             const char *path,
#             unsigned int flags,
#             struct mount_attr *_Nullable attr,
#             size_t size);

class MountAttr(ctypes.Structure):
	_fields_ = [
		("attr_set", u64),
		("attr_clr", u64),
		("propagation", u64),
		("userns_fd", u64)
	]

_open_tree_attr = ctypes.CFUNCTYPE(n, n, n, s, n, p, n, use_errno=True)(("syscall", libcso))

def open_tree_attr(dirfd: int, path: str, flags: int, attr: MountAttr | None = None, size: int = 0) -> int:
	if path is not None:
		path = path.encode()
	if attr is not None:
		if size == 0:
			size = ctypes.sizeof(attr)
		attr = ctypes.byref(attr)
	syscallNum = get_syscall_number('open_tree_attr')
	fd = _open_tree_attr(syscallNum, dirfd, path, flags, attr, size)
	if fd < 0:
		errno = ctypes.get_errno()
		raise OSError(errno, os.strerror(errno))
	return fd

