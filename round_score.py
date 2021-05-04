

class RoundScore:
    def __init__(self):
        self.score = 0
        self.words = []

    def inc_score(self):
        self.score += 1

    def add_word(self, word, success):
        self.words.append((word, success))

    def reset_round(self):
        self.score = 0
        self.words = []

    def __repr__(self):
        return str(self.score)