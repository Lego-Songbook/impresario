KEYS = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
TONE_NAMES = ["C", "D", "E", "F", "G", "A", "B"]


def shift(key: str, offset: int, scale=True) -> str:
    if scale:
        return KEYS[(KEYS.index(key) + offset) % 12]
    else:
        return TONE_NAMES[(TONE_NAMES.index(key) + offset) % 7]


def normalize(key: str) -> str:
    if key in KEYS:
        return key
    else:
        if "#" in key:  # C# -> Db
            key = key.replace("#", "")
            new_key = shift(key, 1, scale=False)
            return f"{new_key}b"
        elif "b" in key:  # Gb -> F#
            key = key.replace("b", "")
            new_key = shift(key, -1, scale=False)
            return f"{new_key}#"


def key_conversion(key: str) -> str:
    """Convert a minor key to its relative major key."""
    if "m" in key:
        key = key.replace("m", "")
        key = normalize(key)
        return shift(key, 3, scale=True)
    else:
        return normalize(key)


def key_order(key):
    try:
        key = key_conversion(key)
        return KEYS.index(key)
    except ValueError:
        return -1
