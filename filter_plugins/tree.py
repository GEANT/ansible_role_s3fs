#!/usr/bin/env python3
import os


def to_tree(data, base_path=None):
    """Converts Ansible find module output into an ASCII tree structure.

    If base_path is omitted, it renders full absolute paths with '/' as the root.
    If base_path is provided, it renders relative paths with '.' as the root.
    """
    if not data:
        return '/' if not base_path else '.'

    # Extract the file list from the registered output dict or raw list
    if isinstance(data, dict):
        file_list = data.get('files', [])
    elif isinstance(data, list):
        file_list = data
    else:
        return '/' if not base_path else '.'

    # Extract path strings
    clean_paths = []
    for item in file_list:
        if isinstance(item, dict) and 'path' in item:
            clean_paths.append(item['path'])
        elif isinstance(item, str):
            clean_paths.append(item)

    if not clean_paths:
        return '/' if not base_path else '.'

    # Convert paths relative to base_path if explicitly provided; otherwise keep full paths
    if base_path:
        formatted_paths = [os.path.relpath(p, base_path) for p in clean_paths]
        root_label = '.'
    else:
        formatted_paths = clean_paths
        root_label = '/'

    # Build nested dictionary structure
    tree_dict = {}
    for path in formatted_paths:
        parts = [p for p in path.split(os.sep) if p]
        current = tree_dict
        for part in parts:
            current = current.setdefault(part, {})

    # Generate ASCII structure recursively
    lines = [root_label]

    def _build_lines(node, prefix=''):
        # Sort keys to ensure directories and files are rendered alphabetically
        items = sorted(node.keys())
        for index, key in enumerate(items):
            is_last = index == len(items) - 1
            connector = '└── ' if is_last else '├── '
            lines.append(f'{prefix}{connector}{key}')

            if node[key]:
                child_prefix = prefix + ('    ' if is_last else '│   ')
                _build_lines(node[key], child_prefix)

    _build_lines(tree_dict)
    return '\n'.join(lines)


class FilterModule:
    """Ansible Jinja2 filter plugin for tree formatting."""

    def filters(self):
        return {
            'to_tree': to_tree,
        }
