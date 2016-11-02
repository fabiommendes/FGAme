def snake_case(name):
    """
    Converts CamelCase to snake_case.
    """

    chars = []
    upper_seq = 0
    for i, c in enumerate(name):
        if c.isupper():
            upper_seq += 1
            if i and name[i - 1].islower():
                chars.append('_')
        if c.islower():
            if upper_seq > 1:
                chars.insert(-1, '_')
            upper_seq = 0
        chars.append(c.lower())
    return ''.join(chars)