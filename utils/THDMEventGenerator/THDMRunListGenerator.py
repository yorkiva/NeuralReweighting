import json
import sys
import numpy as np


#masses = list(np.arange(1100, 2400, 200))
# masses = list(np.arange(600., 2000., 200.))
masses = [800.]

run_dict = {}

for m in masses:
    # for g in gammas2sim:
    run_name = "THDM_MX{:04d}".format(int(m))
    run_dict[run_name] = {'params':{"MHH": m,
                                    "WHH": m,},
                          'run': {"bwcutoff": 10000,
                                  "nevents": 20000,
                                  "use_syst": "False",
                                  "systematics_program": "None"},
                                  # "fixed_ren_scale": "True",
                                  # "fixed_fac_scale": "True",
                                  # "scale":"{}".format(m/2),
                                  # "dsqrt_q2fact1":"{}".format(m/2),
                                  # "dsqrt_q2fact2":"{}".format(m/2)},
                          'reweight': {}}
    for rw_m in np.arange(m-200., m+210., 200.):
        rwt_key = "M{:04d}".format(int(rw_m))
        run_dict[run_name]['reweight'][rwt_key] = {'MHH': rw_m,
                                                   'WHH': 0.01}

fname = "THDM_RunList.json"

f = open(fname, "w")
json.dump(run_dict, f, indent = 3)
f.close()

