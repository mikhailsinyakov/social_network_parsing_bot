import validators
from validators import ValidationFailure

def is_url(s):
    result = validators.url(s)

    if isinstance(result, ValidationFailure):
        return False

    return result