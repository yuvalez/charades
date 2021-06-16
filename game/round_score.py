

class RoundScore:
    def __init__(self):
        self.score = 0
        self.words = []

    def inc_score(self, inc_score=1):
        self.score += inc_score

    def dec_score(self, dec_amount=1):
        self.score -= dec_amount

    def add_word(self, word, success):
        self.words.append((word, success))

    def reset_round(self):
        self.score = 0
        self.words = []

    def __str__(self):
        if isinstance(self.score, float):
            if not self.score.is_integer():
                return f"{self.score:.1f}"

        return f"{self.score}"

