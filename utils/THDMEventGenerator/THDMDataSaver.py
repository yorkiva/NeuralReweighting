import json, os, sys, subprocess
import numpy as np
import lxml.etree as ET
import pandas as pd
import re

def lhe_to_array(lhefilename, mode, msim, gsim, start=0, end=500):
    cols = ['mode',
            'Msim',
            'Gsim',
            'weight',
            'pz_in1',
            'pid_in1',
            'pz_in2',
            'pid_in2',
            'px_out1',
            'py_out1',
            'pz_out1',
            'e_out1',
            'pid_out1',
            'px_out2',
            'py_out2',
            'pz_out2',
            'e_out2',
            'pid_out2',
            'px_out3',
            'py_out3',
            'pz_out3',
            'e_out3',
            'pid_out3',
            'px_out4',
            'py_out4',
            'pz_out4',
            'e_out4',
            'pid_out4',
            'Mtarget',
            'Gtarget',
            'f_rwt']
    entries = []
    entryindex = 0
    eventindex = 0
    tree = ET.iterparse(lhefilename, events = ("end",), tag = "event")
    tree = iter(tree)
    for event, elem in tree:
        if not (eventindex >= start and eventindex < end):
            eventindex += 1
            continue
        eventindex +=1
        this_event = {}
        eventinfo = elem.text.strip().split('\n')
        particleindex = 0
        for ii in range(len(eventinfo)):
            if ii==0: 
                weight = float(eventinfo[ii].strip().split()[2])
                continue
            this_event[particleindex] = {}
            this_particle = this_event[particleindex]
            particleinfo = eventinfo[ii].strip().split()
            # print(particleinfo)
            for jj in range(len(particleinfo)):
                this_info = particleinfo[jj]
                if jj == 0:    
                    this_particle['pdgid'] = int(this_info)
                elif jj == 1:  
                    this_particle['status'] = int(this_info)
                elif jj == 6:  
                    this_particle['px'] = float(this_info) 
                elif jj == 7:  
                    this_particle['py'] = float(this_info)
                elif jj == 8:  
                    this_particle['pz'] = float(this_info)
                elif jj == 9:  
                    this_particle['e'] = float(this_info)
                elif jj == 10: 
                    this_particle['m'] = float(this_info)
                else: 
                    continue
            particleindex += 1
        this_event_wts = []
        try: 
            rwt = elem.find('rwgt')
            for wt in rwt.findall('wgt'):
                wtname = wt.get('id')
                wt_m, wt_g = re.findall(r'\d+', wtname)
                wt_m = int(wt_m)*100.0
                wt_g = int(wt_g)*wt_m/100.
                wtval = float( wt.text.strip() )
                this_event_wts.append([wt_m, wt_g, wtval])
        except:
            pass

        for wt in this_event_wts:
            entries.append([mode, msim, gsim, weight] + [0]*(len(cols)-4))
            pout1 = False
            pout2 = False
            pout3 = False
            pout4 = False
            for pidx in this_event.keys():
                this_particle = this_event[pidx]
                if this_particle['status'] not in [-1, 1]:
                    continue
                if this_particle['status'] == -1 and this_particle['pz'] > 0.:
                    entries[entryindex][cols.index('pz_in1')] = this_particle['pz']
                    entries[entryindex][cols.index('pid_in1')] = this_particle['pdgid']
                elif this_particle['status'] == -1 and this_particle['pz'] < 0.:
                    entries[entryindex][cols.index('pz_in2')] = this_particle['pz']
                    entries[entryindex][cols.index('pid_in2')] = this_particle['pdgid']
                elif this_particle['status'] == 1 and (not pout1 and not pout2 and not pout3 and not pout4):
                    entries[entryindex][cols.index('pz_out1')] = this_particle['pz']
                    entries[entryindex][cols.index('pid_out1')] = this_particle['pdgid']
                    entries[entryindex][cols.index('px_out1')] = this_particle['px']
                    entries[entryindex][cols.index('py_out1')] = this_particle['py']
                    entries[entryindex][cols.index('e_out1')] = this_particle['e']
                    pout1 = True
                elif this_particle['status'] == 1 and (pout1 and not pout2 and not pout3 and not pout4):
                    entries[entryindex][cols.index('pz_out2')] = this_particle['pz']
                    entries[entryindex][cols.index('pid_out2')] = this_particle['pdgid']
                    entries[entryindex][cols.index('px_out2')] = this_particle['px']
                    entries[entryindex][cols.index('py_out2')] = this_particle['py']
                    entries[entryindex][cols.index('e_out2')] = this_particle['e']
                    pout2 = True
                elif this_particle['status'] == 1 and (pout1 and pout2 and not pout3 and not pout4):
                    entries[entryindex][cols.index('pz_out3')] = this_particle['pz']
                    entries[entryindex][cols.index('pid_out3')] = this_particle['pdgid']
                    entries[entryindex][cols.index('px_out3')] = this_particle['px']
                    entries[entryindex][cols.index('py_out3')] = this_particle['py']
                    entries[entryindex][cols.index('e_out3')] = this_particle['e']
                    pout3 = True
                elif this_particle['status'] == 1 and (pout1 and pout2 and pout3 and not pout4):
                    entries[entryindex][cols.index('pz_out4')] = this_particle['pz']
                    entries[entryindex][cols.index('pid_out4')] = this_particle['pdgid']
                    entries[entryindex][cols.index('px_out4')] = this_particle['px']
                    entries[entryindex][cols.index('py_out4')] = this_particle['py']
                    entries[entryindex][cols.index('e_out4')] = this_particle['e']
                entries[entryindex][cols.index('Mtarget')] = wt[0]
                entries[entryindex][cols.index('Gtarget')] = wt[1]
                entries[entryindex][cols.index('f_rwt')] = wt[2]
            entryindex += 1
        elem.clear()
    return cols, entries


