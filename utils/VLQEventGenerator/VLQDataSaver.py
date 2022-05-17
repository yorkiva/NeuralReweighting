import json, os, sys, subprocess
import numpy as np
import lxml.etree as ET
import pandas as pd
import re

def lhe_to_array(lhefilename, mode, msim, gsim):
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
    events = []
    eventindex = 0
    tree = ET.iterparse(lhefilename, events = ("end",), tag = "event")
    tree = iter(tree)
    for event, elem in tree:
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
            events.append([mode, msim, gsim, weight] + [0]*(len(cols)-4))
            pout1 = False
            pout2 = False
            pout3 = False
            pout4 = False
            for pidx in this_event.keys():
                this_particle = this_event[pidx]
                if this_particle['status'] not in [-1, 1]:
                    continue
                if this_particle['status'] == -1 and this_particle['pz'] > 0.:
                    events[eventindex][cols.index('pz_in1')] = this_particle['pz']
                    events[eventindex][cols.index('pid_in1')] = this_particle['pdgid']
                elif this_particle['status'] == -1 and this_particle['pz'] < 0.:
                    events[eventindex][cols.index('pz_in2')] = this_particle['pz']
                    events[eventindex][cols.index('pid_in2')] = this_particle['pdgid']
                elif this_particle['status'] == 1 and (not pout1 and not pout2 and not pout3 and not pout4):
                    events[eventindex][cols.index('pz_out1')] = this_particle['pz']
                    events[eventindex][cols.index('pid_out1')] = this_particle['pdgid']
                    events[eventindex][cols.index('px_out1')] = this_particle['px']
                    events[eventindex][cols.index('py_out1')] = this_particle['py']
                    events[eventindex][cols.index('e_out1')] = this_particle['e']
                    pout1 = True
                elif this_particle['status'] == 1 and (pout1 and not pout2 and not pout3 and not pout4):
                    events[eventindex][cols.index('pz_out2')] = this_particle['pz']
                    events[eventindex][cols.index('pid_out2')] = this_particle['pdgid']
                    events[eventindex][cols.index('px_out2')] = this_particle['px']
                    events[eventindex][cols.index('py_out2')] = this_particle['py']
                    events[eventindex][cols.index('e_out2')] = this_particle['e']
                    pout2 = True
                elif this_particle['status'] == 1 and (pout1 and pout2 and not pout3 and not pout4):
                    events[eventindex][cols.index('pz_out3')] = this_particle['pz']
                    events[eventindex][cols.index('pid_out3')] = this_particle['pdgid']
                    events[eventindex][cols.index('px_out3')] = this_particle['px']
                    events[eventindex][cols.index('py_out3')] = this_particle['py']
                    events[eventindex][cols.index('e_out3')] = this_particle['e']
                    pout3 = True
                elif this_particle['status'] == 1 and (pout1 and pout2 and pout3 and not pout4):
                    events[eventindex][cols.index('pz_out4')] = this_particle['pz']
                    events[eventindex][cols.index('pid_out4')] = this_particle['pdgid']
                    events[eventindex][cols.index('px_out4')] = this_particle['px']
                    events[eventindex][cols.index('py_out4')] = this_particle['py']
                    events[eventindex][cols.index('e_out4')] = this_particle['e']
                events[eventindex][cols.index('Mtarget')] = wt[0]
                events[eventindex][cols.index('Gtarget')] = wt[1]
                events[eventindex][cols.index('f_rwt')] = wt[2]
            eventindex += 1
        elem.clear()
        if eventindex >= 250000:
            break
    return cols, events


def lhe_to_csv(lhefiles, target_file_name):
    msim = 1500.
    gsim = 750.
    mode = 1
    for idx, lhefile in enumerate(lhefiles):
        if lhefile.endswith(".gz"):
            subprocess.call("gunzip {}".format(lhefile), shell=True)
        cols, events = lhe_to_array(lhefile, mode, msim, gsim)
        print("File {} done with {} entries".format(lhefile, len(events)))
        df = pd.DataFrame(events, columns=cols)
        if idx == 0:
            df.to_csv(target_file_name, mode='w', index=False, header=True)
        else:
            df.to_csv(target_file_name, mode='a', index=False, header=False)
        del cols, events, df



def jsonsaver(lhefilename, outfilename):
    if os.path.exists(outfilename):
        f = open(outfilename)
        x = json.load(f)
        if len(x["0"]["wts"]) == 76:
            print(outfilename + " file exists")
            return
        del x
    events = lhe_to_dict(lhefilename)
    print(len(events.keys()))
    fp = open(outfilename, 'w')
    json.dump(events, fp, indent=2)
    print(outfilename + " Done!")
    fp.close()

def metadata(jsonfilename):
    run_data = jsonfilename.split('/')[-1].strip().replace(".json","").split("_")
    proc = run_data[0]
    mass = int(run_data[-1])
    if not mass % 100 == 0:
        mass = mass*100
    default_weight = 'M' + str(int(mass/100)) + 'G100'
    reweight_keys = ['M' + str(int(m/100)) + 'G{0:03d}'.format(int(gm*100)) \
                     for m in range(mass-200, mass+201, 100) \
                     for gm in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.90, 0.95, 1.0] ]
    test_only_keys = ['M' + str(int(m/100)) + 'G{0:03d}'.format(int(gm*100)) \
                     for m in range(mass-100, mass+101, 200) \
                     for gm in [0.1, 0.2, 0.3, 0.5, 0.70, 0.85, 0.95] ]
    train_test_keys = [key for key in reweight_keys if key not in test_only_keys]
    return proc, mass, train_test_keys, test_only_keys, default_weight


def arraymaker(jsonfilename, nevents, X_train_test, X_test_only, firstevent = 0, n_test_only_entries = 0, n_train_test_entries = 0):
    proc, mass, train_test_keys, test_only_keys, default_weight = metadata(jsonfilename)
    #X_train_test = np.zeros((nevents*len(train_test_keys), 7), dtype = np.float32)
    #X_test_only =  np.zeros((nevents*len(test_only_keys),  7), dtype = np.float32)
    if proc[2] == 'W': 
        mode = [1,0,0]
    elif proc[2] == 'Z': 
        mode = [0,1,0]
    elif proc[2] == 'H':
        mode = [0,0,1]
    f = open(jsonfilename, "r")
    data = json.load(f)
    eventcount = 0
    rowcount_test_only = n_test_only_entries
    rowcount_train_test = n_train_test_entries
    for eID in sorted(map(int,data.keys())):
        if eID < firstevent:
            continue
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
            y = data[eventID]['wts'][wt]/data[eventID]['wts'][default_weight]
            if wt in test_only_keys:
                X_test_only[rowcount_test_only] = np.array( mode +  [mass/2500., mT/2500., M_target/2500., G_target/2500., float(eventID), y], dtype = np.float32)
                rowcount_test_only += 1
            elif wt in train_test_keys:
                X_train_test[rowcount_train_test] = np.array(mode + [mass/2500., mT/2500., M_target/2500., G_target/2500., float(eventID), y], dtype = np.float32)
                rowcount_train_test += 1
            else:
                print(wt + " not found!")
                continue
        eventcount += 1
        if eventcount == nevents:
            break
    del f
    del data
    return rowcount_train_test, rowcount_test_only
