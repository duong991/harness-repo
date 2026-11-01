import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from slugify import slugify


class SlugifyTest(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_collapses_repeated_spaces(self):
        self.assertEqual(slugify("Hello   World"), "hello-world")

    def test_trims_edges(self):
        self.assertEqual(slugify("  Hello World "), "hello-world")


if __name__ == "__main__":
    unittest.main()
