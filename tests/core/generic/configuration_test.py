import unittest

from epowcore.generic.configuration import Configuration


class ConfigurationTest(unittest.TestCase):
    """Test the configuration class."""

    def test_config(self) -> None:
        """Test the configuration class."""
        self.assertTrue(Configuration().load_config("tests/test_config.yml", priority=10))
        self.assertEqual(Configuration().get("test.test"), "Hello World!")
        self.assertEqual(Configuration().get("test.list"), ["Hello", "World!"])
        self.assertEqual(Configuration().get("test.list.0"), "Hello")
        self.assertEqual(Configuration().get("test.number"), 123)
        self.assertEqual(Configuration().get("sub_config.list"), [1, 2])
        self.assertEqual(
            Configuration().get("test"),
            {"test": "Hello World!", "list": ["Hello", "World!"], "number": 123},
        )
        Configuration().load_config("config.yml")
        Configuration().delete_config(10)

    def test_priority(self) -> None:
        """Tests configuration overlays with different priorities."""
        self.assertTrue(Configuration().load_config("tests/test_config.yml"))
        self.assertEqual(Configuration().get("test.list"), ["Hello", "World!"])
        self.assertTrue(Configuration().load_config("tests/test_priority.yml", 1))
        self.assertEqual(Configuration().get("test.list"), ["Goodbye", "World!"])
        Configuration().delete_config(1)
        self.assertEqual(Configuration().get("test.list"), ["Hello", "World!"])
        Configuration().delete_config(0)
        self.assertEqual(Configuration().get("test.list"), None)


if __name__ == "__main__":
    unittest.main()
