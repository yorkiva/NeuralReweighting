import json
import numpy as np
from VLQCouplingCalculator import VLQCouplingCalculator as vlq

keys = ['KBLh1', 'KBLh2', 'KBLh3', 'KBLw1', 'KBLw2', 'KBLw3', 'KBLz1', 'KBLz2', 'KBLz3', 'KBRh1', 'KBRh2', 'KBRh3', 'KBRw1', 'KBRw2', 'KBRw3', 'KBRz1', 'KBRz2', 'KBRz3', 'KTLh1', 'KTLh2', 'KTLh3', 'KTLw1', 'KTLw2', 'KTLw3', 'KTLz1', 'KTLz2', 'KTLz3', 'KTRh1', 'KTRh2', 'KTRh3', 'KTRw1', 'KTRw2', 'KTRw3', 'KTRz1', 'KTRz2', 'KTRz3', 'KXL1', 'KXL2', 'KXL3', 'KXR1', 'KXR2', 'KXR3', 'KYL1', 'KYL2', 'KYL3', 'KYR1', 'KYR2', 'KYR3', 'MX', 'MTP', 'MBP', 'MY', 'WX', 'WY', 'WTP', 'WBP']

masses = list(np.arange(1100, 2400, 200))
gammas2sim = [0.25, 0.5]
gammas2rwt = list(np.arange(0.05, 0.55, 0.05))

run_dict = {}

for m in masses:
    for g in gammas2sim:
        run_name = "VLT_M{:02d}G{:03d}".format(int(m/100.), int(g*100))
        run_dict[run_name] = {'params':{},
                              'run': {"bwcutoff": 10000,
                                      "nevents": 20000,
                                      "use_syst": "False",
                                      "systematics_program": "None"},
                              'reweight': {}}
        c = vlq(mvlq = m)
        c.setGammaBRs(m*g, 0.5, 0.25)
        kw, kz, kh, _ = c.getKappas()
        for key in keys:
            if key.upper() == 'KTLZ3':
                run_dict[run_name]['params'][key] = kz
            elif key.upper() == 'KTLW3':
                run_dict[run_name]['params'][key] = kw
            elif key.upper() == 'KTLH3':
                run_dict[run_name]['params'][key] = kh
            elif key.upper() == 'WTP':
                run_dict[run_name]['params'][key] = m*g
            elif key.upper() == 'MTP':
                run_dict[run_name]['params'][key] = m*1.0
            elif key.upper() in ['MBP', 'MX', 'MY']:
                run_dict[run_name]['params'][key] = 600.
            else:
                run_dict[run_name]['params'][key] = 0.
        for rw_m in np.arange(m-200., m+210., 100.):
            for rw_g in gammas2rwt:
                rwt_key = "M{:02d}G{:03d}".format(int(rw_m/100.), int(rw_g*100))
                # run_dict[run_name]['reweight'][rwt_key] = {}
                c_rwt = vlq(mvlq = rw_m)
                c_rwt.setGammaBRs(rw_m*rw_g, 0.5, 0.25)
                rw_kw, rw_kz, rw_kh, _ = c.getKappas()
                run_dict[run_name]['reweight'][rwt_key] = {'KTLw3' : rw_kw,
                                                           'KTLz3' : rw_kz,
                                                           'KTLh3' : rw_kh,
                                                           'MTP': rw_m,
                                                           'WTP': rw_m*rw_g}
        
f = open("VLQ_RunList.json", "w")
json.dump(run_dict, f, indent = 3)
f.close()

