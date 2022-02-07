import json
import numpy as np
from DataSaverUtils import * 
import sys, os, subprocess
from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("", "--base-dir", dest="basedir",
                      help="base directory of the project",
                      default="/code/avik/ReweightProject/")
    parser.add_option("","--MGversion", dest="mgversion",
                      help="MadGraph Version",
                      default="2.6.5")
    parser.add_option("","--proc", dest="proc",
                      help="Process",
                      default="WTWb")
    parser.add_option("","--lhe-to-json", dest="lhe2json",
                      help="Selecet to convert lhe files to json",
                      action="store_true",
                      default=False)
    parser.add_option("","--json-to-npy", dest="json2npy",
                      help="Selecet to convert json file to npy",
                      action="store_true",
                      default=False)
    parser.add_option("", "--nevents", dest="nevents",
                      help="number of events from each lhefile",
                      default=25000)
    parser.add_option("","--append", dest="append",
                      help="If converting json to npy, select this to append to the existing arrays",
                      action="store_true",
                      default=False)
    (options, args) = parser.parse_args()
    proc = str(options.proc)
    if proc == 'all':
        proc = ''
    base_dir = str(options.basedir)
    MG_dir = base_dir + "/MG5_aMC_v" + str(options.mgversion).replace(".","_") + "/"
    data_dir = base_dir + "/data/"
    lhe2json = bool(options.lhe2json)
    json2npy = bool(options.json2npy)
    nevents = int(options.nevents)
    append = bool(options.append)
    train_test_path = (data_dir + "/VLQ_" + proc + "_X_train_test.npy").replace("__", "_")
    test_only_path  = (data_dir + "/VLQ_" + proc + "_X_test_only.npy").replace("__","_")

    if lhe2json:
        event_dir = MG_dir + "/VLQ_" + proc + "/Events/"
        run_list = os.listdir(event_dir)
        for run in run_list:
            if "unweighted_events.lhe" not in os.listdir(event_dir + run):
                subprocess.call("cd " + event_dir + run + " && gunzip unweighted_events.lhe.gz && cd -", shell=True)
            lhefilename = event_dir + run + "/unweighted_events.lhe"
            outfilename = base_dir + "data/" + run.replace("RUN_","") + ".json"
            print (run,lhefilename, outfilename)
            jsonsaver(lhefilename, outfilename)

    if json2npy:
        jsonfilenames = [data_dir + f for f in os.listdir(data_dir) if (".json" in f and (f.split('_')[0] == proc if proc != '' else f.split('/')[-1] != 'events.json')) ]
        nfiles = len(jsonfilenames)
        _, _, train_test_keys, test_only_keys, _ = metadata(jsonfilenames[0])
        n_train_test_keys, n_test_only_keys = len(train_test_keys), len(test_only_keys)

        if append and os.path.exists(train_test_path) and os.path.exists(test_only_path):
            x_train_test = np.load(train_test_path)
            first_event = int(x_train_test[-1, 7]) + 1
            n_train_test_entries = x_train_test.shape[0]
            print("Existing entry count (T&T) = ", n_train_test_entries)
            X_train_test = np.zeros((n_train_test_entries + nevents*n_train_test_keys*nfiles, 9), dtype = np.float32)
            print("Total entry count (T&T) = ", X_train_test.shape[0])
            X_train_test[:n_train_test_entries] = x_train_test
            del x_train_test

            x_test_only  = np.load(test_only_path)
            n_test_only_entries = x_test_only.shape[0]
            print("Existing entry count (TO) = ", n_test_only_entries)
            X_test_only = np.zeros((n_test_only_entries + nevents*n_test_only_keys*nfiles, 9), dtype = np.float32)
            print("Total entry count (TO) = ", X_test_only.shape[0])
            X_test_only[:n_test_only_entries] = x_test_only
            del x_test_only
            print("First new Event = ", first_event)

        else:
            X_train_test = np.zeros((nevents*n_train_test_keys*nfiles,9), dtype = np.float32)
            X_test_only  = np.zeros((nevents*n_test_only_keys*nfiles, 9), dtype = np.float32)
            print("Total entry count (T&T) = ", X_train_test.shape[0])
            print("Total entry count (TO) = ", X_test_only.shape[0])
            n_train_test_entries = 0
            n_test_only_entries = 0
            first_event = 0

        for jsonfilename in jsonfilenames:
            print(jsonfilename)
            #x_train_test, x_test_only = arraymaker(jsonfilename, nevents = nevents, firstevent = first_event)
            n_train_test_entries, n_test_only_entries = arraymaker(jsonfilename, nevents = nevents, firstevent = first_event, 
                                                                   X_test_only = X_test_only, X_train_test = X_train_test,
                                                                   n_train_test_entries = n_train_test_entries,
                                                                   n_test_only_entries = n_test_only_entries)
            #X_train_test = np.append(X_train_test, x_train_test, 0)
            #X_test_only = np.append(X_test_only, x_test_only, 0)
            #del x_train_test
            #del x_test_only
            print("Test Only = ",  n_test_only_entries)
            print("Train Test = ", n_train_test_entries)

        np.save(train_test_path, X_train_test)
        np.save(test_only_path,  X_test_only)
