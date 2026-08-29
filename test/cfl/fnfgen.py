from importlib import resources
import json
import os
import random
import re


# Detect cycles using white/gray/black algorithm
# eg https://www.geeksforgeeks.org/dsa/detect-cycle-direct-graph-using-colors/
# 
# I changed the colors from white/gray/black to NEW/CURR/DONE
#  - NEW - we have not visited this node
#  - CURR - this node is part of the path currently being followed and so if we
#           find a CURR node during our search 
#  - DONE - this node has already been checked
#
# This function is recursive: for each node it checks if the node is gray, and
# if not, it calls is_cyclic() on the next node on the path
#
def is_cyclic(graph):
    nodeState = {node: NEW for node in graph}

    # helper function to check a single node
    def dfs(node):
        nodeState[node] = CURR
        for neighbor in graph.get(node, []):
            if nodeState[neighbor] == CURR:                # cycle detected
                return True
            if nodeState[neighbor] == NEW:
                if dfs(neighbor):                          # recursion
                    return True
        nodeState[node] = DONE
        return False

    # if dfs() returns True for any node, we have a cycle
    for node in graph:                             
        if nodeState[node] == NEW:
            if dfs(node):
                return True

    # no cycle detected - we're clean
    return False


def gen_expected():
    """Generate the folder+file tree for site-04 as JSON.

    Pulls team names for folders and pet names for module files.
    Returns a JSON string with nested dicts representing the directory
    structure and lists of pet names at the leaves.
    """
    team = team_names()
    pet  = pet_names()

    def leaf(n):
        return [next(pet) for _ in range(n)]

    return json.dumps({
        'root': {
            next(team): {
                next(team): {next(team): leaf(2), next(team): leaf(1)},
                next(team): leaf(2),
            },
            next(team): {
                next(team): {next(team): leaf(3)},
            },
        },
        'code': {
            next(team): {
                next(team): {next(team): leaf(1)},
                next(team): {next(team): leaf(1)},
            },
        },
        'content': {
            next(team): {
                next(team): {next(team): leaf(2)},
                next(team): {next(team): leaf(1)},
            },
        },
    })


def gen_hello(json_path='test/codeFolderLoader/fnf.json', out_path='www/site-04/hello.py'):
    """Read fnf.json and write hello.py at the out_root directory.

    hello.py imports every leaf module and copies each module's ``name``
    attribute to a ``{pet}Name`` variable.
    """
    with open(json_path) as f:
        tree = json.load(f)

    imports = []
    assignments = []

    def walk(node, prefix):
        if isinstance(node, dict):
            for key, child in node.items():
                walk(child, prefix + '.' + key if prefix else key)
        elif isinstance(node, list):
            for pet in node:
                path = prefix + '.' + pet
                imports.append(f'from codefolder.{path} import {pet}')
                assignments.append(f'{pet}Name = {pet}.name')

    for folder, subtree in tree.items():
        walk(subtree, folder)

    with open(out_path, 'w') as f:
        for line in imports:
            f.write(line + '\n')
        f.write('\n')
        for line in assignments:
            f.write(line + '\n')


def gen_site(json_path='test/codeFolderLoader/fnf.json', out_root='www/site-04'):
    """Read fnf.json and create the full directory tree + .py files.

    Each leaf module gets random relative imports to 2-5 other leaves
    and a ``name = '<pet>'`` assignment.
    """
    with open(json_path) as f:
        tree = json.load(f)

    all_leaves = leaves(tree)
    random.shuffle(all_leaves)

    def walk(node, path):
        os.makedirs(path, exist_ok=True)
        if isinstance(node, dict):
            for key, child in node.items():
                walk(child, os.path.join(path, key))
        elif isinstance(node, list):
            for pet in node:
                leaf_path = os.path.relpath(
                    os.path.join(path, pet),
                    out_root
                ).replace('/', '.')
                peers = [l for l in all_leaves if l != leaf_path]
                count = min(random.randint(2, 5), len(peers))
                chosen = random.sample(peers, count)
                with open(os.path.join(path, pet + '.py'), 'w') as f:
                    for peer in chosen:
                        f.write(relative_import(leaf_path, peer) + '\n')
                    f.write(f"name = {pet!r}\n")

    walk(tree, out_root)


