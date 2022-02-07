from VLQCouplingCalculator import VLQCouplingCalculator as vlq


def param_editor(proc, m, GM, MG_loc):    
    vlqtype = proc[1]
    _c = vlq(mode = vlqtype, mvlq = m)
    if vlqtype in ['T', 'B']:
        _c.setGammaBRs(GM*m, 0.5, 0.25)
    else:
        _c.setGammaBRs(GM*m, 1.0, 0.0)
    
    kW, kZ, kH, _ = tuple(_c.getKappas())
    
    base_dir = "/VLQ_" + proc
    card_dir = MG_loc + base_dir + "/Cards/"
    card_name = card_dir + "param_card.dat"

    card_template = "../Share/param_card_mydefault_new.dat"

    f_def = open(card_template, "r")
    newcard = open(card_name, "w")

    for line in f_def:
        if ' # KTLh3' in line:
            newcard.write('    3 %.6f # KTLh3 \n' %(kH))
        elif ' # KBLh3' in line:
            newcard.write('    3 %.6f # KBLh3 \n' %(kH))
        elif ' # MTP' in line:
            newcard.write('   6000006 %i # MTP \n'%(m))
        elif ' # MBP' in line:
            newcard.write('   6000007 %i # MBP \n'%(m))
        elif ' # MX' in line:
            newcard.write('   6000005 %i # MX \n'%(m))
        elif ' # MY' in line:
            newcard.write('   6000008 %i # MY \n'%(m))
        elif ' # KTLw3' in line:
            newcard.write('    3 %.6f # KTLw3 \n' %(kW))
        elif ' # KBLw3' in line:
            newcard.write('    3 %.6f # KBLw3 \n' %(kW))
        elif ' # KXL3' in line:
            newcard.write('    3 %.6f # KXL3 \n' %(kW))
        elif ' # KYL3' in line:
            newcard.write('    3 %.6f # KYL3 \n' %(kW))
        elif ' # KTLz3' in line:
            newcard.write('    3 %.6f # KTLz3 \n' %(kZ))
        elif ' # KBLz3' in line:
            newcard.write('    3 %.6f # KBLz3 \n' %(kZ))
        elif ' # WTP' in line:
            newcard.write('DECAY 6000006 %.6f # WTP \n' %(GM*m))
        elif ' # WBP' in line:
            newcard.write('DECAY 6000007 %.6f # WBP \n' %(GM*m))
        elif ' # WX' in line:
            newcard.write('DECAY 6000005 %.6f # WX \n' %(GM*m))
        elif ' # WY' in line:
            newcard.write('DECAY 6000008 %.6f # WY \n' %(GM*m))
        else:
            newcard.write(line)
    f_def.close()
    newcard.close()
    return 1


def run_editor(proc, tag, MG_loc):
    base_dir = "/VLQ_" + proc
    card_dir = MG_loc + base_dir + "/Cards/"
    card_name = card_dir + "run_card.dat"

    card_template = "../Share/run_card_mydefault_new.dat"

    f_def = open(card_template, "r")
    newcard = open(card_name, "w")

    for line in f_def:
	if 'name of the run' in line:
            newcard.write('%s = run_tag ! name of the run \n' %(tag))
        else:
            newcard.write(line)

    return 1
        

def rewtcardmaker(proc, ms, GMs, MG_loc):
    tagnames = []
    vlqtype = proc[1]
    if vlqtype in ['X', 'Y']:
        paramlist = ['M' + vlqtype, 
                     'W' + vlqtype, 
                     'K' + vlqtype + 'L3']
    else:
        paramlist = ['M' + vlqtype + 'P', 
                     'W' + vlqtype + 'P', 
                     'K' + vlqtype + 'Lw3',
                     'K' + vlqtype + 'Lz3',
                     'K' + vlqtype + 'Lh3']

    launch_line = "launch --rwgt_name="
    base_dir = "/VLQ_" + proc
    card_dir = MG_loc + base_dir + "/Cards/"
    card_name = card_dir + "reweight_card.dat"
    f = open(card_name, "w")
    for m in ms:
        for GM in GMs:
            tagname = ('M' + str(int(m/100)) + 'G{0:03d}').format(int(GM*100))
            tagnames.append(tagname)
            _c = vlq(float(m), vlqtype)
            if vlqtype in ['X', 'Y']: 
                _c.setGammaBRs(GM*m, 1.0, 0.0)
            else: 
                _c.setGammaBRs(GM*m, 0.5, 0.25)
            kappas = _c.getKappas()
            Modified_Vars = [float(m), GM*m, kappas[0], kappas[1], kappas[2]]
            print(tagname, m, GM*m)
            f.write(launch_line + tagname + '\n')
            for ii in range(len(paramlist)):
                f.write('\tset ' + str(paramlist[ii]) + ' ' + str(Modified_Vars[ii]) + '\n')
            f.write('\n\n')
    f.flush()
    f.close()
    return tagnames
