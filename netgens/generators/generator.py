import random
import numpy as np
from igraph import *
import netgens.progs.prog as prog
from netgens.generators.genvar import *


def create_exo_generator(directed):
    if directed:
        genvars = (GenVar.ORIGID, GenVar.TARGID, GenVar.ORIGINDEG, GenVar.ORIGOUTDEG,
                   GenVar.TARGINDEG, GenVar.TARGOUTDEG, GenVar.DIST, GenVar.DIRDIST, GenVar.REVDIST)
    else:
        genvars = (GenVar.ORIGID, GenVar.TARGID, GenVar.ORIGDEG, GenVar.TARGDEG, GenVar.DIST)
    return Generator(genvars, directed)


def create_endo_generator(directed):
    if directed:
        genvars = (GenVar.ORIGINDEG, GenVar.ORIGOUTDEG, GenVar.TARGINDEG, GenVar.TARGOUTDEG,
                   GenVar.DIST, GenVar.DIRDIST, GenVar.REVDIST)
    else:
        genvars = (GenVar.ORIGDEG, GenVar.TARGDEG, GenVar.DIST)
    return Generator(genvars, directed)


class Generator(object):
    def __init__(self, genvars, directed):
        self.directed = directed

        self.genvars = genvars
        self.var_names = [genvar2str(gv) for gv in genvars]
        self.var_count = len(genvars)
        self.prog = prog.Prog(self.var_names)

        self.net = None

        self.valid = True
        self.iterations = -1

        self.nodes = 0
        self.trials = 0
        self.sample_origs = None
        self.sample_targs = None
        self.sample_weights = None

    def clone(self):
        cgen = Generator(self.genvars, self.directed)
        cgen.prog = self.prog.clone()
        return cgen

    def load(self, file_path):
        self.prog = prog.load(self.var_names, file_path)

    def distance(self, orig, targ, mode, max_dist=5):
        sp = self.net.get_shortest_paths(orig, to=targ, mode=mode)[0]
        if len(sp) == 0:
            return max_dist + 1
        else:
            return max(max_dist, len(sp) - 1)

    def set_prog_vars(self, orig, targ):
        for i in range(self.var_count):
            gv = self.genvars[i]
            if gv == GenVar.ORIGID:
                self.prog.vars[i] = orig
            elif gv == GenVar.TARGID:
                self.prog.vars[i] = targ
            elif gv == GenVar.ORIGDEG:
                self.prog.vars[i] = self.net.degree(orig, mode=ALL)
            elif gv == GenVar.ORIGINDEG:
                self.prog.vars[i] = self.net.degree(orig, mode=IN)
            elif gv == GenVar.ORIGOUTDEG:
                self.prog.vars[i] = self.net.degree(orig, mode=OUT)
            elif gv == GenVar.TARGDEG:
                self.prog.vars[i] = self.net.degree(targ, mode=ALL)
            elif gv == GenVar.TARGINDEG:
                self.prog.vars[i] = self.net.degree(targ, mode=IN)
            elif gv == GenVar.TARGOUTDEG:
                self.prog.vars[i] = self.net.degree(targ, mode=OUT)
            elif gv == GenVar.DIST:
                self.prog.vars[i] = self.distance(orig, targ, mode=ALL)
            elif gv == GenVar.DIRDIST:
                self.prog.vars[i] = self.distance(orig, targ, mode=OUT)
            elif gv == GenVar.REVDIST:
                self.prog.vars[i] = self.distance(orig, targ, mode=IN)

    def generate_sample(self):
        for i in range(self.trials):
            orig_index = -1
            targ_index = -1
            found = False

            while not found:
                orig_index = random.randrange(self.nodes)
                targ_index = random.randrange(self.nodes)

                if orig_index != targ_index:
                    if self.net[orig_index, targ_index] == 0:
                        found = True

            self.sample_origs[i] = orig_index
            self.sample_targs[i] = targ_index

    def cycle(self, master=None):
        if master is None:
            self.generate_sample()
        else:
            self.sample_origs = master.sample_origs
            self.sample_targs = master.sample_targs

        total_weight = 0.
        for i in range(self.trials):
            self.set_prog_vars(self.sample_origs[i], self.sample_targs[i])

            weight = max(self.prog.eval(), 0.)
            self.sample_weights[i] = weight
            total_weight += weight

        if total_weight == 0.:
            for i in range(self.trials):
                self.sample_weights[i] = 1.
                total_weight += 1.

        targ_weight = random.random() * total_weight
        i = 0
        total_weight = self.sample_weights[i]
        while targ_weight > total_weight:
            i += 1
            total_weight += self.sample_weights[i]
        best_orig_index = self.sample_origs[i]
        best_targ_index = self.sample_targs[i]

        orig_node = self.net.get_nodes()[best_orig_index]
        targ_node = self.net.get_nodes()[best_targ_index]

        return orig_node, targ_node

    def weights_dist(self, gen):
        total_weight1 = 0.
        total_weight2 = 0.

        for i in range(self.trials):
            total_weight1 += self.sample_weights[i]
            total_weight2 += gen.sample_weights[i]

        dist = 0.
        for i in range(self.trials):
            self.sample_weights[i] /= total_weight1
            gen.sample_weights[i] /= total_weight2
            dist += abs(self.sample_weights[i] - gen.sample_weights[i])
        dist /= self.trials
        return dist

    def run(self, nodes, edges, sample_ratio, shadow=None):
        self.nodes = nodes
        self.trials = int(sample_ratio * nodes * edges)
        if self.trials < 2:
            self.trials = 2
        self.sample_origs = np.zeros(self.trials, dtype=np.uint64)
        self.sample_targs = np.zeros(self.trials, dtype=np.uint64)
        self.sample_weights = np.zeros(self.trials)

        dist = 0.

        self.net = Graph(n=nodes, directed=self.directed)

        if shadow is not None:
            shadow.net = self.net

        # create edges
        self.iterations = 0
        while self.iterations < edges:
            orig, targ = self.cycle()

            if shadow is not None:
                shadow.cycle(self)
                dist += self.weights_dist(shadow)

            self.net.add_edge(orig, targ)
            self.iterations += 1

        dist /= edges
        return dist

    def init_random(self):
        self.prog = prog.create_random(self.var_names)

    def recombine(self, parent2):
        generator = Generator(self.genvars, self.directed)
        generator.prog = self.prog.recombine(parent2.prog)
        return generator

    def mutate(self):
        random_gen = Generator(self.genvars, self.directed)
        random_gen.init_random()
        return self.recombine(random_gen)
