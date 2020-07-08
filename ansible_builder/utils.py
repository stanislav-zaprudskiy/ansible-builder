import subprocess
import sys
import os

from . import constants

__all__ = ['introspect']


def run_command(command, capture_output=False):
    print('Running command:')
    print('  {0}'.format(' '.join(command)))

    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

    output = []
    for line in iter(process.stdout.readline, b''):
        line = line.decode(sys.stdout.encoding)
        if capture_output:
            output.append(line.rstrip())
        sys.stdout.write(line)

    rc = process.poll()
    return (rc, output)


def introspect(data_dir=constants.base_collections_path):
    paths = []
    path_root = os.path.join(data_dir, 'ansible_collections')
    if not os.path.exists(path_root):
        # add debug statements at points like this
        sys.exit(1)

    for namespace in sorted(os.listdir(path_root)):
        if not os.path.isdir(os.path.join(path_root, namespace)):
            continue
        for name in sorted(os.listdir(os.path.join(path_root, namespace))):
            if not os.path.isdir(os.path.join(path_root, namespace, name)):
                continue
            collection_dir = os.path.join(path_root, namespace, name)
            files_list = os.listdir(collection_dir)
            if 'galaxy.yml' in files_list or 'MANIFEST.json' in files_list:
                paths.append(collection_dir)

    ret = []
    from .main import CollectionDefinition # avoid circular import
    for path in paths:
        CD = CollectionDefinition(path)
        dep_file = CD.get_dependency('python')
        if not dep_file:
            continue
        namespace, name = CD.namespace_name()
        ret.append(os.path.join(namespace, name, dep_file))
    return ret
