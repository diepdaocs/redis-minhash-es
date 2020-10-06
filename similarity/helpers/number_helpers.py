def is_number(word):
    try:
        float(word)
        return True
    except ValueError:
        return False
