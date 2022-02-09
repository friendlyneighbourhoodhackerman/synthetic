import random
from synthetic.utils import current_time_millis


def within_tolerance(fitness, best_fitness, tolerance):
    return abs(fitness - best_fitness) < tolerance


class EvaluatedIndividual(object):
    def __init__(self, distances_to_net, generator, net):
        self.generator = generator
        self.distances = distances_to_net.compute(net)
        
        # TODO: other types of fitness
        self.fitness = max(self.distances)

    def is_better_than(self, eval_indiv, best_fitness, tolerance, mean=False):
        if mean==False:
            fitness_orig = self.fitness
            fitness_targ = eval_indiv.fitness
        elif mean==True:
            fitness_orig = sum(self.distances)/len(self.distances)
            fitness_targ = sum(eval_indiv.distances)/len(eval_indiv.distances) 

        if tolerance <= 0:
            return fitness_orig < fitness_targ

        if within_tolerance(fitness_orig, best_fitness, tolerance):
            if not within_tolerance(fitness_targ, best_fitness, tolerance):
                return True
            else:
                return (self.generator.prog.size() <
                        eval_indiv.generator.prog.size())
        return False


class Evo(object):
    def __init__(self, net, distances_to_net, generations, tolerance,
                 base_generator, out_dir, sample_ratio):
        self.distances_to_net = distances_to_net
        self.generations = generations
        self.tolerance = tolerance
        self.base_generator = base_generator
        self.out_dir = out_dir
        self.sample_ratio = sample_ratio

        # number of nodes and edges in target network
        self.nodes = len(net.vs)
        self.edges = len(net.es)

        # best individuals
        self.best_individual = None
        self.best_fit_individual = None
        self.best_fit_individual_1=None
        #self.best_fit_individual_2=None

        # state
        self.curgen = 0
        self.best_count = 0

        # timers
        self.gen_time = 0
        self.sim_time = 0.
        self.fit_time = 0.

    def run(self):
        # init state
        self.gen_time = 0
        self.sim_time = 0
        self.fit_time = 0
        self.best_count = 0
        self.write_log_header()

        # init population
        generator = self.base_generator.spawn_random()
        net = generator.run(self.nodes, self.edges, self.sample_ratio)
        self.best_fit_individual = EvaluatedIndividual(self.distances_to_net,
                                                       generator, net)
        self.best_individual = self.best_fit_individual
        generator = self.base_generator.spawn_random()
        nets = generator.run(self.nodes, self.edges, self.sample_ratio)
        self.best_individual = EvaluatedIndividual(self.distances_to_net,
                                                       generator, nets)

        generator = self.base_generator.spawn_random()
        nets = generator.run(self.nodes, self.edges, self.sample_ratio)
        self.best_fit_individual_1 = EvaluatedIndividual(self.distances_to_net,
                                                       generator, nets)    

        #generator = self.base_generator.spawn_random()
        #nets = generator.run(self.nodes, self.edges, self.sample_ratio)
        #self.best_fit_individual_2 = EvaluatedIndividual(self.distances_to_net,
        #                                               generator, nets)
        #self.best_individual = copy.deepcopy(self.best_fit_individual)
        #self.best_fit_individual_1 = copy.deepcopy(self.best_fit_individual)
        #self.best_fit_individual_2 = copy.deepcopy(self.best_fit_individual)

        self.generator_list={}
        
        self.generator_list={'best': self.best_individual,'best_fit': self.best_fit_individual,
                        'best_fit_1':self.best_fit_individual_1}

        entry_list = list(self.generator_list.keys())
        random_entry = random.choice(entry_list)

        # evolve
        stable_gens = 0
        self.curgen = 0
        while stable_gens < self.generations:
            self.curgen += 1
            stable_gens += 1

            start_time = current_time_millis()

            sim_time = 0
            fit_time = 0

            if random.choice([True, False]):
                random_entry = random.choice(entry_list)
                print(random_entry)
                generator = self.generator_list[random_entry].generator.clone()
                #generator.prog.write('{}/test4.txt'.format(self.out_dir))
                generator = generator.mutate()
                #generator.prog.write('{}/test5.txt'.format(self.out_dir))
                #generator = self.best_fit_individual.generator.clone()
            else:
                random_entries = random.sample(entry_list,2)
                print(random_entries)
                generator1=self.generator_list[random_entries[0]].generator.clone()
                generator2=self.generator_list[random_entries[1]].generator.clone()
                generator = generator1.recombine(generator2)
                
                #generator1.prog.write('{}/test1.txt'.format(self.out_dir))
                #generator2.prog.write('{}/test2.txt'.format(self.out_dir))
                #generator.prog.write('{}/test3.txt'.format(self.out_dir))
                #generator = self.best_individual.generator.clone()

            

            time0 = current_time_millis()
            net = generator.run(self.nodes, self.edges, self.sample_ratio)
            sim_time += current_time_millis() - time0
            time0 = current_time_millis()
            individual = EvaluatedIndividual(self.distances_to_net,
                                             generator, net)
            fit_time += current_time_millis() - time0

            best_fitness = self.best_fit_individual.fitness
            #best_meandiss = sum(self.best_fit_individual_1.distances)/len(self.best_fit_individual_1.distances)

            if individual.is_better_than(self.best_fit_individual,
                                         best_fitness, 0):
                self.best_fit_individual = individual
                self.generator_list['best_fit'] = self.best_fit_individual
                self.on_new_best(gene='best_fit')
                stable_gens = 0
                self.on_generation(gene='best_fit')

            if individual.is_better_than(self.best_individual, best_fitness,
                                         self.tolerance):
                self.best_individual = individual
                self.generator_list['best'] = self.best_individual
                self.on_new_best(gene='best')
                self.on_generation(gene='best')
                stable_gens = 0
            
            if individual.is_better_than(self.best_fit_individual_1, best_fitness,
                                         0, mean=True):
                self.best_fit_individual_1 = individual
                self.generator_list['best_fit_1'] = self.best_fit_individual_1
                self.on_new_best(gene='best_fit_1')
                self.on_generation(gene='best_fit_1')
                

            # time it took to compute the generation
            gen_time = current_time_millis() - start_time
            gen_time /= 1000
            sim_time /= 1000
            fit_time /= 1000

            print('stable generation: {}'.format(stable_gens))
            #self.on_generation()

        print('Done.')

    def on_new_best(self,gene='best'):
        suffix = '{}_gen{}'.format(self.best_count, self.curgen)
        best_gen = self.best_individual.generator

        # write net
        #best_gen.net.save('{}/bestnet{}.gml'.format(self.out_dir, suffix))
        best_gen.net.save('{}/bestnet.gml'.format(self.out_dir))

        # write progs
        if gene=='best':
            #best_gen.prog.write('{}/bestprog{}.txt'.format(self.out_dir, suffix))
            best_gen.prog.write('{}/bestprog.txt'.format(self.out_dir))
            self.best_count += 1

        elif gene=='best_fit':
            self.best_fit_individual.generator.prog.write('{}/bestfitprog.txt'.format(self.out_dir))
        elif gene=='best_fit_1':
            self.best_fit_individual_1.generator.prog.write('{}/bestdissprog.txt'.format(self.out_dir))
    

    def write_log_header(self):
        # write header of log file
        with open('{}/evo_best.csv'.format(self.out_dir), 'w') as log_file:
            header = 'gen,best_fit,best_geno_size,gen_comp_time,sim_comp_time,'
            'fit_comp_time'
            stat_names = [stat_type.name
                          for stat_type
                          in self.distances_to_net.targ_stats_set.stat_types]
            header = '{},{}\n'.format(header, ','.join(stat_names))
            log_file.write(header)

        with open('{}/evo_bestfit.csv'.format(self.out_dir), 'w') as log_file:
            header = 'gen,best_fit,best_geno_size,gen_comp_time,sim_comp_time,'
            'fit_comp_time'
            stat_names = [stat_type.name
                          for stat_type
                          in self.distances_to_net.targ_stats_set.stat_types]
            header = '{},{}\n'.format(header, ','.join(stat_names))
            log_file.write(header)

        with open('{}/evo_bestdiss.csv'.format(self.out_dir), 'w') as log_file:
            header = 'gen,best_fit,best_geno_size,gen_comp_time,sim_comp_time,'
            'fit_comp_time'
            stat_names = [stat_type.name
                          for stat_type
                          in self.distances_to_net.targ_stats_set.stat_types]
            header = '{},{}\n'.format(header, ','.join(stat_names))
            log_file.write(header)

    def on_generation(self, gene='best'):
        if gene=='best':
            dists = [str(dist) for dist in self.best_individual.distances]

            # write log line for generation
            with open('{}/evo_best.csv'.format(self.out_dir), 'a') as log_file:
                row = ','.join([str(metric) for metric in (self.curgen,
                                self.best_individual.fitness,
                                self.best_individual.generator.prog.size(),
                                self.gen_time, self.sim_time, self.fit_time)])
                row = '{},{}\n'.format(row, ','.join(dists))
                log_file.write(row)

            # print info
            print(self.gen_info_string())
            stat_names = [stat_type.name
                        for stat_type
                        in self.distances_to_net.targ_stats_set.stat_types]
            items = ['{}: {}'.format(stat_names[i], dists[i])
                    for i in range(len(stat_names))]
            print('; '.join(items))

        if gene=='best_fit':
            dists = [str(dist) for dist in self.best_fit_individual.distances]

            # write log line for generation
            with open('{}/evo_bestfit.csv'.format(self.out_dir), 'a') as log_file:
                row = ','.join([str(metric) for metric in (self.curgen,
                                self.best_fit_individual.fitness,
                                self.best_fit_individual.generator.prog.size(),
                                self.gen_time, self.sim_time, self.fit_time)])
                row = '{},{}\n'.format(row, ','.join(dists))
                log_file.write(row)

        if gene=='best_fit_1':
            dists = [str(dist) for dist in self.best_fit_individual_1.distances]

            # write log line for generation
            with open('{}/evo_bestdiss.csv'.format(self.out_dir), 'a') as log_file:
                row = ','.join([str(metric) for metric in (self.curgen,
                                self.best_fit_individual_1.fitness,
                                self.best_fit_individual_1.generator.prog.size(),
                                self.gen_time, self.sim_time, self.fit_time)])
                row = '{},{}\n'.format(row, ','.join(dists))
                log_file.write(row)



    def info_string(self):
        lines = ['stable generations: {}'.format(self.generations),
                 'directed: {}'.format(
                    self.distances_to_net.net.is_directed()),
                 'target net node count: {}'.format(self.nodes),
                 'target net edge count: {}'.format(self.edges),
                 'distribution bins: {}'.format(self.distances_to_net.bins),
                 'tolerance: {}'.format(self.tolerance)]
        return '\n'.join(lines)

    def gen_info_string(self):
        items = ['gen #{}'.format(self.curgen),
                 'best fitness: {}'.format(self.best_individual.fitness),
                 'best genotype size: {}'.format(
                    self.best_individual.generator.prog.size()),
                 'gen comp time: {}s.'.format(self.gen_time),
                 'sim comp time: {}s.'.format(self.sim_time),
                 'fit comp time: {}s.'.format(self.fit_time)]
        return '; '.join(items)
