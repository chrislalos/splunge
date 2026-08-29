'''boxylady — Python-native sandbox builder for splunge site testing.

Provides a clean facade for namespace manipulation, bind-mounting, and
chroot-style staging.  Initial implementations may delegate to subprocess
for system calls (ip, mount, etc.) but the API stays Pythonic.'''

import argparse
import os
import sysconfig

import libc
import syscalls


class AppendWithMulti(argparse.Action):
	''' Allow multiple occurences of a flag
		Each flag can have one or more arguments:
		e.g. --file foo.txt --file bar.txt bum.txt
	'''
	def __call__(self, parser, namespace, values, option_string=None):
	    current = getattr(namespace, self.dest) or []
	    current.extend(values)
	    setattr(namespace, self.dest, current)

class ToScalar(argparse.Action):
	''' argparse doesn't have a good way of specifying 'give me 1 value.
		I'm serious. Just one.' nargs=1 is close but it returns a list
		of one value. ToScalar converts this list to a single value
		which is what anyone specifying nargs=1 actually wants.
	'''
	def __call__(self, parser, namespace, values, option_string=None):
		if values and len(values) > 1:
			raise ValueError(f'>1 values ({len(values)})')
		val = values[0] if values else None
		setattr(namespace, self.dest, val)


def create_parser():
	''' arg parser w subcommands '''
	parser = argparse.ArgumentParser(prog='messaround')
	subs = parser.add_subparsers(dest="cmd", required=True)
	subCmd = 'test'
	p = subs.add_parser(subCmd)
	#p.add_argument('--folder', ...)
	p.set_defaults(func=test)
	
		
def create_python_distro():
	import sysconfig
	for k, v in sysconfig.get_paths().items(): print(f'{k:<20} {v}')


def create_root(dirpath):
	'''Create the necessary subdirectories inside a staging root.
	dirpath must already exist (typically created by mktemp).'''
	pass


def mount_bind(src, dst, recursive=False):
	'''Bind-mount src onto dst.  If recursive, propagate submounts.
	Handles both files and directories.'''
	pass


def make_rprivate(path='/'):
	'''Set mount propagation on path to private, recursively.
	Prevents mount events from propagating outside the namespace.'''
	pass


def enter_mount_ns():
	'''Create a new mount namespace via unshare(CLONE_NEWNS).
	Caller will be root (uid 0) in the new namespace.'''
	pass


def enter_net_ns():
	'''Create a new network namespace via unshare(CLONE_NEWNET).
	Only the loopback interface exists; no host network access.'''
	pass


def enter_user_ns(uid=None, gid=None):
	'''Create a new user namespace via unshare(CLONE_NEWUSER).
	Maps the calling uid/gid to 0 (root) inside the namespace.
	Falls back to newuidmap/newgidmap if direct /proc writes fail.'''
	pass


def is_child_path(target, paths):
	''' Determine if path is a child of one or more elements in paths '''
	return any(target != path and os.path.commonpath([target, path]) == path for path in paths) 


def reduce_sysconfig_paths():
	paths_dir = sysconfig.get_paths()
	realpaths_dir = {}
	for key, path in paths_dir.items():
		realpaths_dir[key] = os.path.realpath(path)
	realpaths = realpaths_dir.values()
	reduced_dir = {}
	for key, realpath in realpaths_dir.items():
		if not is_child_path(realpath, realpaths) and realpath not in reduced_dir.values():
			reduced_dir[key] = realpath
	return reduced_dir


def safe_mount(srcDir, dstDir):
	''' Do a readonly, private mount of srcDir to dstDir '''
	os.makedirs(dstDir, exist_ok=True)


def stage_current_python(stageDir):
	''' Stage the current python distro under /python in the staging dir '''
	pythonHome='/python'
	vars={'base': pythonHome, 'platbase': pythonHome, 'installed_base': pythonHome, 'installed_platbase': pythonHome}
	dSrcPaths = reduce_sysconfig_paths()
	dDstPaths = sysconfig.get_paths(scheme='posix_prefix', vars=vars)
	for key, srcPath in dSrcPaths.items():
		dstPath = dDstPaths[key]
		safe_mount(srcPath, dstPath)


def up_lo():
	'''Bring up the loopback interface.  Must be called after
	enter_net_ns() so the netns has its own lo.'''
	pass


def stage_system_dirs(root):
	'''Bind-mount system directories into the staging root: /bin, /lib, /usr.
	The staging root must already have matching empty directories.'''
	pass


def stage_venv(root, venv_path):
	'''Bind-mount a virtualenv into the staging root at /venv.
	Also mounts editable packages listed in __editable__.*.pth.'''
	pass


def stage_www(root, www_path):
	'''Bind-mount a www site directory into the staging root at /www.'''
	pass


def write_config(root, name, port, **kwargs):
	'''Write a cfg.toml into the staging root from a set of keyword args.
	Sets sensible defaults: codeFolders/contentFolders/templateFolders
	all point at /www, guniCfg.bind = 0.0.0.0:port, logFolder = /tmp/logs.'''
	pass


def pivot_into(root):
	'''Pivot the current mount namespace to use root as the new /.
	The old root is unmounted.  After this call, / is the staging root.'''
	pass


def launch(root, command=None):
	'''exec into a shell (or command) inside the already-pivoted root.
	If command is None, execs bash.  Never returns.'''
	pass


def mount_log_folders(stagePath, cfg):
	# logFolder
	# accessLog
	# errorLog
	pass


def mount_folder(srcDirPath, dstDirPath):
	''' mount a folder to a mount point.
	    use syscalls including the new open_tree_attr syscall which as of this
		writing does not have a libc mapping and must be invoked directly.
	'''
	# use open_tree_attr to create a detached mount of an existing folder (no flags for now)
	srcDir = os.open(srcDirPath, os.O_DIRECTORY|os.O_PATH)
	srcFd = libc.open_tree_attr(srcDir, "", syscalls.AT_EMPTY_PATH | syscalls.OPEN_TREE_CLONE, None)
	# create the destDir if necessary
	os.makedirs(dstDirPath, exist_ok=True)
	dstFd = os.open(dstDirPath, os.O_DIRECTORY|os.O_PATH)
	# call move_mount to do a open_tree fd => dst fd mount. Both src and dst paths will be empty string
	flags = syscalls.MOVE_MOUNT_F_EMPTY_PATH | syscalls.MOVE_MOUNT_T_EMPTY_PATH
	return libc.move_mount(srcFd, "", dstFd, "", flags) 




def stage(venv_path, www_path, cfg):
	'''Set up a staging root with system dirs, venv, www content,
	and a config file.  Does NOT enter namespaces or pivot.'''
	# mount system files (bin, dev, lib)
	# mount venv
	# mount www_path
	# mount cfg log folders
	pass


def build(name, port, venv_path, www_path):
	'''End-to-end: create temp root, stage it, enter user+net+mount
	namespaces, pivot, bring up lo, and drop into a shell.
	This is the function called by the messaround CLI.'''
	pass


def test(args):
	''' Run one or more tests against a web site launched by splunge on port 80 using
	a specific venv
	'''
	# enter a mount namespace, possibly as root, 
	# stage a folder with all the goodies (site, venv, log?, bin, dev, lib) pboxy
	# mount the staged folder to a local mount-point like `the-stage`
	# run the tests in a userns with the-stage as /
	pass
