import ctypes

###
#
# existing libc wrappers
#
libcso = ctypes.CDLL(None, use_errno=True)

# move_mount
#
# int move_mount(int from_dirfd,
#                const char *from_path,
#                int to_dirfd,
#				 const char *to_path,
#				 unsigned int flags);
_move_mount = libcso.move_mount
_move_mount.restype = ctypes.cint
_move_mount.argtypes = [
	ctypes.c_int,    # int from_dirfd
	ctypes.c_char_p, # const char *from_path
	ctypes.c_int,    # int to_dirfd
	ctypes.c_char_p, # const char *to_path
	ctypes.c_uint    # unsigned int flags
]


def move_mount(from_dirfd: int, from_path: str, to_dirfd: int, to_path: str, flags: int) -> int:
	if from_path:
		from_path = from_path.encode()
	if to_path:
		to_path = to_path.encode()
	return _move_mount(from_dirfd, from_path, to_dirfd, to_path, flags)


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

SYS_open_tree_attr = 467

class MountAttr(ctypes.Structure):
	_fields_ = [
		("attr_set", ctypes.c_uint64),
		("attr_clr", ctypes.c_uint64),
		("propagation", ctypes.c_uint64),
		("userns_fd", ctypes.c_uint64)
	]


_open_tree_attr = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_str, ctypes.c_void_p, ctypes.c_int)(("syscall", ctypes.CDLL(None)))

def open_tree_attr(dirfd: int, path: str, flags: int, attr: MountAttr | None = None, size: int = 0) -> int:
	if path:
		path = path.encode()
	return _open_tree_attr(SYS_open_tree_attr, dirfd, path, flags, attr, size)

