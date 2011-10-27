#!/usr/bin/env python
# encoding: utf-8

__author__ = "Telmo Menezes (telmo@telmomenezes.com)"
__date__ = "Oct 2011"


import random
import math
from syn.core import *
from syn.drmap import *


class Evo:
    def __init__(self, targ_net, mrate=0.3, rrate=0.7, pop=100, tournament=10):
        self.targ_net = targ_net
        self.mrate = mrate
        self.rrate = rrate
        self.tournament = tournament
        self.pop = pop
        self.population = []

        self.syn_net = targ_net.load_net()
        self.nodes = net_node_count(self.syn_net)
        self.edges = net_edge_count(self.syn_net)
        self.nodes = 5000
        self.edges = self.nodes * (net_edge_count(self.syn_net) / net_node_count(self.syn_net))
        self.max_cycles = self.edges * 100

        seed_random()

    def __del__(self):
        for i in range(self.pop):
            destroy_gpgenerator(self.population[i])
        destroy_net(self.syn_net)

    def run(self):
        self.pop = 10
        bins = 10
        draw_drmap(self.syn_net, 'target.png', bins=bins)
        
        print 'Evolving gpgenerator'
        print 'Nodes:', self.nodes
        print 'Edges:', self.edges
        print 'Population:', self.pop

        # init population
        self.population = []
        for i in range(self.pop):
            gen = create_gpgenerator()
            self.population.append(gen)

        print 'Population initialized.'

        cycle = 0
        
        # evolutionary loop
        best_fit = 9999999
        while True:
            best_gen_fit = 9999999
            best_gen = None
            # eval fitness
            for i in range(self.pop):
                gen = self.population[i]
                net = gpgen_run(gen, self.nodes, self.edges, self.max_cycles)

                compute_pageranks(self.syn_net)
                compute_pageranks(net)

                drmap1 = get_drmap_with_limits(self.syn_net, bins, -7.0, 7.0, -7.0, 7.0)
                drmap_log_scale(drmap1)
                drmap_normalize(drmap1)

                drmap2 = get_drmap_with_limits(net, bins, -4.0, 4.0, -4.0, 4.0)
                drmap_log_scale(drmap2)
                drmap_normalize(drmap2)

                fit = drmap_emd_dist(drmap1, drmap2)

                destroy_drmap(drmap1)
                destroy_drmap(drmap2)
                print i, fit
                if fit < best_gen_fit:
                    best_gen_fit = fit
                    best_gen = self.population[i]
                    print_gpgen(self.population[i])
                    draw_drmap(net, 'best.png', bins=bins)
                destroy_net(net)

                if fit < best_fit:
                    best_fit = fit

            print 'Generation %d => best fitness: %f [%f]' % (cycle, best_gen_fit, best_fit)
            cycle += 1

            # next generation
            newgen = []
            
            newgen.append(clone_gpgenerator(best_gen))

            for i in range(1, self.pop):
                clone = clone_gpgenerator(best_gen)
                chicken = create_gpgenerator()
                child = recombine_gpgens(clone, chicken)
                destroy_gpgenerator(chicken)
                destroy_gpgenerator(clone)
                newgen.append(child)

            # replace generations
            for i in range(self.pop):
                destroy_gpgenerator(self.population[i])
            self.population = newgen


    def run2(self):
        bins = 10
        draw_drmap(self.syn_net, 'target.png', bins=bins)
        
        print 'Evolving gpgenerator'
        print 'Nodes:', self.nodes
        print 'Edges:', self.edges
        print 'Population:', self.pop
        print 'Mutation rate:', self.mrate
        print 'Tournament:', self.tournament
        print 'Recombination rate:', self.rrate

        # init population
        self.population = []
        self.fitness = []
        for i in range(self.pop):
            gen = create_gpgenerator()
            self.population.append(gen)
            self.fitness.append(0)

        print 'Population initialized.'

        cycle = 0
        best_fit = 9999999
        # evolutionary loop
        while True:
            # eval fitness
            for i in range(self.pop):
                gen = self.population[i]
                net = gpgen_run(gen, self.nodes, self.edges, self.max_cycles)

                compute_pageranks(self.syn_net)
                compute_pageranks(net)

                drmap1 = get_drmap_with_limits(self.syn_net, bins, -7.0, 7.0, -7.0, 7.0)
                drmap_log_scale(drmap1)
                drmap_normalize(drmap1)

                drmap2 = get_drmap_with_limits(net, bins, -4.0, 4.0, -4.0, 4.0)
                drmap_log_scale(drmap2)
                drmap_normalize(drmap2)

                fit = drmap_emd_dist(drmap1, drmap2)

                destroy_drmap(drmap1)
                destroy_drmap(drmap2)
                self.fitness[i] = fit
                print i, fit
                if fit < best_fit:
                    best_fit = fit
                    print_gpgen(self.population[i])
                    draw_drmap(net, 'best.png', bins=bins)
                destroy_net(net)

            print 'Generation %d => best fitness: %f' % (cycle, best_fit)
            cycle += 1

            # next generation
            newgen = []
            
            for i in range(self.pop):
                parent1 = -1
                for i in range(self.tournament):
                    parent1 = random.randint(0, self.pop - 1)
                    if (parent1 < 0) or (self.fitness[i] < self.fitness[parent1]):
                        parent1 = i

                child = None
                # recombine or clone
                if random.uniform(0, 1) < self.rrate:
                    parent2 = -1
                    for i in range(self.tournament):
                        parent2 = random.randint(0, self.pop - 1)
                        if (parent2 < 0) or (self.fitness[i] < self.fitness[parent2]):
                            parent2 = i

                    child = recombine_gpgens(self.population[parent1], self.population[parent2])
                else:
                    child = clone_gpgenerator(self.population[parent1])

                # mutate
                if random.uniform(0, 1) < self.mrate:
                    chicken = create_gpgenerator()
                    child2 = recombine_gpgens(child, chicken)
                    destroy_gpgenerator(chicken)
                    destroy_gpgenerator(child)
                    child = child2

                newgen.append(child)

            # replace generations
            for i in range(self.pop):
                destroy_gpgenerator(self.population[i])
            self.population = newgen
