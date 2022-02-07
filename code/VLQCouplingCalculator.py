## Class to convert VLQ couplings from one convention to another
## Also useful to calculate decay width, BRs etc
## Author: Avik Roy, UT Austin


import sys, math
    
## Global variables

gWeak =  0.65 #unitless
MW = 80.39 #GEV
MZ = 91.19 #GEV
MH = 125.09 #GEV
Mt = 172.5
Mb = 4.19
v = 2*MW/gWeak

def rhoW(M, mode):
    mV = 80.39
    if mode in ['T', 'Y']: mq = 4.19
    elif mode == '0' or mode == 0: mq = 0.0
    else: mq = 172.5
    return (1+ math.pow(mV/M,2)-2*math.pow(mq/M,2) -2*math.pow(mV/M,4) + math.pow(mq/M,4) + math.pow(mV*mq/(M*M),2))*math.sqrt(1+math.pow(mV/M,4)+math.pow(mq/M,4)-2*math.pow(mV/M,2)-2*math.pow(mq/M,2)-2*math.pow(mV*mq/(M*M),2))

def rhoZ(M, mode):
    mV = 91.19
    if mode == 'T': mq = 172.5
    elif mode == 'B': mq = 4.19
    elif mode == '0' or mode ==0: mq =0.0
    else:
        print ('WARNING! Decay to Z is not allowed for modes X and Y. Returning 1.0 as default')
        return 1.0
    return (1+ math.pow(mV/M,2)-2*math.pow(mq/M,2) -2*math.pow(mV/M,4) + math.pow(mq/M,4) + math.pow(mV*mq/(M*M),2))*math.sqrt(1+math.pow(mV/M,4)+math.pow(mq/M,4)-2*math.pow(mV/M,2)-2*math.pow(mq/M,2)-2*math.pow(mV*mq/(M*M),2))

def rhoH(M, mode):
    mV = 125.09
    if mode == 'T': mq = 172.5
    elif mode == 'B': mq = 4.19
    elif mode == '0' or mode ==0: mq =0.0
    else:
        print ('WARNING! Decay to H is not allowed for modes X and Y. Returning 1.0 as default')
        return 1.0
    return (1 - math.pow(mV/M,2) + math.pow(mq/M,2))*math.sqrt(1+math.pow(mV/M,4)+math.pow(mq/M,4)-2*math.pow(mV/M,2)-2*math.pow(mq/M,2)-2*math.pow(mV*mq/(M*M),2))

def rhoS(MS, M, mode):
    mV = MS
    if mode == 'T': mq = 172.5
    elif mode == 'B': mq = 4.19
    elif mode == '0' or mode ==0: mq =0.0
    else:
        print ('WARNING! Decay to S is not allowed for modes X and Y. Returning 1.0 as default')
        return 1.0
    return (1 - math.pow(mV/M,2) + math.pow(mq/M,2))*math.sqrt(1+math.pow(mV/M,4)+math.pow(mq/M,4)-2*math.pow(mV/M,2)-math.pow(mq/M,2)-2*math.pow(mV*mq/(M*M),2))

 
