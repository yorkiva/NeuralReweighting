import os, sys, subprocess, json, glob
from optparse import OptionParser

def env_checker():
    if 'NEURWT_BASE_PATH' not in os.environ.keys():
        return False
    if 'NEURWT_MGLOC' not in os.environ.keys():
        return False
    return True

def proc_card_reader(proc_card_name):
    f = open(proc_card_name)
    out_path = ''
    model = ''
    procs = []
    for line in f:
        line = line.strip()
        if line.startswith("#"):
            continue
        if "output" in line:
            out_path = line.split()[-1]
        if "import model" in line:
            model = line.split()[-1]
        if 'add process' in line or 'generate' in line:
            procs.append(line)
    return out_path, model, procs

def proc_runner(proc_card):
    out_path, model, procs = proc_card_reader(proc_card)
    
    if out_path == '':
        print("No Specific output path is mentioned! Please modify your proc_card. Exiting")
        return '', False
    if model == '':
        print("No model has been used! Make sure that's what is intended!")
    if len(procs) == 0:
        print("No process has been mentioned! Please include the processes you wish to use. Exiting")
        return '', False

    out_path = os.environ['NEURWT_MGLOC'] + '/' + out_path

    if not check_proc_outdir(out_path):
         subprocess.call("cd {} && bin/mg5_aMC {} && cd -".format(os.environ['NEURWT_MGLOC'], proc_card), shell = True)

    if not check_proc_outdir(out_path):
        print("MG Process Runner Failed! Please check the error log and update your proc card accordingly!")
        return out_path, False

    return out_path, True

def check_proc_outdir(out_path):
    if not os.path.exists(out_path):
        return False
    if not os.path.exists(out_path + '/bin'):
        return False
    if not os.path.exists(out_path + '/bin/generate_events'):
        return False
    if not os.path.exists(out_path + '/Cards'):
        return False
    if not os.path.exists(out_path + '/Cards/param_card.dat'):
        return False
    if not os.path.exists(out_path + '/Cards/run_card.dat'):
        return False
    return True

def get_param_list(out_path):
    params = []
    f = open(out_path + '/Cards/param_card_default.dat')
    pick_param = True
    for line in f:
        line = line.strip()
        if 'Block QNUMBERS' in line:
            pick_param = False
        if 'Block' in line and 'QNUMBERS' not in line:
            pick_param = True
        if line.startswith('#'):
            continue
        if not pick_param:
            continue
        #if 'DECAY' in line or 'Auto' in line or 'auto' in line:
        #    continue
        if '#' in line:
            params.append(line.split('#')[1].split(':')[0].strip().split()[0])
    return params
    
def edit_param_card(out_path, params, param_dict):
    f_def = open(out_path + "/Cards/param_card_default.dat")
    f_new = open(out_path + "/Cards/param_card.dat", "w")
    for key in list(param_dict.keys()):
        if key not in params:
            print("param {} not found in the changeable param list! Please Check".format(key))
            param_dict.pop(key, None)
    for line in f_def:
        line_written = False
        for key in param_dict.keys():
            if "# {}".format(key) in line:
                line_entries = line.split()
                if 'DECAY' in line:
                    param_to_change = line_entries[2]
                else:
                    param_to_change = line_entries[1]
                if not type(param_dict[key]) == str:
                    new_line = line.replace(param_to_change, "{:.6e}".format(param_dict[key]))
                else:
                    new_line = line.replace(param_to_change, param_dict[key])
                f_new.write(new_line)
                line_written = True
        if not line_written:
            f_new.write(line)
    f_def.close()
    f_new.close()

def edit_run_card(out_path, run_dict):
    f_def = open(out_path + "/Cards/run_card_default.dat")
    f_new = open(out_path + "/Cards/run_card.dat", "w")
    for line in f_def:
        line_written = False
        for key in run_dict.keys():
            if key in line:
                line_entries = line.strip().split()
                param_to_change = line_entries[0]
                if key == 'systematics_program':
                    line = line.replace('systematics_program', 'Systematics_program')
                new_line = line.replace(param_to_change, str(run_dict[key]))
                if key == 'systematics_program':
                    new_line = new_line.replace('Systematics_program', 'systematics_program')
                f_new.write(new_line)
                line_written = True
        if not line_written:
            f_new.write(line)
    f_def.close()
    f_new.close()
            
def make_reweight_card(out_path, params, reweight_dict):
    f_rwt = open(out_path + "/Cards/reweight_card.dat", "w")
    launch_line = "launch --rwgt_name="
    for rewt in reweight_dict.keys():
        f_rwt.write(launch_line + rewt + '\n')
        for key in reweight_dict[rewt].keys():
            if key not in params:
                print("param {} not found in the changeable param list! Please Check".format(key))
            else:
                f_rwt.write('\tset ' + str(key) + ' ' + str(reweight_dict[rewt][key]) + '\n')
        f_rwt.write('\n\n')
    f_rwt.close()

