# Site-04 — Generated file and folder layout

## Data sources

| Source | Location | Count | Usage |
|---|---|---|---|
| Team names | `test/rez/codeFolderLoader/team-names.txt` (851 names) | Folders | Wikipedia "List of fictional sports teams" |
| Pet names | `test/rez/codeFolderLoader/inchit/petnames.txt` (1000 names) | Module files | Lowercased, alpha-only |

## `file_and_folder_gen.py` — generators

```python
import re

def team_names(path='tmp/team-names.txt'):
    """Yield valid folder names from the team names list.

    Filter: keep original case, reject non-alphanum+underscore.
    """
    seen = set()
    with open(path) as f:
        for line in f:
            name = line.strip().replace(' ', '_')
            if name and re.match(r'^[A-Za-z][A-Za-z0-9_]+$', name) and name not in seen:
                seen.add(name)
                yield name

def pet_names(path='src/inchit/petnames.txt'):
    """Yield valid module names from the pet names list.

    Filter: lowercase, alpha-only.
    """
    seen = set()
    with open(path) as f:
        for line in f:
            name = line.strip().lower()
            if name and name.isalpha() and name not in seen:
                seen.add(name)
                yield name
```

Both are module-level generators. Call `next(gen)` to pull the next name.

## Site-04 file layout

Three code folders plus the site root, each populated from the generators:

```
site-04/
  hello.py                        # site root — imports all 13 leaf modules
  root/                           # code folder 0
    Abscessed_Molars/             # depth 1
      Aceldama_Butchers/          # depth 2
        Adams_College_Atoms/      # depth 3 — abbey.py, abbie.py
        Albany_Patriots/          # depth 3 — abel.py
      Albany_Senators/            # depth 2 — abigail.py, ace.py
    Alexandria_Glory/             # depth 1
      Amarillo_Armadillos/        # depth 2
        Anaheim_Amigos/           # depth 3 — adam.py, admiral.py, aires.py
  code/                           # code folder 1
    Amsterdam_Lions/              # depth 1
      Anchorage_Wolves/           # depth 2
        Andromeda_Allstars/       # depth 3 — ajax.py
      Angola_Barnstormers/        # depth 2
        Annapolis_Admirals/       # depth 3 — alex.py, alexus.py
  content/                        # code folder 2
    Apollo_Stargazers/            # depth 1
      Arcturus_Archers/           # depth 2
        Arizona_Rattlers/         # depth 3 — alf.py, amber.py
      Asheville_Tourists/         # depth 2
        Astoria_Warriors/         # depth 3 — amie.py
```

4 code folders (site root + 3), 5 depth-1 branches, 8 depth-2 subdirectories, 9 depth-3 leaf directories, 13 pet-named `.py` files total.

## Module content

Every module sets `name = '<module_name>'` (its own pet name). Then imports 2-5 other modules via relative imports (`from ..Team_Name_B1.petname_beta import name`). Each import is shallow-cross-folder (different branches under the same code folder) or sibling. The imported `name` overwrites the local one — unimportant since `hello.py` imports each module directly.

Example for a leaf module `petname_alpha.py`:

```python
from ..Team_Name_B1.petname_beta import name
name = 'petname_alpha'
```

`hello.py` sits at the site root (`site-04/hello.py`) and imports every single module:

```python
from .Team_Name_C.Team_Name_C1.Team_Name_C1a.petname_alpha import name
petnameAlphaName = name
from .Team_Name_C.Team_Name_C1.Team_Name_C1a.petname_beta import name
petnameBetaName = name
# ... every module under code/
```

Each import captures the module's `name` attribute directly — no `as`, no aliasing. The variable `name` gets reassigned between imports.

## Expected data — JSON

Alongside the generated site files, `expected.json` records every module name → expected attribute value pair. Format:

```json
{
  "petnameAlphaName": "petname_alpha",
  "petnameBetaName": "petname_beta",
  ...
}
```

## Test file — `test-site-04.py`

