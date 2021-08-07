from utils.file_reader import read_as_string
import os

TEST_FILE_NAME = "test_file.txt"


def test_read_as_string():
    text = "a test file to be checked"
    "to see if everything is ok."

    with open(TEST_FILE_NAME, "w") as f:
        f.write(text)

    chars = read_as_string(TEST_FILE_NAME)
    assert chars == text

    os.remove(TEST_FILE_NAME)
