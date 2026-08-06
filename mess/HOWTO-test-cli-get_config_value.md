# HOWTO test cli.get_config_value

## Setup

From the splunge project root:

```
cd src/splunge
source venv/bin/activate
python3
```

Then import the helpers:

```python
import sys
sys.path.insert(0, 'src')
from splunge.cli import _read_scalar, _read_list, _sanitize_prompt, get_config_value
```

## `_sanitize_prompt` — pure function

Call directly, check output.

| Call | Expected output |
|---|---|
| `_sanitize_prompt("Name")` | `"Name: "` |
| `_sanitize_prompt("Name:")` | `"Name: "` |
| `_sanitize_prompt("Name: ")` | `"Name: "` |
| `_sanitize_prompt("Name   ")` | `"Name: "` |

## `_read_scalar` — prompt + required flag

| Call | Type | Expected |
|---|---|---|
| `_read_scalar("Name")` | Enter (blank) | `""` |
| `_read_scalar("Name")` | `"myapp"` | `"myapp"` |
| `_read_scalar("Name", required=True)` | Enter, Enter, `"myapp"` | `"myapp"` |
| `_read_scalar("Name", required=True)` | `"myapp"` | `"myapp"` |

Note: prompts are not sanitized here — `"Name"` goes straight to `input()`. Add `: ` yourself if you want a colon: `_read_scalar("Name: ")`.

## `_read_list` — prompt + required flag

First prompt shows the full prompt. Subsequent prompts show `"  ...: "`.

| Call | Type | Expected |
|---|---|---|
| `_read_list("Folder: ")` | Enter | `[]` |
| `_read_list("Folder: ")` | `"foo"`, Enter | `["foo"]` |
| `_read_list("Folder: ")` | `"foo"`, `"bar"`, Enter | `["foo", "bar"]` |
| `_read_list("Folder: ", required=True)` | Enter, `"foo"`, Enter | `["foo"]` |
| `_read_list("Folder: ", required=True)` | `"foo"`, Enter | `["foo"]` |

## `get_config_value` — full prompt construction + defaults

Calls go through `_sanitize_prompt`, so `"Name"` becomes `"Name: "`.

### Scalar (multi=False)

| Call | Type | Expected |
|---|---|---|
| `get_config_value("Name")` | Enter | `""` |
| `get_config_value("Name")` | `"myapp"` | `"myapp"` |
| `get_config_value("Name", default="untitled")` | Enter | `"untitled"` |
| `get_config_value("Name", default="untitled")` | `"myapp"` | `"myapp"` |
| `get_config_value("Name", required=True)` | Enter, `"myapp"` | `"myapp"` |
| `get_config_value("Name", default="untitled", required=True)` | Enter | `"untitled"` |
| `get_config_value("Name", example="my-cool-app")` | `"x"` | `"x"` |

### Multi (multi=True)

| Call | Type | Expected |
|---|---|---|
| `get_config_value("Folder", multi=True)` | Enter | `[]` |
| `get_config_value("Folder", multi=True)` | `"foo"`, Enter | `["foo"]` |
| `get_config_value("Folder", multi=True)` | `"foo"`, `"bar"`, Enter | `["foo", "bar"]` |
| `get_config_value("Folder", multi=True, required=True)` | Enter, `"foo"`, Enter | `["foo"]` |
| `get_config_value("Folder", multi=True, default=["/tmp"])` | Enter | `["/tmp"]` |

### Combined

| Call | Type | Expected |
|---|---|---|
| `get_config_value("Bind", example="0.0.0.0:13000")` | Enter | `""` |
| `get_config_value("Bind", example="0.0.0.0:13000", required=True)` | Enter, `"bar"` | `"bar"` |

## Clean exit

Ctrl-D (`EOFError`) and Ctrl-C (`KeyboardInterrupt`) propagate up from all reader functions. These are caught by `init()` but not by raw REPL calls — you'll see a traceback if you test from the REPL without a handler.

## Notes

- Prompt format: `"Name [default]: "` when default is set, `"Name (ex. example): "` when example is set, `"Name: "` otherwise.
- `autoComplete=True` is not covered here — it requires the `path_completer` context manager and is best tested via the full `splunge init` flow.
