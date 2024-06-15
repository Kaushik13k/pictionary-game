import random

# Step 1: Initialize the word pool
word_pool = [
    "apple",
    "banana",
    "cat",
    "dog",
    "elephant",
    "fish",
    "grape",
    "hat",
    "ice",
    "jacket",
    "kite",
    "lemon",
    "monkey",
    "nut",
    "orange",
    "pizza",
    "queen",
    "rabbit",
    "sun",
    "tree",
    "umbrella",
    "vase",
    "whale",
    "xylophone",
    "yoyo",
    "zebra",
    "clock",
    "wall",
    "beach",
]


async def assign_words(num_rounds, num_players, words_per_round):
    # Step 2: Setup game parameters
    num_rounds = 3
    # num_players = num_players
    words_per_round = 3

    # Step 3: Check if enough words are available
    total_words_needed = num_rounds * num_players * words_per_round
    if total_words_needed > len(word_pool):
        raise ValueError("Not enough unique words in the word pool.")

    # Step 4: Shuffle the word pool and select the required number of words
    random.shuffle(word_pool)
    selected_words = word_pool[:total_words_needed]

    # Step 5: Assign IDs and distribute words to players simultaneously
    player_words = {
        player: [{} for _ in range(num_rounds)] for player in range(1, num_players + 1)
    }
    word_id_map = {}
    current_id = 1

    for i, word in enumerate(selected_words):
        player = (i // words_per_round) % num_players + 1
        round_num = (i // (num_players * words_per_round)) % num_rounds
        if word not in word_id_map:
            word_id_map[word] = current_id
            current_id += 1
        player_words[player][round_num][word_id_map[word]] = word

    return player_words
