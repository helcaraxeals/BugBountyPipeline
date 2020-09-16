import string
import random


def generate_token(length: int = 10):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=length))
