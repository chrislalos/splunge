# site-04 — CodeFolderLoader integration test

## Overview

site-04 is a generated test site exercising splunge's CodeFolderLoader
across multiple code folders, nested directory structures, and relative imports.
Every leaf module imports 2-5 other modules via relative imports that traverse
the folder tree, testing that the loader handles cross-folder resolution,
sub-package detection, and sibling imports at all directory depths.

## Data sources

| Source | Location | Usage |
|---|---|---|
| Team names (877 names) | `test/codeFolderLoader/rez/team-names.txt` | Folder names |
| Pet names (~1000 names) | `test/codeFolderLoader/rez/pet-names.txt` | Module file names |

Both are shuffled and filtered for valid identifiers. Team names
form directory chains to depth 3. Pet names become `.py` file names.

## File layout

```
site-04/
  hello.py                      # imports all 13 leaf modules
  Duluth_Bulldogs/              # code folder 0 branch
    Chicago_Talons/
      Korean_Invasion/          # depth 3 — lexi.py
      San_Francisco_Miners/     # depth 3 — dakota.py, koba.py
    Monroeville_Zombies/        # depth 2 — isabella.py, ivy.py
  The_Harlem_Heroes/            # code folder 0 branch
    Miami_Thunder/
      New_New_York_Mets/        # depth 3 — billie.py, ernie.py, pedro.py
  code/                         # code folder 1
    Washington_Punishers/
      Indianapolis_Rays/
        Ohio_Red_Dogs/          # depth 3 — dolly.py
      London_Silly_Nannies/
        Big_Green/              # depth 3 — ruger.py
  content/                      # code folder 2
    Boston_Minutemen/
      Rump_City_Bootyheads/
        Pelotillehue_Unido/     # depth 3 — tessie.py, tiffany.py
      Whopping_Street_Wanderers/
        Boston_Whalers/         # depth 3 — brownie.py
```

## Code folders registered with the loader

```python
CodeFolderLoader([
    '/www/site-04',             # site root (hello.py, top-level modules)
    '/www/site-04/code',        # code/ directory
    '/www/site-04/content',     # content/ directory
])
```

## Generator infrastructure (`fnfgen.py`)

| Function | Purpose |
|---|---|
| `team_names()` | Shuffled generator of folder names from team-names.txt |
| `pet_names()` | Shuffled generator of module names from pet-names.txt |
| `gen_expected()` | Outputs `fnf.json` — the folder tree populated with pet names |
| `gen_site()` | Reads `fnf.json` and creates the full directory + `.py` file tree |
| `gen_hello()` | Reads `fnf.json` and generates `hello.py` importing all leaf modules |
| `leaves()` | Walks the tree and returns all leaf paths as dotted module names |
| `relative_import()` | Computes a Python relative import statement from source to target |

## What each leaf module contains

Every `.py` file sets `name = '<pet_name>'` and imports 2-5 other
leaf modules via relative imports (e.g. `from ...Monroeville_Zombies import ivy`).
The imports are randomly selected from all leaves. Cross-folder imports
(e.g. `code/Washington_Punishers/...ruger.py` importing from
`Duluth_Bulldogs/.../koba.py`) are included, testing that the loader
resolves modules from any code folder regardless of the calling module's
location.

## Tests (`test-site-04.py`)

22 tests total:

| Test | Verifies |
|---|---|
| `test_import` | `codefolder.hello` loads; all 22 module attribute + module.name checks pass |
| `test_import_billie` | relative imports of dolly, tessie, pedro, isabella |
| `test_import_blitzen` | empty import set (has no relative imports) |
| `test_import_brownie` | relative imports of koba, isabella, pedro |
| `test_import_comet` | empty import set |
| `test_import_cupid` | empty import set |
| `test_import_dakota` | empty import set |
| `test_import_dancer` | empty import set |
| `test_import_dasher` | empty import set |
| `test_import_dolly` | relative imports of ivy, tiffany |
| `test_import_donner` | empty import set |
| `test_import_ernie` | relative imports of dakota, dolly |
| `test_import_isabella` | relative imports of billie, ivy, koba, lexi, tessie |
| `test_import_ivy` | relative imports of brownie, koba, tessie, tiffany |
| `test_import_koba` | relative imports of pedro, billie |
| `test_import_lexi` | relative imports of ivy, ruger, ernie, isabella, billie |
| `test_import_pedro` | relative imports of ernie, isabella, ivy |
| `test_import_prancer` | empty import set |
| `test_import_ruger` | relative imports of koba, tiffany |
| `test_import_tessie` | relative imports of dolly, dakota |
| `test_import_tiffany` | relative imports of koba, tessie, dakota, ivy, lexi |
| `test_import_vixen` | empty import set |

Each test loads the specific module, builds an expected dict of
`{imported_module.name: expected_value}`, and calls `check_mod_vals()`
which walks the dot-separated path to verify the value.

## `check_mod_vals` walker

The `check_mod_vals(mod, expected)` function handles dotted attribute paths
like `'dolly.name'` by splitting on `.` and descending through `getattr()`:

```python
obj = mod
for part in key.split('.'):
    obj = getattr(obj, part)
assert obj == val
```

This works for both single-level checks (`'billie'`) and chained checks
(`'billie.name'` → billie module → name attribute).

## Key architectural decisions

- **Namespace package (`codefolder`)**: installed with empty
  `submodule_search_locations`. Exists purely to pass Python's
  "parent must be a package" gate for relative imports.
- **`find_spec` handles sub-packages**: when no `.py` file is found,
  checks if a directory exists and returns a package spec with
  `is_package=True`. This enables `from ...Monroeville_Zombies import ivy`
  where intermediate directories must be resolved as packages.
- **`submodule_search_locations` scoped per directory**: each
  intermediate package gets its own path pointing to that directory,
  so Python's `_find_and_load_unlocked` resolves nested relative
  imports correctly through the tree.
- **Sandbox isolation**: all tests run inside `boxylady.sh` which
  creates a mount namespace with `/www/site-04` bind-mounted.
  `sys.meta_path` manipulation is contained within the sandbox.
