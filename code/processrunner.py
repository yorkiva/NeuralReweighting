import subprocess
import card_maker
import os.path
import sys
import numpy as np
from VLQCouplingCalculator import VLQCouplingCalculator as vlq

def processor(outdir, outfile, run_command, runname, proc, m, GM, MG_loc):

    if not (os.path.exists(outdir) and os.path.exists(outfile)):
        subprocess.call([run_command, runname, "-f"])
        
    if not (os.path.exists(outdir) and os.path.exists(outfile)):
        print "Something went wrong! Maybe MG didn't run properly. Retrying for m = %i, c1 = %i and c2 = %i" %(m, c1, c2)
        print outdir, outfile
        card_maker.param_editor(proc, m, GM, MG_loc)
        card_maker.run_editor(proc, "_00", MG_loc)
        processor(outdir, outfile, run_command, runname,  proc, m, 1.0, MG_loc)

try:
    proc = sys.argv[1]
except:
    print "No process specified. Exiting"
    sys.exit(1)

basedir = "/code/avik/ReweightProject/"
MGdir = basedir + "MG5_aMC_v2_6_5/"  
procdir = MGdir + "/VLQ_" + proc
print("Process directory: " + procdir)
masses = np.arange(1100, 2400, 200)
#masses = [1700]
GMs = np.append(np.arange(0.05, 0.3, 0.05), np.arange(0.3, 0.8, 0.1))
GMs = np.append(GMs, np.arange(0.8, 1.05, 0.05))
#GMs= [0.05]
for m in masses:
    card_maker.param_editor(proc, m, 1.0, MGdir)
    card_maker.run_editor(proc, "_00", MGdir)
    card_maker.rewtcardmaker(proc, np.arange(m - 200., m + 201., 100.), GMs, MGdir)
    runname = "RUN_" + proc + "_m_" + str(int(m))
    outdir = procdir + "/Events/" + runname
    outfile = outdir + "/" + runname + "__00_banner.txt"
    run_command = procdir + "/bin/generate_events"
    processor(outdir, outfile, run_command, runname, proc, m, 1.0, MGdir )