class VLQCouplingCalculator:
    def __init__(self, mvlq=1000., mode = 'T'):
        #if len(vals) < 3:
        #    print "Not all numbers are given! Aborting!"
        #    sys.exit()
        #if kappaBR:
        #    self.setKappaBR(vals[0], vals[1], vals[2], MVLQ, exotics, exoticBR, exoticM)
        #elif cVals:
        #    self.setcVals(vals[0], vals[1], vals[2], MVLQ, exotics, exoticc, exoticM)
        self.VLQMode = mode
        self.MVLQ = mvlq
        self.Kappa = 0.
        self.xiW = 0.
        self.xiZ = 0.
        self.xiH = 0.
        self.xiS = 0.
        self.exotics = False
        self.MEXOT = 0.
        self.BRW = 0.
        self.BRZ = 0.
        self.BRH = 0.
        self.BRS = 0.
        self.cW = 0.
        self.cZ = 0.
        self.cH = 0.
        self.cHleading = 0.
        self.cHsubleading = 0.
        self.cS = 0.
        self.cW_ = 0.
        self.cZ_ = 0.
        self.cH_ = 0.
        self.cH_leading = 0.
        self.cH_subleading = 0.
        self.cS_ = 0.
        self.KappaW = 0.
        self.KappaZ = 0.
        self.KappaH = 0.
        self.KappaHleading = 0.
        self.KappaHsubleading = 0.
        self.KappaS = 0.
        self.Gamma = 0.
        self.GammaW = 0.
        self.GammaZ = 0.
        self.GammaH = 0.
        self.GammaS = 0.

    def setExotics(self, mexot):
        self.exotics = True
        self.MEXOT = mexot
        
    def setMVLQ(self, M):
        self.MVLQ = M

    def getMVLQ(self):
        return self.MVLQ

    def setVLQMode(self, mode):
        if mode not in ['T', 'B', 'X', 'Y']:
            print ('VLQ Mode is unrecognized. Selecting T by default')
            self.VLQMode = 'T'
        else:
            self.VLQMode = mode

    def getVLQMode(self):
        return self.VLQMode
    
    def setcVals(self, cw, cz, ch, exoticc=0.):
        self.cW = cw
        self.cZ = cz
        self.cH = ch
        if self.VLQMode == 'T':
            self.cHsubleading = self.cH /math.sqrt(1 + math.pow(self.MVLQ/Mt,2))
            self.cHleading = self.cHsubleading*self.MVLQ/Mt
        else:
            self.cHleading = self.cH
            self.cHsubleading = 0.
        if self.exotics: self.cS = exoticc
        else: self.cS = 0.

        # Evaluating tilde Couplings
        
        self.cW_ = self.cW
        self.cZ_ = (MW/MZ)*self.cZ
        self.cH_ = self.cH*(2*MW/(gWeak*self.MVLQ))
        self.cH_leading = self.cHleading*(2*MW/(gWeak*self.MVLQ))
        self.cH_subleading = self.cHsubleading*(2*MW/(gWeak*self.MVLQ))
        self.cS_ = self.cS*(2*MW/(gWeak*self.MVLQ))
        
        # Evaluating Gamma and BRs
        
        self.CalcBRs()

        # Evaluating Kappa

        self.Kappa = math.sqrt((self.cW_**2*rhoW(self.MVLQ, 0) + self.cZ_**2*rhoZ(self.MVLQ, 0) + self.cH_leading**2*rhoH(self.MVLQ, 0) + self.cS_**2*rhoS(self.MEXOT, self.MVLQ, 0))/2.0)

        # Evaluating Xis

        self.xiW = (self.cW_ / self.Kappa)**2*rhoW(self.MVLQ, 0)/2.
        self.xiZ = (self.cZ_ / self.Kappa)**2*rhoZ(self.MVLQ, 0)/2.
        self.xiH = (self.cH_leading / self.Kappa)**2*rhoH(self.MVLQ, 0)/2.
        if self.exotics:
            self.xiS = (self.cS_ / self.Kappa)**2*rhoS(self.MEXOT, self.MVLQ, 0)/2.
        else:
            self.xiS = 0.
        valsum = self.xiW + self.xiZ + self.xiH + self.xiS
        if not (valsum == 1.0):
            self.xiW = self.xiW/valsum
            self.xiZ = self.xiZ/valsum
            self.xiH = self.xiH/valsum
            self.xiS = self.xiS/valsum

        self.KappaW = self.Kappa*math.sqrt(self.xiW/rhoW(self.MVLQ,0))#self.VLQMode))
        self.KappaZ = self.Kappa*math.sqrt(2*self.xiZ/rhoZ(self.MVLQ,0))#self.VLQMode))
        self.KappaHleading = self.Kappa*(self.MVLQ/v)*math.sqrt(2*self.xiH/rhoH(self.MVLQ,0))#self.VLQMode))
        if self.VLQMode == 'T': self.KappaHsubleading = self.Kappa*(Mt/v)*math.sqrt(2*self.xiH/rhoH(self.MVLQ,0))#self.VLQMode))
        else: self.KappaHsubleading = 0.
        self.KappaH = math.sqrt(self.KappaHleading ** 2 + self.KappaHsubleading ** 2)
        self.KappaS = self.Kappa*(self.MVLQ/v)*math.sqrt(2*self.xiS/rhoS(self.MEXOT,self.MVLQ,0))#self.VLQMode))

    def setc_Vals(self, cw_, cz_, ch_, cs_=0.):
        self.cW_ = cw_
        self.cZ_ = cz_
        self.cH_ = ch_
        if self.exotics: self.cS_ = cs_
        else: self.cS_ = 0.

        cW = self.cW_
        cZ = (MZ/MW)*self.cZ_
        cH = self.cH_/(2*MW/(gWeak*self.MVLQ))
        cS = self.cS_/(2*MW/(gWeak*self.MVLQ))

        self.setcVals(cW, cZ, cH, cS)
        
    def setKappaxi(self, k, xiw, xiz, exoticxi=0.):
        self.Kappa = k
        self.xiW = xiw
        if self.exotics: self.xiS = exoticxi
        else: self.xiS = 0.
        if self.VLQMode == 'T' or self.VLQMode == 'B': 
            self.xiZ = xiz
            self.xiH = 1. - self.xiW - self.xiZ - self.xiS
        else: 
            self.xiZ = 0.
            self.xiH = 0.

        if self.xiH < 0:
            print (" xiW + xiZ =", self.xiW + self.xiZ, "> 1.0, setting xiH = 0 ")
            self.xiH = 0

        valsum = self.xiW + self.xiZ + self.xiH + self.xiS
        if not (valsum == 1.0):
            print ("xi values (Branching ratios) not normalized. Valsum = ", valsum, ". Renormalizing BR(W+Z+H) to 1.0")
            self.xiW = self.xiW/valsum
            self.xiZ = self.xiZ/valsum
            self.xiH = self.xiH/valsum
            self.xiS = self.xiS/valsum
    
        self.cW = self.Kappa*math.sqrt(2*self.xiW/rhoW(self.MVLQ, 0))#self.VLQMode))
        self.cZ = (MZ/MW)*self.Kappa*math.sqrt(2*self.xiZ/rhoZ(self.MVLQ, 0))#self.VLQMode))
        self.cHleading = 0.5*(gWeak*self.MVLQ/MW)*self.Kappa*math.sqrt(2*self.xiH/rhoH(self.MVLQ, 0))#self.VLQMode))
        if self.VLQMode == 'T': self.cHsubleading = 0.5*(gWeak*Mt/MW)*self.Kappa*math.sqrt(2*self.xiH/rhoH(self.MVLQ, 0))#self.VLQMode))
        else: self.cHsubleading = 0.
        self.cH = math.sqrt(self.cHleading**2 + self.cHsubleading**2)
        self.cS = 0.5*(gWeak*self.MVLQ/MW)*self.Kappa*math.sqrt(2*self.xiS/rhoS(self.MEXOT, self.MVLQ, self.VLQMode)) 

        self.setcVals(self.cW, self.cZ, self.cH, self.cS)
        # Evaluating tilde Couplings

        #self.cW_ = self.cW
        #self.cZ_ = (MW/MZ)*self.cZ
        #self.cH_ = self.cH*(2*MW/(gWeak*self.MVLQ))
        #self.cH_leading = self.cHleading*(2*MW/(gWeak*self.MVLQ))
        #self.cH_subleading = self.cHsubleading*(2*MW/(gWeak*self.MVLQ))
        #self.cS_ = self.cS*(2*MW/(gWeak*self.MVLQ))

        # Evaluating Decay Widths and BRs

        #self.CalcBRs()

    def setKappas(self, kw, kz, kh, ks=0.):
        #print '''your input for kh is taken as the leading coupling.
        #However, the corresponding Kappa-xi parameterization will get a small subleading coupling. So decay width calculations may slightly vary
        #'''
        self.KappaW = kw
        self.KappaZ = kz
        self.KappaHleading = kh
        if self.VLQMode == 'T': self.KappaHsubleading = kh*Mt/math.sqrt(self.MVLQ**2 + Mt**2)
        else: self.KappaHsubleading = 0.
        self.KappaH = math.sqrt(self.KappaHleading ** 2 + self.KappaHsubleading ** 2)
        self.KappaS = ks
        
        #LL = self.VLQMode
        #self.VLQMode = 0
        self.Kappa = math.sqrt(kw**2*rhoW(self.MVLQ, 0) + kz**2*0.5*rhoZ(self.MVLQ, 0) + kh**2*(v**2/self.MVLQ**2)*0.5*rhoH(self.MVLQ, 0) +  ks**2*(v**2/self.MVLQ**2)*0.5*rhoS(self.MEXOT, self.MVLQ, 0))
        self.xiW = (self.KappaW/self.Kappa)**2 * rhoW(self.MVLQ, 0)
        self.xiZ = (self.KappaZ/self.Kappa)**2 * rhoZ(self.MVLQ, 0) / 2.0
        self.xiH = (self.KappaHleading*v/(self.Kappa*self.MVLQ))**2 * rhoH(self.MVLQ, 0) / 2.0
        self.xiS = (self.KappaS*v/(self.Kappa*self.MVLQ))**2 * rhoS(self.MEXOT, self.MVLQ, 0) / 2.0
        #self.VLQMode = LL
        self.setKappaxi(self.Kappa, self.xiW, self.xiZ, self.xiS)

    def setGammaBRs(self, gamma, brw, brz, brs=0.):
        self.Gamma = gamma
        self.BRW = brw
        if self.exotics: self.BRS = brs
        else: self.BRS = 0

        if self.VLQMode == 'T' or self.VLQMode == 'B': 
            self.BRZ = brz
            self.BRH = 1. - self.BRW - self.BRZ - self.BRS
        else: 
            self.BRZ = 0.
            self.BRH = 0.

        if self.BRH < 0:
            print (" BR(W+Z) > 1, setting BR(H) = 0 ")
            self.BRH = 0

        valsum = self.BRW + self.BRZ + self.BRH + self.BRS
        if not (valsum == 1.0):
            print ("Branching ratios not normalized. Renormalizing BR(W+Z+H) to 1.0", valsum)
            self.BRW = self.BRW/valsum
            self.BRZ = self.BRZ/valsum
            self.BRH = self.BRH/valsum
            self.BRS = self.BRS/valsum

        self.GammaW = self.Gamma*self.BRW
        self.GammaZ = self.Gamma*self.BRZ
        self.GammaH = self.Gamma*self.BRH
        self.GammaS = self.Gamma*self.BRS

        base_val = (gWeak**2/(128*3.1416))*self.MVLQ**3/MW**2

        self.setc_Vals( math.sqrt( self.GammaW / ( base_val * rhoW(self.MVLQ, self.VLQMode)) ),
                   math.sqrt( self.GammaZ / ( base_val * rhoZ(self.MVLQ, self.VLQMode)) ),
                   math.sqrt( self.GammaH / ( base_val * rhoH(self.MVLQ, self.VLQMode)) ),
                   math.sqrt( self.GammaS / ( base_val * rhoS(self.MEXOT, self.MVLQ, self.VLQMode)) ) )

    def getKappas(self):
        return [self.KappaW, self.KappaZ, self.KappaHleading, self.KappaS]
        
    def getKappa(self):
        return self.Kappa

    def getBRs(self):
        return [self.BRW, self.BRZ, self.BRH, self.BRS]

    def getxis(self):
        return [self.xiW, self.xiZ, self.xiH, self.xiS]

    def getc_Vals(self):
        return [self.cW_, self.cZ_, self.cH_, self.cS_]

    def getcVals(self):
        return [self.cW, self.cZ, self.cH, self.cS]

    def CalcDecayWidths(self):
        base_val = (gWeak**2/(128*3.1416))*self.MVLQ**3/MW**2
        self.GammaW = self.cW_**2*rhoW(self.MVLQ, self.VLQMode)*base_val
        self.GammaZ = self.cZ_**2*rhoZ(self.MVLQ, self.VLQMode)*base_val
        self.GammaH = self.cH_**2*rhoH(self.MVLQ, self.VLQMode)*base_val
        self.GammaS = self.cS_**2*rhoS(self.MEXOT, self.MVLQ, self.VLQMode)*base_val
        self.Gamma = self.GammaW + self.GammaZ + self.GammaH + self.GammaS

    def CalcBRs(self):
        self.CalcDecayWidths()
        if self.Gamma == 0:
            print ("Total Width Zero. Setting All BRs to zero. Check your couplings!")
            self.BRW = 0.
            self.BRZ = 0.
            self.BRH = 0.
            self.BRS = 0.
        else:
            self.BRW = self.GammaW/self.Gamma
            self.BRZ = self.GammaZ/self.Gamma
            self.BRH = self.GammaH/self.Gamma
            self.BRS = self.GammaS/self.Gamma

    def getGamma(self):
        return self.Gamma


    def getGammas(self):
        return [self.GammaW, self.GammaZ, self.GammaH, self.GammaS]