def edit_me5_configuration(out_path, do_multicore, nb_core):
    f_config = open(out_path + "/Cards/me5_configuration.txt")
    f2 = open("me5_configuration.txt", "w")
    for line in f_config:
        if "automatic_html_opening" in line:
            f2.write("automatic_html_opening = False\n")
        elif "run_mode" in line and do_multicore:
            f2.write("run_mode = 2\n")
        elif "nb_core" in line and do_multicore:
            f2.write("nb_core = {}\n".format(nb_core))
        elif "lhapdf_py3" in line:
            f2.write("lhapdf_py3 = {}\n".format(os.environ['NEURWT_LHAPDFLOC'] + "/bin/lhapdf-config"))
        else:
            f2.write(line)
    f_config.close()
    f2.close()
    subprocess.call("cp me5_configuration.txt {}/Cards/me5_configuration.txt && rm me5_configuration.txt".format(out_path), shell=True)

def edit_mg5_configuration(do_multicore, nb_core):
    f_config = open(os.environ['NEURWT_MGLOC'] + "/input/mg5_configuration.txt")
    f2 = open("mg5_configuration.txt", "w")
    for line in f_config:
        if "automatic_html_opening" in line:
            f2.write("automatic_html_opening = False\n")
        elif "run_mode" in line and do_multicore:
            f2.write("run_mode = 2\n")
        elif "nb_core" in line and do_multicore:
            f2.write("nb_core = {}\n".format(nb_core))
        elif "lhapdf_py3" in line:
            f2.write("lhapdf_py3 = {}\n".format(os.environ['NEURWT_LHAPDFLOC'] + "/bin/lhapdf-config"))
        else:
            f2.write(line)
    f_config.close()
    f2.close()
    subprocess.call("cp mg5_configuration.txt {}/input/mg5_configuration.txt && rm mg5_configuration.txt".format(os.environ['NEURWT_MGLOC']), shell=True)

def processor(outdir, outfile, run_command, runname):
    if bool(glob.glob(outdir)) and bool(glob.glob(outfile)):
        print("Run {} already Exists".format(runname))
        return True

    subprocess.call([run_command, runname, "-f"])
        
    if not (bool(glob.glob(outdir)) and bool(glob.glob(outfile))):
        print("Something went wrong! Maybe MG didn't run properly. Check Logs and Retry Later")
        return False

    return True



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--proc-card", dest="proc",
                      help="Proc Card",
                      default='None')
    parser.add_option("--run-list", dest="runs",
                      help="Give a JSON file with the list of run configs",
                      default='None')
    parser.add_option("","--do-MultiCore", dest="domulticore",
                      help="Set this flacg to run event generation with multicore",
                      action='store_true',
                      default=False)
    parser.add_option("--nbCore", dest="nbcore",
                      help="Number of cores",
                      type=int,
                      default=-1)
    (options, args) = parser.parse_args()

    proc_card = str(options.proc)
    run_list_file = str(options.runs)
    do_multicore = bool(options.domulticore)
    nb_core = int(options.nbcore)
    if proc_card == 'None':
        print("No Process Card Given! Exiting!")
        sys.exit(1)
    if not os.path.exists(proc_card):
        print("MG Process Card {} not found".format(proc_card))
        sys.exit(1)
    else:
        proc_card = os.path.abspath(proc_card)
    
    if not env_checker():
        print("Environment not setup! Please run the setup script!")
        sys.exit(1)
        
    edit_mg5_configuration(do_multicore, nb_core)

    out_path, status = proc_runner(proc_card)

    if not status:
        print("Process Runner Failed! Exiting!")
        sys.exit(1)

    params = get_param_list(out_path)
    
    if run_list_file == 'None':
        print("No Run list file given. Not Generating any events this time!")
        sys.exit(0)
    
    if not os.path.exists(run_list_file):
        print("Run list file not found. Please enter a correct file")
        sys.exit(1)
    else:
        run_list_file = os.path.abspath(run_list_file)
        
    run_list = json.load(open(run_list_file))
    edit_me5_configuration(out_path, do_multicore=do_multicore, nb_core=nb_core)
    for runname in run_list.keys():
        param_dict = run_list[runname]['params']
        reweight_dict = run_list[runname]['reweight']
        run_dict = run_list[runname]['run']
        edit_param_card(out_path, params, param_dict)
        edit_run_card(out_path, run_dict)
        make_reweight_card(out_path, params, reweight_dict)
        outdir = out_path + '/Events/' + runname
        outfile = out_path + '/Events/' + runname + "/{}*banner.txt".format(runname)
        run_command = out_path + "/bin/generate_events"
        if not processor(outdir, outfile, run_command, runname):
            sys.exit(1)
