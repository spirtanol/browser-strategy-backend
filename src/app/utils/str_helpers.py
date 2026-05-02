import string
import random


def generate_random_string(length: int) -> str:
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join(random.choices(letters_and_digits, k=length))
    return result_str