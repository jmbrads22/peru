import os
import tempfile
import unittest

from peru.cache import Cache


def tmp_dir():
    tmp_root = "/tmp/perutest"
    os.makedirs(tmp_root, mode=0o777, exist_ok=True)
    return tempfile.mkdtemp(dir=tmp_root)


def create_dir_with_contents(path_contents_map):
    dir = tmp_dir()
    for path, contents in path_contents_map.items():
        full_path = os.path.join(dir, path)
        full_parent = os.path.dirname(full_path)
        if not os.path.isdir(full_parent):
            os.makedirs(full_parent)
        with open(full_path, "w") as f:
            f.write(contents)
    return dir


def read_contents_from_dir(dir):
    contents = {}
    for subdir, _, files in os.walk(dir):
        for file in files:
            path = os.path.normpath(os.path.join(subdir, file))
            with open(path) as f:
                content = f.read()
            relpath = os.path.relpath(path, dir)
            contents[relpath] = content
    return contents


class CacheTest(unittest.TestCase):
    def setUp(self):
        self.cache = Cache(tmp_dir())

    def test_exports_equal_imports(self):
        contents = {
            "a": "foo",
            "b/c": "bar",
        }
        import_dir = create_dir_with_contents(contents)
        tree = self.cache.import_tree(import_dir)
        export_dir = tmp_dir()
        self.cache.export_tree(tree, export_dir)
        new_contents = read_contents_from_dir(export_dir)
        self.assertDictEqual(contents, new_contents)
