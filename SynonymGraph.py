from nltk.corpus import wordnet
import igraph
import os

# # only needs to be run once per host
# import nltk
# nltk.download('wordnet')
# nltk.download('omw-1.4')

DEPTH = 2


def main():
    sg = SynonymGraph()
    while True:
        word = input('?')
        sg.find_children(word)
        out_file = sg.write_svg(word)
        os.startfile(out_file)


class Memoize:
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}

    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.fn(*args)
        return self.memo[args]


class SynonymGraph:
    def __init__(self):
        self.g = igraph.Graph()

    def find_children(self, start_word, depth=DEPTH):
        if depth == 0:
            # end the recursion
            return

        n = self.get_vertex(start_word)
        if n['found_children']:
            return

        for syn in get_synonyms(start_word):
            s = self.get_vertex(syn)
            self.g.add_edge(n, s)
            self.find_children(syn, depth=depth - 1)

        n['found_children'] = True

    def get_vertex(self, name):
        try:
            v = self.g.vs(name_eq=name)
            assert len(v) in [0, 1]
            if len(v):
                return v[0]

        except KeyError:
            # graph is empty
            pass

        # either fell through from empty graph or there's no vertex with that name
        v = self.g.add_vertex(name)
        v['found_children'] = False
        return v

    def write_svg(self, word):
        out_file = f'output\\{word}.svg'
        vs = self.g.vs.select(_degree_gt=1)
        to_plot = self.g.subgraph(vs)

        igraph.plot(
                to_plot,
                out_file,
                layout=self.g.layout("kk"),
                bbox=(1152, 522),
                margin=20,
                autocurve=False,
                vertex_label=self.g.vs["name"],
                vertex_size=40,
        )

        return out_file


@Memoize
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())

    synonyms.remove(word)
    return synonyms


if __name__ == '__main__':
    main()
