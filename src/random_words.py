import random

word_bank = [
    "the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
    "sun", "moon", "tree", "house", "book", "car", "road", "light"
]


def random_text(num_words=5):
    return ' '.join(random.choices(word_bank, k=num_words))
