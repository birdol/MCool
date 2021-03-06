from CoolProp.CoolProp import Props
from Correlations import f_h_1phase_Annulus,f_h_1phase_Tube,ShahEvaporation_Average
from Correlations import TwoPhaseDensity,LMPressureGradientAvg,AccelPressureDrop
from math import pi,exp,log
from scipy.optimize import brentq
import numpy as np

class CoaxialHXClass():
    def __init__(self,**kwargs):
        #Load the parameters passed in
        # using the dictionary
        self.__dict__.update(kwargs)
        
    def Update(self,**kwargs):
        #Update the parameters passed in
        # using the dictionary
        self.__dict__.update(kwargs)
        
        # Wetted area on the refrigerant side
        self.A_r_wetted=pi*self.ID_i*self.L
        # Wetted area of the glycol side (not including outer tube)
        self.A_g_wetted=pi*self.OD_i*self.L
        
        self.V_r=self.L*pi*self.ID_i**2/4.0
        self.V_g=self.L*pi*(self.ID_o**2-self.OD_i**2)/4.0
    
    def OutputList(self):
        """
            Return a list of parameters for this component for further output
            
            It is a list of tuples, and each tuple is formed of items:
                [0] Description of value
                [1] Units of value
                [2] The value itself
        """
        
        return [
            ('Length of tube','m',self.L),
            ('Annulus wetted OD','m',self.ID_o),
            ('Annulus wetted ID','m',self.OD_i),
            ('Tube wetted OD','m',self.ID_i),
            ('Outlet Superheat','K',self.Tin_r-self.Tdew_r),
            ('Q Total','W',self.Q),
            ('Q Superheat','W',self.Q_superheat),
            ('Q Two-Phase','W',self.Q_2phase),
            ('Q Subcooled','W',self.Q_subcool),
            ('Inlet glycol temp','K',self.Tin_g),
            ('Outlet glycol temp','K',self.Tout_g),
            ('Inlet ref. temp','K',self.Tin_r),
            ('Outlet ref. temp','K',self.Tout_r),
            ('Charge Total','kg',self.Charge_r),
            ('Charge Superheat','kg',self.Charge_r_superheat),
            ('Charge Two-Phase','kg',self.Charge_r_2phase),
            ('Charge Subcool','kg',self.Charge_r_subcool),
            ('Mean HTC Ref. Superheat','W/m^2-K',self.h_r_superheat),
            ('Mean HTC Ref. Two-Phase','W/m^2-K',self.h_r_2phase),
            ('Mean HTC Ref. Subcool','W/m^2-K',self.h_r_subcool),
            ('Mean HTC Gly. Superheat','W/m^2-K',self.h_g),
            ('Mean Reynolds # Gly. Superheat','-',self.Re_g),
            ('Pressure Drop Gly.','Pa',self.DP_g),
            ('Pressure Drop Ref.','Pa',self.DP_r),
            ('Pressure Drop Ref. Superheat','Pa',self.DP_r_superheat),
            ('Pressure Drop Ref. Two-Phase','Pa',self.DP_r_2phase),
            ('Pressure Drop Ref. Subcool','Pa',self.DP_r_subcool),                                                                           
            ('Area fraction Superheat','-',self.w_superheat),
            ('Area fraction Two-Phase','-',self.w_2phase),
            ('Area fraction Subcooled','-',self.w_subcool)
         ]
        
    def Calculate(self):
        #Update the parameters
        self.Update()
        
        #Average mass flux of refrigerant [kg/m^2-s]
        self.G_r = self.mdot_r/(pi*self.ID_i**2/4.0) 
        #Average mass flux of glycol [kg/m^2-s]
        self.G_g = self.mdot_g/(pi*(self.ID_o**2-self.OD_i**2)/4.0) 
        #Hydraulic diameter
        self.Dh_g=self.ID_o-self.OD_i
        #Evaporation hydraulic diameter [m]
        self.Dh_r=self.ID_i
        
        self.Tbubble_r=Props('T','P',self.pin_r,'Q',0,self.Ref_r)
        self.Tdew_r=Props('T','P',self.pin_r,'Q',1,self.Ref_r)
        self.Tsat_r=(self.Tbubble_r+self.Tdew_r)/2.0
        
        #Inlet enthalpy
        hsatL=Props('H','T',self.Tbubble_r,'Q',0,self.Ref_r)*1000
        hsatV=Props('H','T',self.Tdew_r,'Q',1,self.Ref_r)*1000
        self.xin_r=(self.hin_r-hsatL)/(hsatV-hsatL)
        
        #Change in enthalpy through two-phase region [J/kg]
        self.h_fg=(Props('H','T',self.Tdew_r,'Q',1.0,self.Ref_r)-Props('H','T',self.Tbubble_r,'Q',0.0,self.Ref_r))*1000.
        self.Tin_r=self.xin_r*self.Tdew_r+(1-self.xin_r)*self.Tbubble_r
        #Inlet entropy
        ssatL=Props('S','T',self.Tbubble_r,'Q',0,self.Ref_r)*1000
        ssatV=Props('S','T',self.Tdew_r,'Q',1,self.Ref_r)*1000
        self.sin_r=self.xin_r*ssatV+(1-self.xin_r)*ssatL
        
        #Mean values for the glycol side based on average of inlet temperatures
        Tavg_g=(self.Tsat_r+self.Tin_g)/2.0
        self.f_g,self.h_g,self.Re_g=f_h_1phase_Annulus(self.mdot_g, self.ID_o, self.OD_i, Tavg_g, self.pin_g, self.Ref_g)
        self.cp_g=Props('C','T',Tavg_g,'P',self.pin_g,self.Ref_g)*1000
        
        #Glycol pressure drop
        v_g=1/Props('D','T',Tavg_g,'P',self.pin_g,self.Ref_g)
        dpdz_g=-self.f_g*v_g*self.G_g**2/(2.*self.Dh_g) #Pressure gradient
        self.DP_g=dpdz_g*self.L
        
        def OBJECTIVE(w_superheat):
            """Nested function for driving the Brent's method solver"""
            #Run the superheated portion
            self._Superheat_Forward(w_superheat)
            #Run the two-phase portion and return residual
            return self._TwoPhase_Forward(1-w_superheat)
        
        def OBJECTIVE_2phase(xout_2phase):
            """Nested function for finding outlet quality"""
            #Need to pass in outlet quality but still maintain the full w_2phase 
            return self._TwoPhase_Forward(1.0,xout_2phase)
        
        # First see if you have a superheated portion.  Try to use the entire HX
        # for the two-phase portion
        # ---------------------
        # Intermediate glycol temp between superheated and 2phase sections [K] 
        self.T_g_x=self.Tin_g
        #Call two-phase forward method
        error=self._TwoPhase_Forward(1.0)
        # If HT greater than required
        if error>0:
            #Too much HT if all is 2phase, there is a superheated section
            existsSuperheat=True
            #Solve for the break between 2phase and superheated parts
            w_superheat=brentq(OBJECTIVE,0.00001,0.99999)
            self.w_2phase=1-w_superheat
            self.w_superheat=w_superheat
        else:
            existsSuperheat=False
            # Solve for outlet quality in 2phase section, lowest possible outlet 
            # quality is the inlet quality
            self.xout_2phase=brentq(OBJECTIVE_2phase,self.xin_r,0.99999)
            #Dummy variables for the superheated section which doesn't exist
            self.Q_superheat=0.0
            self.Charge_r_superheat=0.0
            self.h_r_superheat=0.0
            self.DP_r_superheat=0.0
            self.w_superheat=0.0
            self.w_2phase=1.0
            
        self.Charge_r=self.Charge_r_2phase+self.Charge_r_superheat
        self.Q=self.Q_2phase+self.Q_superheat
        self.Tout_g=self.Tin_g-self.Q/(self.cp_g*self.mdot_g)
        
        self.DP_r=self.DP_r_2phase+self.DP_r_superheat
        
        if existsSuperheat==True:
            self.hout_r=Props('H','T',self.Tout_r,'P',self.pin_r,self.Ref_r)*1000
            self.sout_r=Props('S','T',self.Tout_r,'P',self.pin_r,self.Ref_r)*1000
        else:
            self.Tout_r=self.xout_2phase*self.Tdew_r+(1-self.xout_2phase)*self.Tbubble_r
            self.hout_r=Props('H','T',self.Tout_r,'Q',self.xout_2phase,self.Ref_r)*1000
            self.sout_r=Props('S','T',self.Tout_r,'Q',self.xout_2phase,self.Ref_r)*1000
        
        #Dummy variables for the subcooled section which doesn't exist
        self.Q_subcool=0.0
        self.DP_r_subcool=0.0
        self.h_r_subcool=0.0
        self.Re_r_subcool=0.0
        self.Charge_r_subcool=0.0
        self.w_subcool=0.0
        
    def _Superheat_Forward(self,w_superheat):
        # Superheated portion
        # Mean temperature for superheated part can be taken to be average
        # of dew and glycol inlet temps
        Tavg_sh_r=(self.Tdew_r+self.Tin_g)/2.0
        self.f_r_superheat,self.h_r_superheat,self.Re_r_superheat=f_h_1phase_Tube(self.mdot_r, self.ID_i, Tavg_sh_r, self.pin_r, self.Ref_r)
        cp_r_superheat=Props('C','T',Tavg_sh_r,'P',self.pin_r,self.Ref_r)*1000
        # Overall conductance of heat transfer surface in superheated
        # portion
        UA_superheat=w_superheat/(1/(self.h_g*self.A_g_wetted)+1/(self.h_r_superheat*self.A_r_wetted))
        #List of capacitance rates [W/K]
        C=[cp_r_superheat*self.mdot_r,self.cp_g*self.mdot_g]
        Cmin=min(C)
        Cr=Cmin/max(C)
        Ntu_superheat=UA_superheat/Cmin
        epsilon_superheat = ((1 - exp(-Ntu_superheat * (1 - Cr))) / 
            (1 - Cr * exp(-Ntu_superheat * (1 - Cr))))
        self.Q_superheat=epsilon_superheat*Cmin*(self.Tin_g-self.Tdew_r)
        
        self.Tout_r=self.Tdew_r+self.Q_superheat/(self.mdot_r*cp_r_superheat)
        rho_superheat=Props('D','T',(self.Tin_g+self.Tdew_r)/2.0, 'P', self.pin_r, self.Ref_r)
        self.Charge_r_superheat = w_superheat * self.V_r * rho_superheat
        
        #Pressure drop calculations for superheated refrigerant
        v_r=1./rho_superheat;
        #Pressure gradient using Darcy friction factor
        dpdz_r=-self.f_r_superheat*v_r*self.G_r**2/(2.*self.Dh_r) #Pressure gradient
        self.DP_r_superheat=dpdz_r*self.L*w_superheat
        
        # Temperature of "glycol" at the point where the refrigerant is at
        # a quality of 1.0 [K]
        self.T_g_x=self.Tin_g-self.Q_superheat/(self.cp_g*self.mdot_g)
        
    def _TwoPhase_Forward(self,w_2phase=1.0,xout_2phase=1.0):
        # Update outlet quality field [-]
        self.xout_2phase=xout_2phase
        # Heat transfer rate based on inlet quality [W]
        self.Q_2phase=self.mdot_r*(self.xout_2phase-self.xin_r)*self.h_fg
        # Heat flux in 2phase section (for Shah correlation) [W/m^2]
        q_flux=self.Q_2phase/(w_2phase*self.A_r_wetted)
        #
        self.h_r_2phase=ShahEvaporation_Average(self.xin_r,1.0,self.Ref_r,
                    self.G_r,self.Dh_r,self.pin_r,q_flux,self.Tbubble_r,self.Tdew_r)
        UA_2phase=w_2phase/(1/(self.h_g*self.A_g_wetted)+1/(self.h_r_2phase*self.A_r_wetted))
        C_g=self.cp_g*self.mdot_g
        Ntu_2phase=UA_2phase/(C_g)
        epsilon_2phase=1-exp(-Ntu_2phase)
        Q_2phase_eNTU=epsilon_2phase*C_g*(self.T_g_x-self.Tsat_r)
        
        rho_average=TwoPhaseDensity(self.Ref_r,self.xin_r,xout_2phase,self.Tdew_r,self.Tbubble_r,slipModel='Zivi')
        self.Charge_r_2phase = rho_average * w_2phase * self.V_r     
        
        # Frictionalprssure drop component
        DP_frict=LMPressureGradientAvg(self.xin_r,xout_2phase,self.Ref_r,self.G_r,self.Dh_r,self.Tbubble_r,self.Tdew_r)*w_2phase*self.L
        # Accelerational prssure drop component
        DP_accel=AccelPressureDrop(self.xin_r,xout_2phase,self.Ref_r,self.G_r,self.Tbubble_r,self.Tdew_r)
        self.DP_r_2phase=DP_frict+DP_accel
        
        if self.Verbosity>4:
            print Q_2phase_eNTU-self.Q_2phase
        return Q_2phase_eNTU-self.Q_2phase
        
if __name__=='__main__':
    
    TT=[]
    QQ=[]
    Q1=[]
    for Tdew_evap in np.linspace(270,290.4):
        Tdew_cond=317.73
#        Tdew_evap=285.42
        pdew_cond=Props('P','T',Tdew_cond,'Q',1.0,'R290')
        h=Props('H','T',Tdew_cond-7,'P',pdew_cond,'R290')*1000
        params={
                'ID_i':0.0278,
                'OD_i':0.03415,
                'ID_o':0.045,
                'L':50,
                'mdot_r':0.040,
                'mdot_g':0.38,
                'hin_r':h,
                'pin_r':Props('P','T',Tdew_evap,'Q',1.0,'R290'),
                'pin_g':300,
                'Tin_g':290.52,
                'Ref_r':'R290',
                'Ref_g':'Water',
                'Verbosity':0
                }
        IHX=CoaxialHXClass(**params)
        IHX.Calculate()
        
        TT.append(Tdew_evap)
        QQ.append(IHX.h_r_2phase)#IHX.Q)
        Q1.append(IHX.h_r_superheat)
                  
        print IHX.Q
    
    