import filecmp
import os
import os.path
import tempfile

import boxylady


def test_mount_folder():
	''' Try and mount an existing root folder to a non existing mount 
	    folder. Both the root and mount folders will be temp folders created
		by this function. In addition to testing that mount_folder
		returns non-error, test that the root and mount have the
		same contents
	'''
	tmpDir = tempfile.mkdtemp(prefix='tests.test_mount_folder')
	srcDirPath = os.path.join(tmpDir, "src")
	print(f'{srcDirPath=}')
	dstDirPath = os.path.join(tmpDir, "dst")
	print(f'{dstDirPath=}')
	os.makedirs(srcDirPath)
	srcDir = os.open(srcDirPath, os.O_DIRECTORY|os.O_PATH)
	populate_source_dir(srcDir)
	rc = boxylady.mount_folder(srcDirPath, dstDirPath)
	assert rc == 0
	assert same_tree(srcDirPath, dstDirPath)


def populate_source_dir(srcDir):
	os.mkdir('a', dir_fd=srcDir)
	os.mkdir('a/b', dir_fd=srcDir)
	fd = os.open('a/foo.txt', os.O_WRONLY|os.O_CREAT, 0o644, dir_fd=srcDir)
	with os.fdopen(fd, "w") as f:
		f.write('foo')
	fd = os.open('a/b/bar.txt', os.O_WRONLY|os.O_CREAT, 0o644, dir_fd=srcDir)
	with os.fdopen(fd, "w") as f:
		f.write('bar')


def same_tree(left, right):
	comparison = filecmp.dircmp(left, right, shallow=False)

	def equal(dcmp):
		if (
			dcmp.left_only
			or dcmp.right_only
			or dcmp.common_funny
			or dcmp.diff_files
			or dcmp.funny_files
		):
			return False

		return all(equal(child) for child in dcmp.subdirs.values())

	return equal(comparison)