# def gen_site_script():
#     """Emit a shell script that creates the site tree from resolved JSON.
# 
#     Reads stdin (resolved fnf.json format with {imports, var}).
#     Writes mkdir/touch/printf commands to stdout. Target dir from $1.
#     """
#     import sys
# 
#     tree = json.load(sys.stdin)
# 
#     dirs = set()
#     files = []
# 
#     def walk(node, prefix=''):
#         for key, child in node.items():
#             if isinstance(child, dict) and 'imports' in child:
#                 files.append((prefix + key, child['imports'], child['var']))
#             elif isinstance(child, dict):
#                 dirs.add(prefix + key)
#                 walk(child, prefix + key + '/')
# 
#     walk(tree)
# 
#     print('#!/usr/bin/env bash')
#     print('set -eu')
#     print('target=${1:?usage: $0 <target-dir>}')
#     print()
#     for d in sorted(dirs):
#         print(f'mkdir -p "$target/{d}"')
#     for path, imports, var in sorted(files):
#         print(f'touch "$target/{path}.py"')
#         for imp in imports:
#             print(f'printf "%s\\n" {shlex.quote(imp)} >> "$target/{path}.py"')
#         print()
#         print(f'printf "%s\\n" {shlex.quote(var)} >> "$target/{path}.py"')


def gen_site_script():
    """Emit a shell script that creates the site tree from resolved JSON.

    Reads stdin (resolved fnf.json format with {imports, var}).
    Writes mkdir/touch/printf commands to stdout. Target dir from $1.
    """
    import sys
    from jinja2 import Environment

    tree = json.load(sys.stdin)

    dirs = set()
    files = []

    def walk(node, prefix=''):
        for key, child in node.items():
            if isinstance(child, dict) and 'imports' in child:
                files.append((prefix + key, child['imports'], child['var']))
            elif isinstance(child, dict):
                dirs.add(prefix + key)
                walk(child, prefix + key + '/')

    walk(tree)

    template = """#!/usr/bin/env bash
set -eu
target=${1:?usage: $0 <target-dir>}

{% for d in dirs -%}
mkdir -p "$target/{{ d }}"
{% endfor -%}
{% for path, imports, var in files -%}
touch "$target/{{ path }}.py"
{% for imp in imports -%}
printf '%s\\n' {{ imp }} >> "$target/{{ path }}.py"
{% endfor %}
printf '%s\\n' {{ var }} >> "$target/{{ path }}.py"

{% endfor -%}"""

    env = Environment(autoescape=False)
    print(env.from_string(template).render(dirs=sorted(dirs), files=sorted(files)))


def gen_site06_tree():
    """Generate a cycle-free site-06 folder tree with random imports as JSON.

    Produces 3 hello modules (apex, import all non-hellos), 4 rel modules
    (relative imports only), and 4 pet-named modules (absolute imports only),
    spread across a 2-child folder structure with one grandchild.
    """
    teams = team_names()
    pets = pet_names()
    rels = rel_names()
    hellos = hello_names()

    child1 = next(teams)
    child2 = next(teams)
    grandchild = next(pets).capitalize()

    top_rel = next(rels)
    child1_rel = next(rels)
    child2_rel = next(rels)
    gc_rel = next(rels)

    top_pet = next(pets)
    child1_pet = next(pets)
    child2_pet = next(pets)
    gc_pet = next(pets)

    top_hello = next(hellos)
    mid_hello = next(hellos)
    deep_hello = next(hellos)

    HELLOS = [top_hello, mid_hello, deep_hello]
    RELS = [top_rel, child1_rel, child2_rel, gc_rel]
    PETS = [top_pet, child1_pet, child2_pet, gc_pet]
    ALL_NON_HELLO = RELS + PETS

    N = 100000
    for attempt in range(N):
        graph = {name: [] for name in HELLOS + ALL_NON_HELLO}

        for h in HELLOS:
            graph[h] = ALL_NON_HELLO[:]

        for name in ALL_NON_HELLO:
            rel_candidates = [r for r in RELS if r != name]
            graph[name].extend(random.sample(
                rel_candidates,
                random.randint(0, min(2, len(rel_candidates)))
            ))
            abs_candidates = [p for p in PETS if p != name]
            graph[name].extend(random.sample(
                abs_candidates,
                random.randint(0, min(2, len(abs_candidates)))
            ))

        if not is_cyclic(graph):
            print(json.dumps({
                top_hello: graph[top_hello],
                top_rel: graph[top_rel],
                top_pet: graph[top_pet],
                child1: {
                    child1_rel: graph[child1_rel],
                    child1_pet: graph[child1_pet],
                },
                child2: {
                    child2_rel: graph[child2_rel],
                    child2_pet: graph[child2_pet],
                    mid_hello: graph[mid_hello],
                    grandchild: {
                        gc_rel: graph[gc_rel],
                        gc_pet: graph[gc_pet],
                        deep_hello: graph[deep_hello],
                    },
                },
            }))
            return

    raise RuntimeError(f"{N} attempts without cycle-free graph")



