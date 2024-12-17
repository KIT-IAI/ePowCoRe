import os
import unittest

from epowcore.generic.logger import Logger

LOG_FILE_PATH = "test.log"


class LoggingTest(unittest.TestCase):
    def test_lifecycle(self) -> None:
        """Test the lifecycle of the logger with creation, retrieval and deletion."""
        # Create
        logger = Logger.new("test")
        handle = logger.handle
        logger1 = Logger.new("test1")
        self.assertEqual(logger1.handle, logger.handle + 1)
        # Get
        logger_ = Logger.get(logger.handle)
        self.assertEqual(logger_.origin, "test")

        current_logger = Logger.get()
        self.assertEqual(current_logger.origin, "test1")

        # Destroy
        logger.close()
        with self.assertRaises(ValueError):
            Logger.get(handle)
        return

    def test_save(self) -> None:
        """Tests if the logger saves to file correctly."""

        logger = Logger.new("test")
        logger.log("Line 1")
        logger.log("Line 2")
        logger.save_to_file(LOG_FILE_PATH)
        with open(LOG_FILE_PATH, "r") as f:
            content = f.read()
        self.assertEqual(content, "test\nLine 1\nLine 2\n")

    def tearDown(self) -> None:
        if os.path.exists(LOG_FILE_PATH):
            os.remove(LOG_FILE_PATH)


if __name__ == "__main__":
    unittest.main()
