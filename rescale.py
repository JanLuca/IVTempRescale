#!/usr/bin/env python
# encoding: utf-8
'''
rescale.py -- Rescale a measurement to another tempature

@author:     Jan Luca Naumann

@copyright:  2015 Jan Luca Naumann (Max-Planck-Institut für Physik München). All rights reserved.

@license:    GNU General Public License 3 or any later version (http://www.gnu.org/licenses/gpl.txt)

@contact:    j.naumann@fu-berlin.de

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import os
from ROOT import *
import argparse
import time
from array import array
from time import sleep

__all__ = []
__version__ = 1.0
__date__ = '2015-09-01'
__updated__ = '2015-09-01'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
    
class writeable_dir(argparse.Action):
    def __call__(self,parser, namespace, values, option_string=None):
        dest_dir=values
        if not os.path.isdir(dest_dir):
            raise argparse.ArgumentTypeError("writeable_dir:{0} is not a valid path".format(dest_dir))
        if os.access(dest_dir, os.W_OK):
            setattr(namespace,self.dest,dest_dir)
        else:
            raise argparse.ArgumentTypeError("writeable_dir:{0} is not a writeable dir".format(dest_dir))

class InputError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg
        
def drawPlots(xvalues, xerr, yvalues, yerr, plottitle, savedir, args):
    graphs = []
    
    canvas = TCanvas(args.plottitle, args.plottitle,-50,50,1300,1000)
    canvas.cd()
    canvas.SetLeftMargin(0.15)
    canvas.SetRightMargin(0.1)
    canvas.SetBottomMargin(0.13)
    canvas.SetTopMargin(0.12)
    canvas.SetGrid()
    
    mg = TMultiGraph()
    mg.SetTitle(args.plottitle)
    
    legend = TLegend(0.18,0.67,0.47,0.87)
    legend.SetBorderSize(1)
    legend.SetFillColor(0)
    
    colors=[kBlack, kOrange+1, kAzure+1, kSpring+9]+[4+i for i in range(40)]*2
    styles=[20 + i for i in range(10)]*10
    
    for i in range(len(xvalues)):
        graphs.append(TGraphErrors(len(xvalues[i]), array("f", xvalues[i]),
                            array("f", yvalues[i]), array("f", xerr[i]), array("f", yerr[i])))
        legend.AddEntry(graphs[-1],plottitle[i],"lp")
        graphs[-1].SetMarkerStyle(styles[i])
        graphs[-1].SetMarkerColor(colors[i])
        graphs[-1].SetTitle(plottitle[i])
        mg.Add(graphs[-1])
        
    mg.Draw("AP")
    mg.GetXaxis().SetTitle(args.xlabel)
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetXaxis().SetTitleOffset(0.9)
    mg.GetXaxis().SetLabelSize(0.04)
    mg.GetXaxis().SetLabelOffset(0.004)
    mg.GetYaxis().SetTitle(args.ylabel)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().SetTitleOffset(1.4)
    mg.GetYaxis().SetLabelSize(0.04)
    mg.GetYaxis().SetLabelOffset(0.005)
    
    legend.Draw()
    sleep(0.1)
    canvas.Update()
    
    save = raw_input("Save this Plot (.png, .gif, .pdf, .eps, .C)? [y/N]")
    if save.lower()=="y" or save.lower()=="yes":
        savePlot(canvas, savedir)
    
    return 0

def savePlot(canvas, savedir):
    curtime = time.strftime("%y%m%d%H%M%S", time.localtime())
    
    if not os.path.isdir(savedir):
        os.mkdir(savedir)
        
    for suffix in [".png",".eps",".gif",".pdf",".C"]:
        canvas.SaveAs(savedir+"/"+curtime+"_Plots_rescale"+suffix)
    
    return 0

def getPrefixFactor(prefixname):
    if prefixname.lower() == "none":
        return 1
    elif prefixname.lower() == "mega":
        return 1./1000000.
    elif prefixname.lower() == "kilo":
        return 1./1000.
    elif prefixname.lower() == "milli":
        return 1000
    elif prefixname.lower() == "micro":
        return 1000000
    elif prefixname.lower() == "nano":
        return 1000000000
    else:
        raise argparse.ArgumentTypeError("{0} is not a known unit prefix".format(prefixname))

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Jan Luca Naumann on %s.
  Copyright 2015 Jan Luca Naumann (Max-Planck-Institut für Physik München). All rights reserved.

  Licensed under the GNU GPL 3.0 or any later version
  http://www.gnu.org/licenses/gpl.txt
  
USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = argparse.ArgumentParser(description=program_license, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-g', dest='gap', help="Energy gap of Si (in eV) [default: %(default)s]", default="1.12", metavar='ENERGY')
        parser.add_argument('-t', dest='intemp', help="Tempature (in C) of measurement in input file [default: %(default)s]", default="-40", metavar='TEMPATURE')
        parser.add_argument('-o', dest='outputdir', action=writeable_dir, help="Directory for the output files (e.g. plots, raw data) [default: Name of input file]", metavar='OUTPUTDIR')
        parser.add_argument('--skip', dest='skip', help="Lines to skip at start of input files [default: %(default)s]", metavar='N', default=4, type=int)
        parser.add_argument('--voltage', dest='voltagecol', help="Column with data for voltage [default: %(default)s]", metavar='N', default=0, type=int)
        parser.add_argument('--voltagedev', dest='voltagedevcol', help="Column with data for voltage deviation [default: not used]", metavar='N', default=-1, type=int)
        parser.add_argument('--current', dest='currentcol', help="Column with data for current [default: %(default)s]", metavar='N', default=2, type=int)
        parser.add_argument('--currentdev', dest='currentdevcol', help="Column with data for current deviation [default: %(default)s]", metavar='N', default=3, type=int)
        parser.add_argument('--xlabel', dest='xlabel', help="Label for x-axis [default: %(default)s]", metavar='STR', default="Voltage [V]")
        parser.add_argument('--ylabel', dest='ylabel', help="Label for y-axis [default: %(default)s]", metavar='STR', default="Current [#muA]")
        parser.add_argument('--xunitpre', dest='xunitprefix', help="Unit prefix for x-axis [default: %(default)s]", metavar='STR', default="none")
        parser.add_argument('--yunitpre', dest='yunitprefix', help="Unit prefix for y-axis [default: %(default)s]", metavar='STR', default="micro")
        parser.add_argument('inputfile', help="Input file with data to rescale", type=argparse.FileType('r'))
        parser.add_argument('comparefile', help="Input file with data to plot as comparison", type=argparse.FileType('r'))
        parser.add_argument('outtemp', help="Output Tempature for rescaling (in C)")
        parser.add_argument('plottitle', help="Title for the plot (can use TLatex)")
        parser.add_argument('inputlabel', help="Label for the graph of input data (can use TLatex)")
        parser.add_argument('comparelabel', help="Label for the graph of compare data (can use TLatex)")
        parser.add_argument('rescalelabel', help="Label for the graph of rescaled data (can use TLatex)")
        
        # Process arguments
        args = parser.parse_args()

        # Read input lines
        inputfile = args.inputfile.readlines()
        comparefile = args.comparefile.readlines() 
        
        # Set cols for data
        if args.voltagecol < 0:
            raise IndexError("The column for voltage has to be positive")
        else:
            voltagecol = args.voltagecol
        if args.currentcol < 0:
            raise IndexError("The column for current has to be positive")
        else:
            currentcol = args.currentcol
        voltagedevcol = args.voltagedevcol
        currentdevcol = args.currentdevcol
        
        # Get output dir
        if args.outputdir == None:
            savedir = os.path.basename(args.inputfile.name)
            savedir = os.path.splitext(savedir)[0]
        else:
            savedir = args.outputdir
        
        # Set tempature and gap
        intemp = float(args.intemp.replace(",",".")) + 273.15
        outtemp = float(args.outtemp.replace(",",".")) + 273.15
        gap = float(args.gap.replace(",",".")) * TMath.Qe()
        
        # Get unit prefix factor
        xfactor = getPrefixFactor(args.xunitprefix)
        yfactor = getPrefixFactor(args.yunitprefix)
        
        # Factor for rescale
        tempfactor = TMath.Power(outtemp/intemp, 2) * TMath.Exp((gap / (2. * TMath.K())) * (1. / intemp - 1. / outtemp))
        
        xvalues = [[],[],[]]
        yvalues = [[],[],[]]
        xerr = [[],[],[]]
        yerr = [[],[],[]]
        
        for lineinput in inputfile[args.skip:]:
            xvalues[0].append(abs(float(lineinput.split()[voltagecol].replace(",",".")) * xfactor))
            yvalues[0].append(abs(float(lineinput.split()[currentcol].replace(",",".")) * yfactor))
            if voltagedevcol > -1:
                xerr[0].append(float(lineinput.split()[voltagedevcol].replace(",",".")) * xfactor)
            else:
                xerr[0].append(0.0)
            if currentdevcol > -1:
                yerr[0].append(float(lineinput.split()[currentdevcol].replace(",",".")) * yfactor)
            else:
                yerr[0].append(0.0)
        
        for linecomp in comparefile[args.skip:]:
            xvalues[1].append(abs(float(linecomp.split()[voltagecol].replace(",",".")) * xfactor))
            yvalues[1].append(abs(float(linecomp.split()[currentcol].replace(",",".")) * yfactor))
            if voltagedevcol > -1:
                xerr[1].append(float(linecomp.split()[voltagedevcol].replace(",",".")) * xfactor)
            else:
                xerr[1].append(0.0)
            if currentdevcol > -1:
                yerr[1].append(float(linecomp.split()[currentdevcol].replace(",",".")) * yfactor)
            else:
                yerr[1].append(0.0)
                        
        for lineinput in inputfile[args.skip:]:
            xvalues[2].append(abs(float(lineinput.split()[voltagecol].replace(",",".")) * xfactor))\
            
            yvalues[2].append(abs(float(lineinput.split()[currentcol].replace(",",".")) * tempfactor * 1000000))
            
            xerr[2].append(0.0)
            yerr[2].append(0.0)
                
        plottitle = [args.inputlabel, args.comparelabel, args.rescalelabel]
        
        drawPlots(xvalues, xerr, yvalues, yerr, plottitle, savedir, args)

        raw_input("Hit Enter to close!")

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-g 1.12")
        sys.argv.append("/home/iwsatlas1/naumann/Documents/CIS-Productions/BATCH_312967/BARE_LUB/WAFER12/STD2_1.3e16_40C_2days_Anneling/IV_STD2_1.3e16_40C_2days_Anneling_150828115743.dat")
        sys.argv.append("/home/iwsatlas1/naumann/Documents/CIS-Productions/BATCH_312967/BARE_LUB/WAFER12/STD2_1.3e16_25C_2days_Anneling/IV_STD2_1.3e16_25C_2days_Anneling_150828125301.dat")
        sys.argv.append("-25")
        sys.argv.append("Test")
        sys.argv.append("Label_164b46v4v5v4v")
        sys.argv.append("Label_2")
        sys.argv.append("Label_3")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'rescale.test2_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    sys.exit(main())