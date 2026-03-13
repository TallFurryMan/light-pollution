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

    def test_french_docs_reference_french_diagrams(self):
        architecture = (REPO_ROOT / "docs" / "fr" / "ARCHITECTURE.md").read_text()
        assembly = (REPO_ROOT / "docs" / "fr" / "ASSEMBLY.md").read_text()
        self.assertIn("classroom-flow-fr.svg", architecture)
        self.assertIn("software-stack-fr.svg", architecture)
        self.assertIn("node-wiring-pico-fr.svg", assembly)
        self.assertIn("power-chain-fr.svg", assembly)

    def test_localized_french_diagrams_exist(self):
        expected = [
            "classroom-flow-fr.svg",
            "software-stack-fr.svg",
            "node-wiring-pico-fr.svg",
            "power-chain-fr.svg",
        ]
        for name in expected:
            self.assertTrue((REPO_ROOT / "docs" / "images" / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
