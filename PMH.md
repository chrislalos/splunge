# Python Module Handler — import requirements

## Request lifecycle

1. `splunge run` starts a gunicorn worker that creates an `AppFactory`
2. `AppFactory._handle_request(wsgi, start_response)` fires for each HTTP request
3. A `CodeFolderLoader` is created with the configured code folders, installed at `meta_path[0]`
4. `wsgi_fn()` processes the request — handlers, enrichment, response generation
5. On completion (success or exception), CFL is removed from `meta_path`

CFL exists only during request handling. Outside of requests, Python imports are completely unaffected.

## Module name construction

`Xgi.get_module_name()` converts a URL path to a module name by splitting on `/` and joining with `.`:

```
/hello           → hello
/foo/bar/baz     → foo.bar.baz
```

No `codefolder.` prefix is added. The handler passes the bare name to `importlib.import_module()`.

## CFL find_spec behavior

`find_spec(fullname)` is called for every import during request handling. The CFL:

1. **Namespace package** — if `fullname == 'codefolder'`, returns the namespace spec (created at install time, idempotent). This enables `__package__ = 'codefolder'` for relative imports.

2. **Prefixed names** — if `fullname` starts with `codefolder.`, strips the prefix and searches code folders. This handles subtree imports (e.g., `codefolder.foo.bar`) and provides backward compatibility for existing tests.

3. **Bare names** — searches code folders for `<name>.py` or `<name>/__init__.py`. If found, returns a spec with `fullname = 'codefolder.<name>'`. This ensures `__package__` is set correctly for relative imports. If not found, returns `None` — Python falls through to `PathFinder` for stdlib and third-party modules.

## Shadowing behavior

CFL at position 0 shadows stdlib just like a local file shadows stdlib in normal Python:

- **Pre-cached modules** (`os`, `sys`, `builtins`, etc.) are never shadowed. They're already in `sys.modules` from Python startup. The import machinery returns them directly without consulting `meta_path`.

- **Un-cached modules** (`csv`, `json`, etc.) would be shadowed if a code folder contains a matching file. This is identical to normal Python behavior where `./csv.py` beats `/usr/lib/python3.12/csv.py`. The first finder to return a spec wins.

- **Performance** — each uncached bare import does one `os.stat` per code folder. With 3 code folders and 20 uncached imports per request: ~60 filesystem lookups. On a cached VFS, negligible. Once the first module resolves as `codefolder.foo`, all subtree imports arrive prefixed and match on the fast `startswith` check.

## Namespace package

The `codefolder` namespace package is created at CFL install time via `sys.modules['codefolder'] = ModuleType('codefolder')`. This is:

- **Idempotent** — repeated install/uninstall cycles are harmless. The namespace stays in `sys.modules` between requests.
- **Required** — without it, relative imports (`from . import sibling`) would fail because Python wouldn't know what `__package__` refers to.

## What doesn't use ContextVars

- `CV_xgi` — would be set per-request for module enrichment (`exec_module` adding `http` attribute). That's a future concern. Not needed for `find_spec`.
- `CV_cfg` / `CV_codeFolders` — CFL receives code folders at construction time. No ContextVar needed.

## PythonModuleHandler

The handler's job is minimal:

1. Get module name from xgi
2. Call `importlib.import_module(moduleName)`
3. CFL handles resolution, namespace setup, and relative import infrastructure

The handler never prepends `codefolder.` — that's the CFL's responsibility in `find_spec`.

## Remaining work

- CFL `exec_module()` — enrichment with `http` attribute, stdout capture. Requires access to the current Xgi. ContextVar is the natural mechanism.
- Related imports — content folders and template folders will need similar path-search utilities (a shared `find_in_folders(name, folders)` helper).
