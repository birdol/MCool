from __future__ import division #Make integer 3/2 give 1.5 in python 2.x
from math import floor,ceil
from CoolProp.CoolProp import Props
from FinCorrelations import FinInputs
from Evaporator import EvaporatorClass
import numpy as np, pylab
import copy
from CoolProp.Plots import Ph
from scipy.optimize import newton
from ACHPTools import Write2CSV

#MultiCircuitEvaporator inherits things from the Evaporator base class
class MultiCircuitEvaporatorClass(EvaporatorClass):
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
    def Update(self,**kwargs):
        self.__dict__.update(kwargs)

    def OutputList(self):
        """
            Return a list of parameters for this component for further output
            
            It is a list of tuples, and each tuple is formed of items:
                [0] Description of value
                [1] Units of value
                [2] The value itself
        """
        Output_list=[]
        num_evaps= int(self.Fins.Tubes.Ncircuits)
        Output_list_i=[]
        for i in range(num_evaps):                                                                                                                              #Generate output list with all evaporators
            Output_list_i.append([('Volumetric flow rate'+' '+str(i),'m^3/s',self.Evaps[i].Fins.Air.Vdot_ha),
                                    ('Inlet Dry bulb temp'+' '+str(i),'K',self.Evaps[i].Fins.Air.Tdb),
                                        ('Inlet Air pressure'+' '+str(i),'kPa',self.Evaps[i].Fins.Air.p),
                                        ('Inlet Air Relative Humidity'+' '+str(i),'-',self.Evaps[i].Fins.Air.RH),
                                        ('Tubes per bank'+' '+str(i),'-',self.Evaps[i].Fins.Tubes.NTubes_per_bank),
                                        ('Number of banks'+' '+str(i),'-',self.Evaps[i].Fins.Tubes.Nbank),
                                        ('Number circuits'+' '+str(i),'-',self.Evaps[i].Fins.Tubes.Ncircuits),
                                        ('Length of tube'+' '+str(i),'m',self.Evaps[i].Fins.Tubes.Ltube),
                                        ('Tube OD'+' '+str(i),'m',self.Evaps[i].Fins.Tubes.OD),
                                        ('Tube ID'+' '+str(i),'m',self.Evaps[i].Fins.Tubes.ID),
                                        ('Tube Long. Pitch'+' '+str(i),'m',self.Evaps[i].Fins.Tubes.Pl),
                                        ('Tube Transverse Pitch'+' '+str(i),'m',self.Evaps[i].Fins.Tubes.Pt),
                                        ('Outlet superheat'+' '+str(i),'K',self.Evaps[i].Tout_r-self.Evaps[i].Tdew_r),
                                        ('Fins per inch'+' '+str(i),'1/in',self.Evaps[i].Fins.Fins.FPI),
                                        ('Fin waviness pd'+' '+str(i),'m',self.Evaps[i].Fins.Fins.Pd),
                                        ('Fin waviness xf'+' '+str(i),'m',self.Evaps[i].Fins.Fins.xf),
                                        ('Fin thickness'+' '+str(i),'m',self.Evaps[i].Fins.Fins.t),
                                        ('Fin Conductivity'+' '+str(i),'W/m-K',self.Evaps[i].Fins.Fins.k_fin),
                                        ('Refrigerant flowrate'+' '+str(i),'kg/s',self.Evaps[i].mdot_r),
                                        ('Q Total'+' '+str(i),'W',self.Evaps[i].Q),
                                        ('Q Superheat'+' '+str(i),'W',self.Evaps[i].Q_superheat),
                                        ('Q Two-Phase'+' '+str(i),'W',self.Evaps[i].Q_2phase),
                                        ('Inlet ref. temp'+' '+str(i),'K',self.Evaps[i].Tin_r),
                                        ('Outlet ref. temp'+' '+str(i),'K',self.Evaps[i].Tout_r),
                                        ('Outlet air temp'+' '+str(i),'K',self.Evaps[i].Tout_a),
                                        ('Pressure Drop Total'+' '+str(i),'Pa',self.Evaps[i].DP_r),
                                        ('Pressure Drop Superheat'+' '+str(i),'Pa',self.Evaps[i].DP_r_superheat),
                                        ('Pressure Drop Two-Phase'+' '+str(i),'Pa',self.Evaps[i].DP_r_2phase),
                                        ('Charge Total'+' '+str(i),'kg',self.Evaps[i].Charge),
                                        ('Charge Superheat'+' '+str(i),'kg',self.Evaps[i].Charge_superheat),
                                        ('Charge Two-Phase'+' '+str(i),'kg',self.Evaps[i].Charge_2phase),
                                        ('Mean HTC Superheat'+' '+str(i),'W/m^2-K',self.Evaps[i].h_r_superheat),
                                        ('Mean HTC Two-phase'+' '+str(i),'W/m^2-K',self.Evaps[i].h_r_2phase),
                                        ('Wetted Area Fraction Superheat'+' '+str(i),'-',self.Evaps[i].w_superheat),
                                        ('Wetted Area Fraction Two-phase'+' '+str(i),'-',self.Evaps[i].w_2phase),
                                        ('Mean Air HTC'+' '+str(i),'W/m^2-K',self.Evaps[i].Fins.h_a),
                                        ('Surface Effectiveness'+' '+str(i),'-',self.Evaps[i].Fins.eta_a),
                                        ('Air-side area (fin+tubes)'+' '+str(i),'m^2',self.Evaps[i].Fins.A_a),
                                        ('Mass Flow rate dry Air'+' '+str(i),'kg/s',self.Evaps[i].Fins.mdot_da),
                                        ('Mass Flow rate humid Air'+' '+str(i),'kg/s',self.Evaps[i].Fins.mdot_ha),
                                        ('Pressure Drop Air-side'+' '+str(i),'Pa',self.Evaps[i].Fins.dP_a),
                                        ('Sensible Heat Ratio'+' '+str(i),'-',self.Evaps[i].SHR)])
        for i in range(len(Output_list_i[0])):                                                                                                  #sort output list, such that corresponding values are next to each other
            sumsi=0    #need sums and avgs
            for n in range(num_evaps):
                Output_list.append(Output_list_i[n][i])
                if type(Output_list_i[n][i][2]) is not type("string"):
                    sumsi+=Output_list_i[n][i][2] #sum up values
                    if n == num_evaps-1:
                         Output_list.append((Output_list_i[n][i][0][:-2]+" sum",Output_list_i[n][i][1],sumsi))
                         Output_list.append((Output_list_i[n][i][0][:-2]+" avg",Output_list_i[n][i][1],sumsi/num_evaps))
        Output_List_tot=[]
        #append optional parameters, if applicable
        if hasattr(self,'TestName'):
            Output_List_tot.append(('Name','N/A',self.TestName)) 
        if hasattr(self,'TestDescription'):
            Output_List_tot.append(('Description','N/A',self.TestDescription))
        if hasattr(self,'TestDetails'):
            Output_List_tot.append(('Details','N/A',self.TestDetails))
        for i in range(0,len(Output_list)):                             #append default parameters to output list
            Output_List_tot.append(Output_list[i])
        return Output_List_tot

    def Calculate(self):
        #Check that the length of lists of mdot_r and FinsTubes.Air.Vdot_ha 
        #match the number of circuits or are all equal to 1 (standard evap)
        Ncircuits=int(self.Fins.Tubes.Ncircuits)
        
        # Make Ncircuits copies of evaporator classes defined 
        #  by the inputs to the MCE superclass
        EvapDict=self.__dict__
        self.Evaps=[]
        for i in range(Ncircuits):
            # Make a deep copy to break all the links between the Fins structs
            # of each of the evaporator instances
            ED=copy.deepcopy(EvapDict)
            #Create new evaporator instanciated with new deep copied dictionary
            E=EvaporatorClass(**ED)
            #Add to list of evaporators
            self.Evaps.append(E)
            
        #Upcast single values to lists, and convert numpy arrays to lists
        self.Fins.Air.Vdot_ha=np.atleast_1d(self.Fins.Air.Vdot_ha).tolist()
        self.mdot_r=np.atleast_1d(self.mdot_r).tolist()
        
        if Ncircuits != len(self.mdot_r) and len(self.mdot_r)>1:
            print "Problem with length of vector for mdot_r for MCE"
        else:
            if len(self.mdot_r)==1: #Single value passed in for mdot_r
                if hasattr(self,'mdot_r_coeffs'):
                    if len(self.mdot_r_coeffs)!=Ncircuits:
                        raise AttributeError("Size of array mdot_r_coeffs: "+str(len(self.mdot_r_coeffs))+" does not equal Ncircuits: "+str(Ncircuits))
                    elif abs(np.sum(self.mdot_r_coeffs)-1)>=100*np.finfo(float).eps:
                        raise AttributeError("mdot_r_coeffs must sum to 1.0.  Sum *100000is: "+str(100000*np.sum(self.mdot_r_coeffs)))
                    else:
                        # A vector of weighting factors multiplying the total mass flow rate is provided with the right length
                        for i in range(Ncircuits):
                            self.Evaps[i].mdot_r=self.mdot_r[-1]*self.mdot_r_coeffs[i]
                else:
                    # Refrigerant flow is evenly distributed between circuits,
                    # give each evaporator an equal portion of the refrigerant
                    for i in range(Ncircuits):
                        self.Evaps[i].mdot_r=self.mdot_r[-1]/Ncircuits
            else:
                for i in range(Ncircuits):
                    self.Evaps[i].mdot_r=self.mdot_r[i]
                   
        # Deal with the possibility that the quality might be varied among circuits
        if hasattr(self,'mdot_v_coeffs'):
            if len(self.mdot_v_coeffs)!=Ncircuits:
                raise AttributeError("Size of array mdot_v_coeffs: "+str(len(self.mdot_v_coeffs))+" does not equal Ncircuits: "+str(Ncircuits))
            elif abs(np.sum(self.mdot_v_coeffs)-1)>=10*np.finfo(float).eps:
                raise AttributeError("mdot_v_coeffs must sum to 1.0.  Sum is: "+str(np.sum(self.mdot_v_coeffs)))
            else:
                hsatL=Props('H','P',self.psat_r,'Q',0.0,self.Ref)*1000
                hsatV=Props('H','P',self.psat_r,'Q',1.0,self.Ref)*1000
                x_inlet=(self.hin_r-hsatL)/(hsatV-hsatL)
                mdot_v=x_inlet*sum(self.mdot_r)
                for i in range(Ncircuits):
                    mdot_v_i=self.mdot_v_coeffs[i]*mdot_v
                    x_i=mdot_v_i/self.Evaps[i].mdot_r
                    self.Evaps[i].hin_r=Props('H','P',self.psat_r,'Q',x_i,self.Ref)*1000
                 
        #For backwards compatibility, if the coefficients are provided in the FinInputs class, copy them to the base class
        if hasattr(self.Fins.Air,'Vdot_ha_coeffs'):
            self.Vdot_ha_coeffs=self.Fins.Air.Vdot_ha_coeffs
            print "Warning: please put the vector Vdot_ha_coeffs in the base MCE class, accesssed as MCE.Vdot_ha_coeffs"
            
        if Ncircuits !=len(self.Fins.Air.Vdot_ha) and len(self.Fins.Air.Vdot_ha)>1:
            print "Problem with length of vector for Vdot_ha for MCE"
        else:
            if len(self.Fins.Air.Vdot_ha)==1:
                if hasattr(self,'Vdot_ha_coeffs'):
                    if len(self.Vdot_ha_coeffs)!=Ncircuits:
                        raise AttributeError("Size of array Vdot_ha_coeffs: "+str(len(self.Vdot_ha_coeffs))+" does not equal Ncircuits: "+str(Ncircuits))
                    elif abs(np.sum(self.Vdot_ha_coeffs)-1)>=10*np.finfo(float).eps:
                        raise AttributeError("Vdot_ha_coeffs does not sum to 1.0!")                        
                    else:                        
                        # A vector of factors multiplying the total volume flow rate is provided
                        for i in range(Ncircuits):
                            self.Evaps[i].Fins.Air.Vdot_ha=self.Fins.Air.Vdot_ha[-1]*self.Vdot_ha_coeffs[i]
                else:
                    # Air flow is evenly distributed between circuits,
                    # give each circuit an equal portion of the air flow
                    for i in range(Ncircuits):
                        self.Evaps[i].Fins.Air.Vdot_ha=self.Fins.Air.Vdot_ha[-1]/Ncircuits
            else:
                for i in range(Ncircuits):
                    self.Evaps[i].Fins.Air.Vdot_ha=self.Fins.Air.Vdot_ha[i]
                    
        # Distribute the tubes of the bank among the different circuits
        # If Tubes per bank is divisible by the number of circuits, all the 
        # circuits have the same number of tubes per bank
        
        # The circuits are ordered from fewer to more if they are not evenly distributed
        NTubes_min=int(floor(self.Fins.Tubes.NTubes_per_bank/Ncircuits))
        NTubes_max=int(ceil(self.Fins.Tubes.NTubes_per_bank/Ncircuits))
        
        if NTubes_min==NTubes_max:
            #If evenly divisible, use the tubes per circuit from the division
            A=Ncircuits
        else:
            # Total number of tubes per bank is given by
            # NTubesPerBank=A*NTube_min+(Ncircuits-A)*NTube_max
            # A=(NTubesPerBank-Ncircuits*NTube_max)/(NTube_min-Ntube_max)
            A=(self.Fins.Tubes.NTubes_per_bank-Ncircuits*NTubes_max)/(NTubes_min-NTubes_max)
        
        for i in range(Ncircuits):
            if i+1<=A:
                self.Evaps[i].Fins.Tubes.NTubes_per_bank=NTubes_min
            else:
                self.Evaps[i].Fins.Tubes.NTubes_per_bank=NTubes_max
            
        for i in range(Ncircuits):
            self.Evaps[i].Fins.Tubes.Ncircuits=1
            #Actually run each Evaporator
            self.Evaps[i].Calculate()
            
        #Collect the outputs from each of the evaporators individually
        #Try to mirror the outputs of each of the evaporators
        self.Q=np.sum([self.Evaps[i].Q for i in range(Ncircuits)])
        self.Charge=np.sum([self.Evaps[i].Charge for i in range(Ncircuits)])
        self.Charge_superheat=np.sum([self.Evaps[i].Charge_superheat for i in range(Ncircuits)])
        self.Charge_2phase=np.sum([self.Evaps[i].Charge_2phase for i in range(Ncircuits)])
        self.DP_r=np.mean([self.Evaps[i].DP_r for i in range(Ncircuits)])  #simplified
        self.DP_r_superheat=np.mean([self.Evaps[i].DP_r_superheat for i in range(Ncircuits)])  #simplified
        self.DP_r_2phase=np.mean([self.Evaps[i].DP_r_2phase for i in range(Ncircuits)])  #simplified
        self.Tin_r=np.mean([self.Evaps[i].Tin_r for i in range(Ncircuits)])  #simplified
        self.h_r_superheat=np.mean([self.Evaps[i].h_r_superheat for i in range(Ncircuits)])  #simplified, really should consider flowrate
        self.h_r_2phase=np.mean([self.Evaps[i].h_r_2phase for i in range(Ncircuits)])  #simplified, really should consider flowrate
        self.w_superheat=np.sum([self.Evaps[i].w_superheat for i in range(Ncircuits)])/float(Ncircuits)
        self.w_2phase=np.sum([self.Evaps[i].w_2phase for i in range(Ncircuits)])/float(Ncircuits)
        self.hout_r=0.0
        for i in range(Ncircuits): self.hout_r+=self.Evaps[i].hout_r*self.Evaps[i].mdot_r 
        self.hout_r=(self.hout_r/self.mdot_r[0])
        self.Tin_a=self.Evaps[0].Fins.Air.Tdb #assuming equal temperature for all circuits
        self.Tout_a=0.0
        for i in range(Ncircuits): self.Tout_a+=self.Evaps[i].Tout_a*self.Evaps[i].Fins.Air.Vdot_ha
        
        self.Tout_a=(self.Tout_a/self.Fins.Air.Vdot_ha[0])
        Pout_r=self.psat_r+self.DP_r/1000.0
        hsatV_out=Props('H','P',Pout_r,'Q',1.0,self.Ref)*1000
        hsatL_out=Props('H','P',Pout_r,'Q',0.0,self.Ref)*1000
        if self.hout_r>hsatV_out:
            self.Tout_r=newton(lambda T: Props('H','T',T,'P',Pout_r,self.Ref)-self.hout_r/1000,Props('T','P',Pout_r,'Q',1.0,self.Ref))  #saturated temperature at outlet quality
        else:
            xout_r=((self.hout_r-hsatL_out)/(hsatV_out-hsatL_out))
            self.Tout_r=Props('T','P',Pout_r,'Q',xout_r,self.Ref) #saturated temperature at outlet quality
        self.Capacity=np.sum([self.Evaps[i].Q for i in range(Ncircuits)])-self.Fins.Air.FanPower
        self.SHR=np.mean([self.Evaps[i].SHR for i in range(Ncircuits)])
        self.UA_a=np.sum([self.Evaps[i].UA_a for i in range(Ncircuits)])
        self.UA_r=np.sum([self.Evaps[i].UA_r for i in range(Ncircuits)])
        self.Q_superheat=np.sum([self.Evaps[i].Q_superheat for i in range(Ncircuits)])
        self.Q_2phase=np.sum([self.Evaps[i].Q_2phase for i in range(Ncircuits)])
                #Convert back to a single value for the overall evaporator
        self.Fins.Air.Vdot_ha=float(self.Fins.Air.Vdot_ha[-1])
        if self.Verbosity>0:
            print chr(127), #progress bar
