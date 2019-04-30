class Seq:

    def  __init__  (self, strbases):

        self.strbases = strbases
    def len(self):
        return len(self.strbases)

    def compl(self):
        word = ''
        for letter in self.strbases:
            self.strbases = self.strbases.upper()
            if letter == 'A':
                word += 'T'
            elif letter == 'C':
                word += 'G'
            elif letter == 'G':
                word += 'C'
            elif letter == 'T':
                word += 'A'
        c = Seq(word)
        return c

    def reverse(self):
        s = self.strbases[::-1]
        seq = Seq(s)
        return seq




    def Count(self, base):
        self.base = base
        count = self.strbases.count(base)
        return count

    def perc(self, base):
        self.base = base
        p = round(100.0 * self.strbases.count(base) / len(self.strbases), 2)
        return p