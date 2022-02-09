import sys
import argparse
from termcolor import colored
from synthetic.consts import (CLI_NAME, ASCII_LOGO, DEFAULT_BINS,
                              DEFAULT_SAMPLE_RATE, DEFAULT_MAX_DIST, DEFAULT_SNAPSHOTS)
from synthetic.commands.evo import Evolve
from synthetic.commands.compare import Compare
from synthetic.commands.const import Const
from synthetic.commands.eval_distance import EvalDistance
from synthetic.commands.fit import Fit
#from synthetic.commands.fit_dyn import Fit_Dyn #! Change to fit_dyn
from synthetic.commands.gen import Gen
#from synthetic.commands.gen_chi import Gen_Chi
#from synthetic.commands.gen_dyn_chi import Gen_Dyn_Chi
#from synthetic.commands.gen_switch import Gen_Switch
from synthetic.commands.prune import Prune
from synthetic.commands.rand_gen import RandGen
#from synthetic.commands.gen_dyn import Gen_Dyn
#from synthetic.commands.evo_with_E_dyn import Evolve_Dyn
#from synthetic.commands.evo_init import Evolve_Init
#from synthetic.commands.compare_dyn import Compare_Dyn
import time



def create_command(name):
    if name == 'evo':
        return Evolve(CLI_NAME)
    elif name == 'compare':
        return Compare(CLI_NAME)
    elif name == 'const':
        return Const(CLI_NAME)
    elif name == 'eval_distance':
        return EvalDistance(CLI_NAME)
    elif name == 'fit':
        return Fit(CLI_NAME)
    elif name == 'fit_dyn':
        return Fit_Dyn(CLI_NAME)
    elif name == 'gen':
        return Gen(CLI_NAME)
    elif name == 'prune':
        return Prune(CLI_NAME)
    elif name == 'rand_gen':
        return RandGen(CLI_NAME)
    #elif name=="gen_dyn":    
    #    return Gen_Dyn(CLI_NAME) 
    #elif name=="gen_chi":
    #    return Gen_Chi(CLI_NAME)
    #elif name=="gen_dyn_chi":
    #    return Gen_Dyn_Chi(CLI_NAME)
    #elif name=="gen_switch":
    #    return Gen_Switch(CLI_NAME)
    #elif name=="evo_dyn":
    #    return Evolve_Dyn(CLI_NAME)
    #elif name=="evo_init":
    #    return Evolve_Init(CLI_NAME)
    #elif name=="compare_dyn":
    #    return Compare_Dyn(CLI_NAME)
    
    return None


def show_logo():
    print()
    print(colored(ASCII_LOGO, 'magenta'))
    print()


def cli():
    t0= time.time()
    
    parser = argparse.ArgumentParser()

    parser.add_argument('command', type=str, help='command to execute')
    parser.add_argument('--inet', type=str, help='input net file')
    parser.add_argument('--inet2', type=str, help='second input net file')
    parser.add_argument('--onet', type=str, help='output net file')
    parser.add_argument('--dir', type=str, help='directory')
    parser.add_argument('--odir', type=str, help='output directory')
    parser.add_argument('--prg', type=str, help='generator program file')
    parser.add_argument('--prg2', type=str,
                        help='second generator program file')
    parser.add_argument('--oprg', type=str,
                        help='generator output program file')
    parser.add_argument('--out', type=str, help='output file')
    parser.add_argument('--gens', type=int, help='number of generations')
    parser.add_argument('--bins', type=int, help='number of distribution bins',
                        default=DEFAULT_BINS)
    parser.add_argument('--runs', type=int, help='number of generator runs')
    parser.add_argument('--undir', help='undirected network',
                        action='store_true')
    parser.add_argument('--tolerance', type=float, help='antibloat tolerance')
    parser.add_argument('--nodes', type=int, help='number of nodes')
    parser.add_argument('--edges', type=int, help='number of edges')
    parser.add_argument('--mean', help='compute mean', action='store_true')
    parser.add_argument('--gentype', type=str, help='generator type')
    parser.add_argument('--sr', type=float, help='sample rate',
                        default=DEFAULT_SAMPLE_RATE)
    parser.add_argument('--maxdist', type=int, help='maximum distance',
                        default=DEFAULT_MAX_DIST)

    parser.add_argument('--snaps', type=int, help='number of snapshots of the network',
                        default=DEFAULT_SNAPSHOTS)
    parser.add_argument('--snaplist', type=float, help='list of edge snapshots of the network') #nargs='+', for multiple args
    
    
    parser.add_argument('--mval', type=int, help='number of edges')
    parser.add_argument('--switch', type=int, help='Position to switch to second generator')
    
    
    args = vars(parser.parse_args())

    show_logo()

    command = create_command(args['command'])    
    
    if command is None:
        print('unkown command: {}'.format(command))
        sys.exit(2)
    else:
        if not command.check_args(args):
            print('error: {}'.format(command.error_msg))
            sys.exit(2)
        if not command.run(args):
            print('error: {}'.format(command.error_msg))
            sys.exit(1)
    print("Time taken: {} minutes and {} seconds".format(int((time.time()-t0)//60),round((time.time()-t0)%60)))
    
import cProfile

if __name__ == '__main__':
    cli()
    
