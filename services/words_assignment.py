import random
import logging
from collections import defaultdict


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

word_pool = [
    {"word": "apple", "description": "a fruit"},
    {"word": "banana", "description": "yellow and curved"},
    {"word": "cat", "description": "a purring pet"},
    {"word": "dog", "description": "man's best friend"},
    {"word": "elephant", "description": "has a trunk"},
    {"word": "fish", "description": "lives in water"},
    {"word": "grape", "description": "small and round"},
    {"word": "hat", "description": "worn on the head"},
    {"word": "ice", "description": "cold and solid"},
    {"word": "jacket", "description": "keeps you warm"},
    {"word": "kite", "description": "flies in the wind"},
    {"word": "lemon", "description": "sour and yellow"},
    {"word": "monkey", "description": "likes bananas"},
    {"word": "nut", "description": "hard-shelled snack"},
    {"word": "orange", "description": "citrus fruit"},
    {"word": "pizza", "description": "often with toppings"},
    {"word": "queen", "description": "royal lady"},
    {"word": "rabbit", "description": "hops around"},
    {"word": "sun", "description": "bright in the sky"},
    {"word": "tree", "description": "has leaves"},
    {"word": "umbrella", "description": "for rainy days"},
    {"word": "vase", "description": "holds flowers"},
    {"word": "whale", "description": "large sea creature"},
    {"word": "xylophone", "description": "musical bars"},
    {"word": "yoyo", "description": "up and down toy"},
    {"word": "zebra", "description": "striped animal"},
    {"word": "clock", "description": "tells time"},
    {"word": "wall", "description": "vertical barrier"},
    {"word": "beach", "description": "sandy area by water"},
]


async def assign_words(num_rounds, num_players, words_per_round):
    num_rounds = 3
    words_per_round = 3

    # Check if enough words are available
    total_words_needed = num_rounds * num_players * words_per_round
    if total_words_needed > len(word_pool):
        raise ValueError("Not enough unique words in the word pool.")

    # Shuffle the word pool and select the required number of words
    random.shuffle(word_pool)
    selected_words = word_pool[:total_words_needed]

    # Assign IDs and distribute words to players simultaneously
    player_words = {
        player: [[] for _ in range(num_rounds)] for player in range(1, num_players + 1)
    }
    word_id_map = defaultdict(lambda: len(word_id_map) + 1)

    for i, word in enumerate(selected_words):
        player = (i // words_per_round) % num_players + 1
        round_num = (i // (num_players * words_per_round)) % num_rounds
        word_id = word_id_map[word["word"]]
        player_word_with_id = {"id": word_id, **word}
        player_words[player][round_num].append(player_word_with_id)

    logger.info(f"Player words: {player_words}")
    return player_words
