def pad_or_slice(data: str) -> str:
    # Rich Presence text fields are
    # Restricted within 2 to 32 characters
    if len(data) == 1:
        return data + '\u200b'
    elif len(data) > 32:
        return data[:30] + '..'

    return data
