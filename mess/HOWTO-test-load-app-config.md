# HOWTO test _load_app_config and config discovery

## Setup

From the splunge project root:

```
cd src/splunge
source venv/bin/activate
python3
```

Import helpers:

```python
import os
import sys
sys.path.insert(0, 'src')

from splunge.util import get_config_xattr, set_config_xattr, find_xattr_configs
from splunge.cli import _load_app_config, _mark_as_app_config, _get_app_config_paths
from splunge.cli import _get_default_config_path, _resolve_config
```

## Create a test config file

```python
with open('/tmp/test.cfg.py', 'w') as f:
    f.write('''name = "myapp"
codeFolders = []
contentFolders = []
templateFolders = []
guniCfg = {"bind": "0.0.0.0:13000"}
''')
```

## `_load_app_config` — import and build Config

| Call | Expected result |
|---|---|
| `cfg = _load_app_config('/tmp/test.cfg.py')` | `Config` object |
| `cfg.name` | `"myapp"` |
| `cfg.codeFolders` | `[]` |
| `cfg.guniCfg` | `{"bind": "0.0.0.0:13000"}` |
| `cfg.pprint()` | prints all 5 fields |

```python
cfg = _load_app_config('/tmp/test.cfg.py')
print(type(cfg).__name__)     # Config
print(cfg.name)                # myapp
print(cfg.guniCfg['bind'])     # 0.0.0.0:13000
```

### Missing file

| Call | Expected result |
|---|---|
| `_load_app_config('/tmp/does-not-exist.cfg.py')` | `FileNotFoundError` |

## `get_config_xattr` — check xattr tag

| Call | Expected |
|---|---|
| `get_config_xattr('/tmp/test.cfg.py')` | `False` (not yet tagged) |

## `set_config_xattr` — tag a file

| Call | Expected |
|---|---|
| `set_config_xattr('/tmp/test.cfg.py')` | no output (no error) |
| `get_config_xattr('/tmp/test.cfg.py')` | `True` |

```python
set_config_xattr('/tmp/test.cfg.py')
print(get_config_xattr('/tmp/test.cfg.py'))  # True
```

### Tag failure

On NFS or tmpfs where xattr is unsupported, `set_config_xattr` and `get_config_xattr` silently fail:

| fs type | `set_config_xattr(path)` | `get_config_xattr(path)` |
|---|---|---|
| ext4, btrfs, XFS | succeeds, tags file | `True` |
| tmpfs, NFS | no error, no-op | `False` |

## `_mark_as_app_config` — wrapper

| Call | Expected |
|---|---|
| `_mark_as_app_config('/tmp/test.cfg.py')` | no output |
| `get_config_xattr('/tmp/test.cfg.py')` | `True` |

## `find_xattr_configs` — list tagged files

| Call | Expected |
|---|---|
| `find_xattr_configs('/tmp')` | list containing `/tmp/test.cfg.py` |

```python
set_config_xattr('/tmp/test.cfg.py')
paths = find_xattr_configs('/tmp')
# should include /tmp/test.cfg.py
```

## `_get_app_config_paths` — tagged files in CWD

Scans `os.getcwd()` for xattr-tagged configs:

```python
os.chdir('/tmp')
set_config_xattr('/tmp/test.cfg.py')
paths = _get_app_config_paths()
# should include /tmp/test.cfg.py
```

## `_get_default_config_path` — dirname-based default

Create a file matching `$(dirname).cfg.py`:

```python
os.chdir('/tmp/myapp')
os.makedirs('/tmp/myapp', exist_ok=True)
open('myapp.cfg.py', 'w').close()
print(_get_default_config_path())  # ./myapp.cfg.py
```

## Cleanup

```python
import shutil
shutil.rmtree('/tmp/myapp', ignore_errors=True)
```

## Notes

- `_resolve_config` and `_load_default_config` test implicitly with the helpers above — not worth testing standalone
- `_get_user_app_config_path` requires interactive input — skip for manual testing
- xattr operations require `os.setxattr`/`os.getxattr` which exist on Linux only; they silently no-op on macOS and other platforms
- Files created in `/tmp` may be on tmpfs — xattr silently fails there, so choose a real filesystem path (e.g. project dir) for xattr tests
