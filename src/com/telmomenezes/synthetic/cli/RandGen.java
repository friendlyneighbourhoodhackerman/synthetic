package com.telmomenezes.synthetic.cli;

import com.telmomenezes.synthetic.NetParams;
import com.telmomenezes.synthetic.generators.Generator;
import com.telmomenezes.synthetic.generators.GeneratorFactory;

public class RandGen extends Command {
    
	@Override
	public String name() {return "randgen";}
	
	
	@Override
	public String help() {
		String help = "Create a random generator program.\n";
		help += "$ synt randgen -oprg <out_generator>\n";
		return help;
    }
	
	
	@Override
	public boolean run() throws SynCliException {
    	String outProg = getStringParam("oprg");
        
    	NetParams netParams = new NetParams(0, 0, false, false, false);
        Generator gen = GeneratorFactory.create("exo", netParams, 0);
        gen.initRandom();
        
        gen.getProg().write(outProg);
    	
        System.out.println("done.");
        
        return true;
    }
}