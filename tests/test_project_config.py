import pathlib
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


class ProjectConfigTests(unittest.TestCase):
    def test_homeassistant_config_uses_supported_influx_key(self):
        content = (REPO_ROOT / "src" / "configuration.yaml").read_text()
        self.assertIn("\ninfluxdb:\n", content)
        self.assertNotIn("\ninfluxdb2:\n", content)
        self.assertIn("api_version: 2", content)

    def test_readme_links_to_published_docs(self):
        content = (REPO_ROOT / "README.md").read_text()
        self.assertIn("https://tallfurryman.github.io/light-pollution/fr/", content)
        self.assertIn("https://tallfurryman.github.io/light-pollution/en/", content)

    def test_docs_root_language_page_exists(self):
        self.assertTrue((REPO_ROOT / "docs" / "index.md").exists())


if __name__ == "__main__":
    unittest.main()
