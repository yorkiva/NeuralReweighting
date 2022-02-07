import matplotlib.pyplot as plt
import numpy as np
import sys, subprocess, os, json
from ReweighterNN import *
from DataSaverUtils import *
# modeW, modeZ, modeH, mass/2500., mT/2500., M_target/2500., G_target/2500., float(eventID), y

def plotter(hists, binning, test_only_keys, xlabel, plotloc):
    for hist_name in hists.keys():
        if len(hists[hist_name]) == 3:
            plt_max = float(max(hists[hist_name][1] + hists[hist_name][2]))
            plt.scatter(hists[hist_name][1],
                        hists[hist_name][2],
                        marker="x", 
                        color=("r" if hist_name.split('_')[2] in test_only_keys else "b"), 
                        )
            plt.xlabel("Actual Reweighting Factor (from  MG)")
            plt.ylabel("Reconstructed Reweighting Factor (from  NN)")
            plt.plot(np.array([0.,plt_max]), np.array([0.,plt_max]) )
            plt.savefig(plotloc + "/scatter_plots/{}/{}/scatter_{}.png".format(hist_name.split('_')[1],
                                                                               hist_name.split('_')[-1],
                                                                               hist_name.replace("hist_","")))
            plt.clf()

            plt.hist(x = hists[hist_name][0], 
                     bins = binning,
                     weights = hists[hist_name][2],
                     histtype = 'step',
                     density = True,
                     label = 'Prediction',
                 )
        plt.hist(x = hists[hist_name][0], 
                 bins = binning,
                 weights = hists[hist_name][1],
                 histtype = 'step',
                 density = True,
                 label = 'Original Calculation')
        
        plt.xlabel(xlabel)
        plt.ylabel('Normalized Events/Bin')
        plt.yscale('log')
        #plt.legend()
        plt.savefig(plotloc + "/comp_plots/{}/{}/MT_{}.png".format(hist_name.split('_')[1],
                                                                   hist_name.split('_')[-1], 
                                                                   hist_name))
        plt.clf()
        

def plot_maker(jsonfilename, modelname, nevents):
    if not os.path.exists(jsonfilename):
        print("{} does not exist".format(jsonfilename))
        sys.exit(1)
    proc, mass, train_test_keys, test_only_keys, default_weight = metadata(jsonfilename)
    subprocess.call("mkdir -p ../plots/comp_plots/{}/M{}".format(proc, int(mass/100)), shell=True)
    subprocess.call("mkdir -p ../plots/scatter_plots/{}/M{}".format(proc, int(mass/100)), shell=True)

    model = torch.load(modelname)
    model.eval()
    
    hists = {}
    for key in train_test_keys + test_only_keys:
        hist_name = "hist_{}_{}_from_M{}".format(proc, key, int(mass/100))
        hists[hist_name] = [[], [], []]


    if proc[2] == 'W': 
        mode = [1,0,0]
    elif proc[2] == 'Z': 
        mode = [0,1,0]
    elif proc[2] == 'H':
        mode = [0,0,1]
    f = open(jsonfilename, "r")
    data = json.load(f)
    eventcount = 0

    for eID in sorted(map(int,data.keys())):
        if eID%1000 == 0:
            print("{} Events Done!".format(eID))
        if eID == nevents:
            break
        eventID = str(eID)
        for infoID in data[eventID].keys():
            if infoID == 'wts':
                continue
            if abs(data[eventID][infoID]['pdgid']) == 6000006:
                mT = data[eventID][infoID]['m']
                break
        for wt in data[eventID]['wts'].keys():
            if wt == 'nominal':
                continue
            M_target = int(wt.split('G')[0].replace('M',''))*100.0
            G_target = int(wt.split('G')[1])*M_target/100.0
            hist_name = "hist_{}_{}_from_M{}".format(proc, wt, int(mass/100))
            hists[hist_name][0].append(mT)
            hists[hist_name][1].append( data[eventID]['wts'][wt]/data[eventID]['wts'][default_weight] )
            var = torch.tensor( mode + [mass/2500., mT/2500., M_target/2500., G_target/2500.]).reshape(1,-1)
            with torch.no_grad():
                y = float(model.forward(var).reshape(-1))
            hists[hist_name][2].append(y)
    binning = np.arange(0, 4000., 50.)
    plotter(hists, 
            binning, 
            test_only_keys,
            xlabel = "M(T) [GeV]", 
            plotloc = "../plots/" )


if __name__ == "__main__":
    List_of_files = [f for f in os.listdir("../data") if (".json" in f and f.split("_")[0] in ["WTWb", "WTZt", "WTHt"]) ]
    for f in List_of_files:
        print("File: " + f)
        plot_maker("../data/" + f, 
                   "../Models/TrainedVLQ_nLayers_5_nNodes_1024.model", 
                   nevents = 25000)