def lhe_to_csv(lhefiles, target_file_name, start=0, end=500):
    
    # msim = 1500.
    # gsim = 750.
    # mode = 1
    for idx, lhefile in enumerate(lhefiles):
        if 'WTWb' in lhefile:
            mode = -1
        if 'WTZt' in lhefile:
            mode = 1
        if 'WTHt' in lhefile:
            mode = 0
        run_name = lhefile.split('/')[-2]
        msim, gsim = re.findall(r'\d+', run_name)
        msim = int(msim)*100.0
        gsim = int(gsim)*msim/100.
        rezip = True
        if lhefile.endswith(".gz"):
            subprocess.call("gunzip {}".format(lhefile), shell=True)
            # rezip = True
        cols, events = lhe_to_array(lhefile.replace(".gz", ""), mode, msim, gsim, start, end)
        if rezip:
            subprocess.call("gzip {}".format(lhefile.replace(".gz", "")), shell=True)
        print("File {} done with start = {} and end = {}".format(lhefile, start, end))
        if idx == 0:
            df = pd.DataFrame(events, columns=cols)
            # df.to_csv(target_file_name, mode='w', index=False, header=True)
        else:
            df = df.append(pd.DataFrame(events, columns=cols), ignore_index = True)
            # df.to_csv(target_file_name, mode='a', index=False, header=False)
        # print(df.shape[0])
    df = df.sample(frac = 1).reset_index(drop=True)
    df.to_hdf(target_file_name.replace(".csv", ".h5"), key="VLQ_Reweighting_data", mode="w")
    df.to_csv(target_file_name.replace(".h5", ".csv"), mode="w", index=False, header=True)



if __name__ == "__main__":
    lhefile_locs = ['{}/{}/Events/'.format(os.environ['NEURWT_MGLOC'], _loc)  for _loc in ['VLQ_WTWb', 'VLQ_WTZt', 'VLQ_WTHt']  ]
    lhefiles = []
    train_lhefiles = []
    test_lhefiles = []
    for _loc in lhefile_locs:
        all_runs = os.listdir(_loc)
        for run in all_runs:
            event_file = [(_loc + '/' + run + '/' + f) for f in os.listdir(_loc + '/' + run) if 'unweighted_events' in f][0]
            lhefiles.append(event_file)
    for _fname in lhefiles:
        if 'M19' in _fname:
            test_lhefiles.append(_fname)
        else:
            train_lhefiles.append(_fname)
    nevents_per_lhe = 5000
    nevents_to_take = 500
    nfiles = int(nevents_per_lhe/nevents_to_take)
    # print(len(train_lhefiles))
    for ii in range(nfiles):
        lhe_to_csv(train_lhefiles, 
                   target_file_name = '{}/data/VLQData/train_{}.csv'.format(os.environ['NEURWT_BASE_PATH'], ii), 
                   start=ii*nevents_to_take, 
                   end=(ii+1)*nevents_to_take)
    for ii in range(nfiles):
        lhe_to_csv(test_lhefiles, 
                   target_file_name = '{}/data/VLQData/test_{}.csv'.format(os.environ['NEURWT_BASE_PATH'], ii), 
                   start=ii*nevents_to_take, 
                   end=(ii+1)*nevents_to_take)
    
