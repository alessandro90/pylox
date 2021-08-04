def read_as_string(fname: str) -> str:
    """Return file content as a single string"""
    with open(fname, mode="r") as source:
        return source.read()
