import string
import random


# функция для генерации года из случайных цифр и букв
def generate_short_code(length: int = 10) -> str:

    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))
