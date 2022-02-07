import json, os, sys, subprocess
import numpy as np
import lxml.etree as ET

def lhe_to_dict(lhefilename='unweighted_events.lhe'):
    events = {}
    eventindex = 0
    tree = ET.iterparse(lhefilename, events = ("end",), tag = "event")
    tree = iter(tree)
    for event, elem in tree:
        events[eventindex] = {}
        this_event = events[eventindex]
        eventinfo = elem.text.strip().split('\n')
        particleindex = 0
        for ii in range(len(eventinfo)):
            if ii==0: 
                continue
            this_event[particleindex] = {}
            this_particle = this_event[particleindex]
            particleinfo = eventinfo[ii].strip().split()
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
        this_event['wts'] = {'nominal': 1.0 }
        try: 
            rwt = elem.find('rwgt')
            for wt in rwt.findall('wgt'):
                wtname = wt.get('id')
                wtval = float( wt.text.strip() )
                this_event['wts'][wtname] = wtval
        except:
            pass
        eventindex += 1
        elem.clear()
    return events


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