def hello_names():
    """Infinite generator yielding 'hello1', 'hello2', 'hello3', ..."""
    n = 1
    while True:
        yield f'hello{n}'
        n += 1


def leaves(tree):
    """Walk a folder tree and return all leaf module paths as dotted names.

    Each leaf is a pet name at the end of a list node; the return value
    includes the full dotted chain from the root.
    """
    result = []
    def walk(node, prefix):
        if isinstance(node, dict):
            for key, child in node.items():
                walk(child, prefix + '.' + key if prefix else key)
        elif isinstance(node, list):
            for pet in node:
                result.append(prefix + '.' + pet)
    for key, subtree in tree.items():
        walk(subtree, key)
    return result


def pet_names():
    """Shuffled generator of valid Python module names from pet-names.txt.

    Filters: lowercase, alpha-only, no duplicates.
    """
    seen = set()
    names = []
    data = resources.files('test.codeFolderLoader.rez').joinpath('pet-names.txt').read_text()
    for line in data.splitlines():
        name = line.strip().lower()
        if name and name.isalpha() and name not in seen:
            seen.add(name)
            names.append(name)
    random.shuffle(names)
    for name in names:
        yield name


def rel_names(start=1):
    """Infinite generator yielding 'rel1', 'rel2', 'rel3', ..."""
    n = start
    while True:
        yield f'rel{n}'
        n += 1


def relative_import(source, target):
    """Return a Python relative-import statement from source to target.

    Both arguments are dotted leaf paths (e.g. 'foo.bar.bum').
    The result is a string like 'from ...bar import bum'.
    """
    src_dirs = source.split('.')[:-1]
    tgt_dirs = target.split('.')[:-1]
    tgt_leaf = target.split('.')[-1]
    common = 0
    for s, t in zip(src_dirs, tgt_dirs):
        if s == t:
            common += 1
        else:
            break
    ups = len(src_dirs) - common
    dots = '.' * (ups + 1)
    downs = tgt_dirs[common:]
    if downs:
        path = dots + '.'.join(downs)
    else:
        path = dots
    return f'from {path} import {tgt_leaf}'


def resolve_imports():
    """Read fnf.json from stdin, write resolved imports + var to stdout."""
    import sys
    tree = json.load(sys.stdin)

    folder_map = {}

    def walk_map(node, parent=None):
        if isinstance(node, dict):
            for key, child in node.items():
                if isinstance(child, list):
                    folder_map[key] = parent
                else:
                    walk_map(child, parent + '/' + key if parent else key)

    walk_map(tree)

    def _make_abs(target):
        path = folder_map[target]
        if path:
            return f'import {path.replace("/", ".")}.{target}'
        return f'import {target}'

    def _make_rel(src, target):
        src_parts = src.split('/') if src else []
        tgt_parent = folder_map[target]
        tgt_parts = tgt_parent.split('/') if tgt_parent else []
        common = 0
        for s, t in zip(src_parts, tgt_parts):
            if s == t:
                common += 1
            else:
                break
        ups = len(src_parts) - common
        dots = '.' * (ups + 1)
        down = '.'.join(tgt_parts[common:])
        if down:
            return f'from {dots}{down} import {target}'
        else:
            if ups == 0:
                return f'from . import {target}'
            return f'from {dots[:-1]} import {target}'

    def walk_resolve(node, parent=None):
        if isinstance(node, dict):
            for key, child in node.items():
                if isinstance(child, list):
                    imports = []
                    for target in child:
                        if target.startswith('rel'):
                            imports.append(_make_rel(parent, target))
                        else:
                            imports.append(_make_abs(target))
                    node[key] = {
                        'imports': imports,
                        'var': f"name = '{key}-san'",
                    }
                else:
                    walk_resolve(child, parent + '/' + key if parent else key)

    walk_resolve(tree)
    json.dump(tree, sys.stdout)
    sys.stdout.write('\n')


def team_names():
    """Shuffled generator of valid directory names from team-names.txt.

    Filters: PascalCase, spaces replaced with underscores, alphanumeric+underscore only.
    """
    seen = set()
    names = []
    data = resources.files('test.codeFolderLoader.rez').joinpath('team-names.txt').read_text()
    for line in data.splitlines():
        name = line.strip().replace(' ', '_')
        if name and re.match(r'^[A-Za-z][A-Za-z0-9_]+$', name) and name not in seen:
            seen.add(name)
            names.append(name)
    random.shuffle(names)
    for name in names:
        yield name


