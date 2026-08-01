from importlib import resources
import json
import os
import random
import re


def team_names():
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


def pet_names():
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


def gen_expected():
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


def leaves(tree):
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


def relative_import(source, target):
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


def gen_site(json_path='test/codeFolderLoader/fnf.json', out_root='www/site-04'):
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


def gen_hello(json_path='test/codeFolderLoader/fnf.json', out_path='www/site-04/hello.py'):
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
