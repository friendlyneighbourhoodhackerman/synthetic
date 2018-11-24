from netgens.net import load_net
import netgens.generator as gen
from netgens.fitness import Fitness, Norm
from netgens.evo import Evo
from netgens.commands.command import *


class Evolve(Command):
    def __init__(self, cli_name):
        Command.__init__(self, cli_name)
        self.name = 'evo'
        self.description = 'evolve network generator'
        self.mandatory_args = ['inet', 'odir']
        self.optional_args = ['undir', 'gens', 'sr', 'bins', 'tolerance']

    def run(self, args):
        self.error_msg = None

        netfile = args['inet']
        outdir = args['odir']
        generations = arg_with_default(args, 'gens', 1000)
        sr = arg_with_default(args, 'sr', 0.0006)
        bins = arg_with_default(args, 'bins', 100)
        directed = not args['undir']
        tolerance = arg_with_default(args, 'tolerance', 0.1)
        gen_type = arg_with_default(args, 'gentype', 'exo')

        # load net
        net = load_net(netfile, directed)

        # create base generator
        base_generator = gen.create(gen_type, directed)
        if base_generator is None:
            self.error_msg = 'unknown generator type: %s' % gen_type
            return False

        # create fitness calculator
        # TODO: norm samples configurable
        fitness = Fitness(net, get_stat_dist_types(args), bins, norm=Norm.ER_MEAN_RATIO, norm_samples=30)

        # create evolutionary search
        evo = Evo(net, fitness, generations, tolerance, base_generator, outdir, sr)

        # some reports to screen
        print('target net: %s' + netfile)
        print(evo.info_string())
        print(base_generator)
        
        # write experiment params to file
        with open('%s/params.txt' % outdir, 'w') as text_file:
            text_file.write(evo.info_string())

        # run search
        evo.run()
        
        return True
