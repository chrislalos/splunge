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


def gen_site(json_path='test/codeFolderLoader/fnf.json', out_root='www/site-04'):
    with open(json_path) as f:
        tree = json.load(f)

    def walk(node, path):
        os.makedirs(path, exist_ok=True)
        if isinstance(node, dict):
            for key, child in node.items():
                walk(child, os.path.join(path, key))
        elif isinstance(node, list):
            for pet in node:
                with open(os.path.join(path, pet + '.py'), 'w') as f:
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