```python
from splunge import CodeFolderLoader
import importlib, json, pytest

@pytest.fixture(scope='module')
def loader():
    ldr = CodeFolderLoader([
        '/www/site-04', '/www/site-04/root',
        '/www/site-04/code', '/www/site-04/content',
    ])
    ldr.install()
    yield ldr
    ldr.uninstall()

def test_import(loader):
    mod = importlib.import_module('codefolder.hello')
    assert mod is not None
    with open('./expected.json') as f:
        expected = json.load(f)
    check_mod_vals(mod, expected)

def check_mod_vals(mod, expected):
    for key, val in expected.items():
        attr = getattr(mod, key, None)
        assert attr is not None, f'{key} not found on hello'
        assert attr == val, f'{key}: expected {val!r}, got {attr!r}'
```

`check_mod_vals` takes the module and an expected dict — no extra params. The expected dict is generated alongside the site files, stored as JSON, and loaded by the test. The test is deterministic: same generator seed → same site layout → same expected values.

### step 1

create a module in codeFolderLoader caller fnfgen.py. Include the generator functions. The module should be suitable for me to open up a REPL, import the module, and then loop and next() to confirm im getting expected values. Open the files as resources w the Python stdlib importlib.resources

### step 2

add a function to fnfgen.py that generates JSON that corresponds to the following folder+filestructure:

```text
site-04/
  hello.py                      # site root — imports all 13 leaf modules
  root/                         # code folder 0
    Team_A/                     # depth 1
      Team_A1/                  # depth 2
        Team_A1a/               # depth 3 — pet_1.py (name='pet_1'), pet_2.py (name='pet_2')
        Team_A1b/               # depth 3 — pet_3.py (name='pet_3')
      Team_A2/                  # depth 2 — pet_4.py (name='pet_4'), pet_5.py (name='pet_5')
    Team_B/                     # depth 1
      Team_B1/                  # depth 2
        Team_B1a/               # depth 3 — pet_6.py (name='pet_6'), pet_7.py (name='pet_7'), pet_8.py (name='pet_8')
  code/                         # code folder 1
    Team_C/                     # depth 1
      Team_C1/                  # depth 2
        Team_C1a/               # depth 3 — pet_9.py (name='pet_9')
      Team_C2/                  # depth 2
        Team_C2a/               # depth 3 — pet_10.py (name='pet_10')
  content/                      # code folder 2
    Team_D/                     # depth 1
      Team_D1/                  # depth 2
        Team_D1a/               # depth 3 — pet_11.py (name='pet_11'), pet_12.py (name='pet_12')
      Team_D2/                  # depth 2
        Team_D2a/               # depth 3 — pet_13.py (name='pet_13')
```

`gen_expected()` pulls 13 names from the shuffled `pet_names()` generator and returns dict mapping each `petName → pet_value`. `hello.py` imports all 13, creating attributes for `check_mod_vals`.



### step 3

run the gen function and redirect output to test/codeFolderLoader/fnf.json. Then jq the file to validate its JSON 


### step 4

write a function that reads fnf.json and creates those folders and files under www/site-04. Make sure the filenames end in .py and each has a line of the form name = $moduleName (minus the .py) 


### step 5

create a hello.py at root and add imports to hello.py for every module. Also write assignments of the form ${moduleName}Name = ${moduleName}.name for each imported module. Every module gets imported and every module's `name` attribute gets assigned to a variable

### step 6

Look at test-site-04.py. There's an stub for test_import that calls check_mod_vals and a stub check_mod_vals that does nothing. Fill in test_import so it builds a dict of module attribute names and expected values. Simliar to site-test-03, there should be tests for the ${moduleName}Name module level attrubutes, as tell as ${moduleName}.name which checks the actual imported module value as well. Then check_mod_vals traverses the expected dict and asserts. Show me your plan

### step 7

Look test test-site-04/test_import_billie. This is a simple test where I copy pasted the imports from billie.py, then did some regexs to strip all but the module name, and then build the expected up and called check_mod_vals. Pretty easy. Write a similiar test for blitzen.py

### step 8


