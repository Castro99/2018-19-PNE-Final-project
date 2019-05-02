#Copy from previous lessons

class Seq:
    """A class for representing sequences"""

    def __init__(self, strbases):
        # this method is called every time a new object is created

        self.strbases = strbases

    def len(self):
        return str(len(self.strbases))

    def complement(self):
        seq = self.strbases
        seq = seq.upper()
        for x, letter in enumerate(seq):
            if letter == 'A':
                seq = seq[:x] + seq[x:].replace('A', 'T')
            if letter == 'T':
                seq = seq[:x] + seq[x:].replace('T', 'A')
            if letter == 'C':
                seq = seq[:x] + seq[x:].replace('C', 'G')
            if letter == 'G':
                seq = seq[:x] + seq[x:].replace('G', 'C')
        return seq

    def reverse(self):
        seq = self.strbases.upper()[::-1]
        return seq

    def count(self, base):
        base=base.upper()
        return str(self.strbases.upper().count(base))

    def percentage(self, base):
        seq = self.strbases.upper()
        base=base.upper()
        counter= seq.count(base)
        line = len(seq)
        return str(round(100.0 * counter/line, 2))