### Calculation of Mixing angles is taken care of the inherited class below
### To keep things simple and avoid L-R interference, we set mb = 0.0


class VLQMixAngleCalculator(VLQCouplingCalculator):
    def __init__(self, mvlq=1000., mode = 'T', multiplet = 'T'):
        VLQCouplingCalculator.__init__(self, mvlq, mode)
        self.setMultiplet(multiplet)
        ## multiplet = 'T', 'B', 'XT', 'TB', 'BY', 'XTB', 'TBY'
        self.Angle_UL = 0.
        self.Angle_UR = 0.
        self.Angle_DL = 0.
        self.Angle_DR = 0.

    def setMultiplet(self, multiplet):
        if multiplet not in ['T', 'B', 'XT', 'TB', 'BY', 'XTB', 'TBY']:
            print ("Multiplet not recognized. Must be one of 'T', 'B', 'XT', 'TB', 'BY', 'XTB', 'TBY'. Selecting 'T' by default.")
            self.VLQMultiplet = 'T'
        else:
            self.VLQMultiplet = multiplet

    def setAngleUL(self, a):
        self.Angle_UL = a
        self.Angle_UR = math.atan(Mt/VLQCouplingCalculator.getMVLQ(self) * math.tan(a))
        self.Angle_DR = 0.
        if self.VLQMultiplet == 'T':
            self.Angle_DL = 0.
        elif self.VLQMultiplet == 'XTB':
            if a > math.pi/8.0:
                print ("maximum value of Angle_UL in XTB triplet it pi/8 i.e. 22.5 degrees. Setting angle to 0.1 radians as default")
                this_a = 0.1
            else: this_a = a
            self.Angle_DL = 0.5*math.asin(1.414 * math.sin(2*this_a))
        elif self.VLQMultiplet == 'TBY':
            self.Angle_DL = 0.5*math.asin( (1. / 1.414) * math.sin(2*a))
        else:
            print ("Angle_UL is not a dominant angle for current choice of SU(2) representation")

    def setAngleDL(self, a):
        self.Angle_DL = a
        self.Angle_DR = 0
        if self.VLQMultiplet == 'B':
            self.Angle_UL = 0.
        elif self.VLQMultiplet == 'XTB':
            self.Angle_UL = 0.5*math.asin( (1./1.414) * math.sin(2*a))
        elif self.VLQMultiplet == 'TBY':
            if a > math.pi/8.0:
                print ("maximum value of Angle_DL in TBY triplet it pi/8 i.e. 22.5 degrees. Setting angle to 0.1 radians as default")
                this_a = 0.1
            else: this_a = a
            self.Angle_UL = 0.5*math.asin(1.414 * math.sin(2*this_a))
        else:
            print ("Angle_DL is not a dominant angle for current choice of SU(2) representation")
        self.Angle_UR = math.atan(Mt/VLQCouplingCalculator.getMVLQ(self) * math.tan(a))

    def setAngleUR(self, a, b = 0.): # the angle b represents Angle_DR for TB multiplet only
        self.Angle_UR = a
        if self.VLQMultiplet == 'XT':
            self.Angle_UL = math.atan(Mt/VLQCouplingCalculator.getMVLQ(self) * math.tan(a))
            self.Angle_DL = 0.
            self.Angle_DR = 0.
        elif self.VLQMultiplet == 'TB':
            self.Angle_UL = math.atan(Mt/VLQCouplingCalculator.getMVLQ(self) * math.tan(a))
            self.Angle_DL = 0.
            self.Angle_DR = b

    def setAngleDR(self, a, b = 0.): # the angle b represents Angle_UR for TB multiplet only
        self.Angle_DR = a
        if self.VLQMultiplet == 'BY':
            self.Angle_UL = 0.
            self.Angle_DL = 0.
            self.Angle_UR = 0.
        elif self.VLQMultiplet == 'TB':
            self.Angle_DL = 0.
            self.Angle_UR = b
            self.Angle_UL = math.atan(Mt/VLQCouplingCalculator.getMVLQ(self) * math.tan(b))
            
    def getAngles(self):
        return [self.Angle_UL, self.Angle_UR, self.Angle_DL, self.Angle_DR]
        
    def setCouplings(self):
        rt = Mt/VLQCouplingCalculator.getMVLQ(self)
        if self.VLQMultiplet == 'T':
            VLQCouplingCalculator.setc_Vals(self,
                1.414*math.sin(self.Angle_UL),
                math.sin(self.Angle_UL)*math.cos(self.Angle_UL),
                math.sqrt(1+rt**2)*math.sin(self.Angle_UL)*math.cos(self.Angle_UL)
            )
        if self.VLQMultiplet == 'B':
            VLQCouplingCalculator.setc_Vals(self,
                1.414*math.sin(self.Angle_DL),
                math.sin(self.Angle_DL)*math.cos(self.Angle_DL),
                math.sin(self.Angle_DL)*math.cos(self.Angle_DL)
            )
        
        if self.VLQMultiplet == 'XTB':
            if VLQCouplingCalculator.getVLQMode(self) == 'X':
                VLQCouplingCalculator.setc_Vals(self,
                    2*math.sqrt(math.sin(self.Angle_UL)**2 + math.sin(self.Angle_UR)**2),
                    0.,
                    0.
                )
            if VLQCouplingCalculator.getVLQMode(self) == 'T':
                VLQCouplingCalculator.setc_Vals(self,
                    1.414*(math.sin(self.Angle_UL)*math.cos(self.Angle_DL) - 1.414*math.cos(self.Angle_UL)*math.sin(self.Angle_DL)),
                    math.sin(self.Angle_UL)*math.cos(self.Angle_UL),
                    math.sqrt(1+rt**2)*math.sin(self.Angle_UL)*math.cos(self.Angle_UL)
                )
            if VLQCouplingCalculator.getVLQMode(self) == 'B':
                VLQCouplingCalculator.setc_Vals(self,
                    1.414 * math.sqrt( (math.cos(self.Angle_UL)*math.sin(self.Angle_DL) - 1.414*math.sin(self.Angle_UL)*math.cos(self.Angle_DL)) ** 2 + (1.414*math.sin(self.Angle_UR)) **2 ),
                math.sin(self.Angle_DL)*math.cos(self.Angle_DL),
                math.sin(self.Angle_DL)*math.cos(self.Angle_DL)
                )
        if self.VLQMultiplet == 'TBY':
            if VLQCouplingCalculator.getVLQMode(self) == 'Y':
                VLQCouplingCalculator.setc_Vals(self,
                    2*math.sin(self.Angle_DL),
                    0.,
                    0.
                )
            if VLQCouplingCalculator.getVLQMode(self) == 'T':
                VLQCouplingCalculator.setc_Vals(self,
                    1.414*(math.sin(self.Angle_UL)*math.cos(self.Angle_DL) - 1.414*math.cos(self.Angle_UL)*math.sin(self.Angle_DL)),
                    math.sqrt((math.sin(self.Angle_UL)*math.cos(self.Angle_UL)) ** 2 + (2*math.sin(self.Angle_UR)*math.cos(self.Angle_UR))**2),
                    math.sqrt(1+rt**2)*math.sin(self.Angle_UL)*math.cos(self.Angle_UL)
                )
            if VLQCouplingCalculator.getVLQMode(self) == 'B':
                VLQCouplingCalculator.setc_Vals(self,
                    1.414 * math.sqrt( (math.cos(self.Angle_DL)*math.sin(self.Angle_DL) - 1.414*math.sin(self.Angle_UL)*math.cos(self.Angle_DL)) ** 2 + (1.414*math.sin(self.Angle_UR)) **2 ),
                math.sin(self.Angle_DL)*math.cos(self.Angle_DL),
                math.sin(self.Angle_DL)*math.cos(self.Angle_DL)
                )
        if self.VLQMultiplet == 'XT':
            if VLQCouplingCalculator.getVLQMode(self) == 'X':
                VLQCouplingCalculator.setc_Vals(self,
                    1.414*math.sqrt(math.sin(self.Angle_UL)**2 + math.sin(self.Angle_UR)**2),
                    0.,
                    0.
                )
            if VLQCouplingCalculator.getVLQMode(self) == 'T':
                VLQCouplingCalculator.setc_Vals(self,
                    1.414*(math.sin(self.Angle_UL)),
                    math.sqrt((2*math.sin(self.Angle_UL)*math.cos(self.Angle_UR))**2 + (math.sin(self.Angle_UR)*math.cos(self.Angle_UR))**2),
                    math.sqrt(1+rt**2)*math.sin(self.Angle_UR)*math.cos(self.Angle_UR)
                )
        if self.VLQMultiplet == 'BY':
            if VLQCouplingCalculator.getVLQMode(self) == 'Y':
                VLQCouplingCalculator.setc_Vals(self,
                    1.414*math.sin(self.Angle_DR),
                    0.,
                    0.
                )
            if VLQCouplingCalculator.getVLQMode(self) == 'B':
                VLQCouplingCalculator.setc_Vals(self,
                    1.414*(math.sin(self.Angle_DL)),
                    math.sin(self.Angle_DR)*math.cos(self.Angle_DR),
                    math.sin(self.Angle_DR)*math.cos(self.Angle_DR)
                )
        if self.VLQMultiplet == 'TB':
            if VLQCouplingCalculator.getVLQMode(self) == 'T':
                VLQCouplingCalculator.setc_Vals(self,
                    1.414*math.sqrt( math.sin(self.Angle_UL) ** 2 + (math.cos(self.Angle_UR) * math.sin(self.Angle_DR)) **2 ),
                    math.sin(self.Angle_UR)*math.cos(self.Angle_UR),
                    math.sqrt(1 + rt**2)*math.sin(self.Angle_UR)*math.cos(self.Angle_UR)
                )
            if VLQCouplingCalculator.getVLQMode(self) == 'B':
                VLQCouplingCalculator.setc_Vals(self,
                    1.414*math.sqrt( math.sin(self.Angle_UL) ** 2 + (math.cos(self.Angle_DR) * math.sin(self.Angle_UR)) **2 ),
                    math.sin(self.Angle_DR)*math.cos(self.Angle_DR),
                    math.sin(self.Angle_DR)*math.cos(self.Angle_DR)
                )
            
            
            
