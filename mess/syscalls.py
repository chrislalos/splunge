import json
from urllib.request import urlretrieve

from bs4 import BeautifulSoup as BS


AT_EMPTY_PATH = 0x1000                  # $src/include/uapi/linux/fcntl.h
OPEN_TREE_CLONE = 1<<0					# $src/include/uapi/linux/mount.h
MOVE_MOUNT_F_EMPTY_PATH = 0x00000004	# $src/include/uapi/linux/mount.h
MOVE_MOUNT_T_EMPTY_PATH = 0x00000040	# $src/include/uapi/linux/mount.h

machineMappings = {
	"x86_64": "x86_64",
	"aarch64": "arm64",
	"armv7l": "arm",
	"armv6l": "arm",
	"arm": "arm",
	"i686": "i386",
	"i386": "i386",
	"riscv64": "riscv64",
	"riscv32": "riscv32",
	"ppc64le": "powerpc64",
	"ppc64": "powerpc64",
	"powerpc64": "powerpc64",
	"ppc": "powerpc",
	"powerpc": "powerpc",
	"s390x"	: "s390x"	,
	"alpha": "alpha",
	"arc": "arc",
	"csky": "csky",
	"hexagon": "hexagon",
	"loongarch32": "loongarch32",
	"loongarch64": "loongarch64",
	"m68k": "m68k",
	"microblaze": "microblaze",
	"mips64": "mips64",
	"mips64n32": "mips64n32",
	"mipso32": "mipso32",
	"nios2": "nios2",
	"openrisc": "openrisc",
	"parisc": "parisc",
	"parisc64": "parisc64",
	"sh": "sh",
	"sparc": "sparc",
	"sparc64": "sparc64",
	"xtensa": "xtensa",
	"s390": "s390",
}


def create_syscall_table(table):
	syscalls = {}
	machines = get_machines(table)
	rows = get_data_rows(table)
	for row in rows:
		syscall = get_syscall(row)
		syscallNums = get_syscall_numbers(row)
		syscalls[syscall] = dict(zip(machines, syscallNums))
	return syscalls	


def download_table():
	url = "https://gpages.juszkiewicz.com.pl/syscalls-table/syscalls.html"
	(file, msg) = urlretrieve(url)
	with open(file) as f:
		doc = BS(f, "lxml")
	table = doc.select_one("#infotable")
	return table


def get_data_rows(table):
	rows = table.tbody.find_all("tr")
	return rows


def get_machines(table):
	machines = [th.get_text() for th in table.thead.tr.find_all('th')][1:]
	return machines


def get_syscall(row):
	tds = row.find_all("td")
	syscall = tds[0].a.string
	return syscall


def get_syscall_numbers(row):
	tds = row.find_all("td")[1:]
	syscallNums = [int(td.string) for td in tds]
	return syscallNums


def load_syscall_table():
	with open("./syscall_table.json") as f:
		syscall_table = json.load(f)
	return syscall_table


def write_syscall_table():
	table = download_table()
	syscallTable = create_syscall_table(table)
	print(json.dumps(syscallTable, indent=3))
