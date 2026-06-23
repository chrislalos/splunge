import os
import signal
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')
WWW_DIR = os.path.join(os.path.dirname(__file__), '..', 'www')

def find_free_port():
	with socket.socket() as s:
		s.bind(('', 0))
		return s.getsockname()[1]

def wait_for_port(port, timeout=5):
	deadline = time.time() + timeout
	while time.time() < deadline:
		try:
			with socket.create_connection(('localhost', port), timeout=1):
				return
		except OSError:
			time.sleep(0.1)
	raise TimeoutError(f"Port {port} not ready after {timeout}s")

def wait_for_socket(path, timeout=5):
	deadline = time.time() + timeout
	while time.time() < deadline:
		s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		try:
			s.connect(path)
			return
		except OSError:
			time.sleep(0.1)
		finally:
			s.close()
	raise TimeoutError(f"Socket {path} not ready after {timeout}s")

def start_server(script, *args, env=None):
	cmd = [os.path.join(SCRIPTS_DIR, script)] + [str(a) for a in args]
	merged_env = os.environ.copy()
	if env:
		merged_env.update(env)
	return subprocess.Popen(cmd, env=merged_env, start_new_session=True)

def stop_server(proc):
	"""Terminate a subprocess and its process group. Safe to call with None or already-dead process."""
	if proc is None:
		return
	try:
		os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
		proc.wait(timeout=5)
	except ProcessLookupError:
		pass
	except subprocess.TimeoutExpired:
		os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
		proc.wait()

def http_get(port, path):
	url = f'http://localhost:{port}{path}'
	try:
		resp = urllib.request.urlopen(url)
		return resp.status, resp.read().decode()
	except urllib.error.HTTPError as e:
		return e.code, e.read().decode()

def socket_get(sock_path, path):
	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	try:
		s.connect(sock_path)
		request = f'GET {path} HTTP/1.0\r\nHost: localhost\r\n\r\n'
		s.sendall(request.encode())
		response = b''
		while True:
			chunk = s.recv(4096)
			if not chunk:
				break
			response += chunk
	finally:
		s.close()
	status_line, _, body = response.partition(b'\r\n\r\n')
	status_code = int(status_line.split()[1])
	return status_code, body.decode()