if __name__=='__main__':
    #This code runs if this file is run by itself, but otherwise doesn't run
    FinsTubes=FinInputs()

    FinsTubes.Tubes.NTubes_per_bank=32
    FinsTubes.Tubes.Ncircuits=5
    FinsTubes.Tubes.Nbank=3
    FinsTubes.Tubes.Ltube=0.452
    FinsTubes.Tubes.OD=0.009525
    FinsTubes.Tubes.ID=0.0089154
    FinsTubes.Tubes.Pl=0.0254
    FinsTubes.Tubes.Pt=0.0219964
    
    FinsTubes.Fins.FPI=14.5
    FinsTubes.Fins.Pd=0.001
    FinsTubes.Fins.xf=0.001
    FinsTubes.Fins.t=0.00011
    FinsTubes.Fins.k_fin=237
    
    FinsTubes.Air.Vdot_ha=0.5663
    FinsTubes.Air.Tmean=299.8
    FinsTubes.Air.Tdb=299.8
    FinsTubes.Air.p=101.325
    FinsTubes.Air.RH=0.51
    FinsTubes.Air.RHmean=0.51
    FinsTubes.Air.FanPower=438
        
    Tdew=282.0
    kwargs={'Ref': 'R410A',
            'mdot_r':  0.0708,
            'psat_r':  Props('P','T',Tdew,'Q',1.0,'R410A'),
            'Fins': FinsTubes,
            'hin_r':Props('H','T',Tdew,'Q',0,'R410A')*1000,
            'Verbosity':0
    }
    
    Evap=EvaporatorClass(**kwargs)
    Evap.Update(**kwargs)
    Evap.Calculate()
    print 'Q=' + str(Evap.Q) + ' W'
        
    Tdew=282.0
    kwargs={'Ref': 'R410A',
            'mdot_r':  0.0708,
            'mdot_r_coeffs':[0.1,0.1,0.3,0.3,0.2],   #Mass flow distribution at distributor
            'mdot_v_coeffs':[0.2,0.2,0.2,0.2,0.2],  #Quality distribution at distributor
            'Vdot_ha_coeffs':[0.2,0.2,0.2,0.2,0.2], #airside flow distribution
            'psat_r':  Props('P','T',Tdew,'Q',1.0,'R410A'),
            'Fins': FinsTubes,
            'hin_r':Props('H','T',Tdew,'Q',0,'R410A')*1000,
            'Verbosity':0,
            'TestName':'MCE-0014',  #this and the two next lines can be used to specify exact test conditions
             'TestDescription':'shows application of MCE',
             'TestDetails':'This is the sample multi circuited evaporator'
    }
    
    MCE=MultiCircuitEvaporatorClass(**kwargs)
    MCE.Update(**kwargs)
    MCE.Calculate()
    print MCE.OutputList()
    Write2CSV(MCE,open('Evaporator_MCE.csv','w'),append=False)
    """
    print 'Q='+str(MCE.Q)+' W'
    print MCE.hin_r*MCE.mdot_r[-1]
    print np.sum([MCE.Evaps[i].hin_r*MCE.Evaps[i].mdot_r for i in range(MCE.Fins.Tubes.Ncircuits)])
    h=np.array([MCE.Evaps[i].hout_r for i in range(len(MCE.Evaps))])
    p=MCE.psat_r*(1+0*h)
    
    # plott maldistribution
    Ph('R410A')
    pylab.plot(h/1000,p,'o')
    pylab.plot(MCE.hout_r/1000,MCE.psat_r,'o')
    pylab.show()
    print [MCE.Evaps[i].hout_r for i in range(len(MCE.Evaps))], MCE.hout_r, Props('H','T',MCE.Evaps[-1].Tdew_r,'Q',1,MCE.Evaps[-1].Ref)*1000
    print [MCE.Evaps[i].DT_sh_calc for i in range(len(MCE.Evaps))]
    """