#########################################################################
#################     Unit conversions for ACHP         #################
#########################################################################
'''This module is used to convert values between different units,
   as needed commonly for ACHP'''

#import necessary modules
from __future__ import division
from numpy import array, ones,ndarray
"""##### Array handling (convenience function ####################################"""
def unitconvert(value,function):
    try:
        return function(value)
    except:
        try:
            result=ones(len(value))
        except:
            print value
            result=ones(value.size)
        for i in range(0,len(value)):
            if type(value[i])!=float:
                value[i]=float(value[i])
            result[i]=function(float(value[i]))
        return result
"""##### Temperature ####################################"""
def F2K(T_F):
    """Convert temperature in Fahrenheit to Kelvin"""
    return 5/9*(T_F+459.67)
def C2K(T_C):
    """Convert temperature in Celsius to Kelvin"""
    return T_C+273.15
def K2C(T_C):
    """Convert temperature in Kelvin to Celsius"""
    return T_C-273.15

"""##### Massflow    ####################################"""
def lbh2kgs(lbm):
    """Convert pound per minute to kilogramms per second"""
    return 0.000125998*lbm #0.45359237 [kg/lbm]/3600 [s/h]
def lbm2kgs(lbm):
    """Convert pound per minute to kilogramms per second"""
    return 0.007559873*lbm #0.45359237 [kg/lbm]/60 [s/h]
def kgh2kgs(kgh):
    """Convert kilograms per hour to kilogramms per second"""
    return kgh/3600.0 

"""##### Volumetric flow ####################################"""
def cfm2cms(cfm):
    """"convert cubic feet per minute(cfm) to cubic meters per second(cms)"""
    return 0.0004719474*cfm  #(0.3048[ft/m])^3/60[s/minute]
def cms2cfm(cms):
    """"convert cubic feet per minute(cfm) to cubic meters per second(cms)"""
    return cms/0.0004719474  #(0.3048[ft/m])^3/60[s/minute]

"""##### Energy     ####################################"""
def kJ2J(kJ):
    """Convert kJ to J """
    return kJ*1000.0
def J2kJ(J):
    """Convert J to kJ"""
    return J/1000.0

"""##### Power     ####################################"""
def BTUh2W(btuh):
    """convert Btu/h to W"""
    return btuh*0.2928104
def kW2W(kW):
    """convert kW to W"""
    return kW*1000.0

"""##### Pressure     ####################################"""
def kPa2Pa(kPa):
    """ convert kPa to Pa"""
    return kPa*1000.0
def MPa2kPa(MPa):
    """convert MPa to kPa"""
    return MPa*1000.0
def MPa2Pa(MPa):
    """convert MPa to Pa"""
    return MPa*1000000

"""##### Length ####################################"""
def in2m(inch):
    "convert inch to meters"
    return inch*0.0254
def ft2m(ft):
    "convert feet to meters"
    return ft*0.3048

"""##### Area ####################################"""
def sqin2sqm(sqInch):
    "convert sqare inches to square meters"
    return sqInch*0.00064516
def sqm2sqin(sqM):
    "convert sqare inches to square meters"
    return sqM/0.00064516

"""##### Composed properties ####################################"""
def ipK2siK(ipKValue):
    "convert K-value from [Btu/(hr ft F]] to [W/(m K)]"
    return ipKValue*1.730735
def siK2ipK(siKValue):
    "convert K-value from  [W/(m K)] to [Btu/(hr ft F]]"
    return siKValue/1.730735

"""##### Example conversions, for input 1 ####################################"""
if __name__=='__main__':
    #This runs if you run this file directly, shows usage
    x=1 #this is the input value for all the examples below
    print 'Conversion results for input value',x
    print ' * Temperature conversions:','  F2K',F2K(x),'  C2K',C2K(x),'  K2C',K2C(x)
    print ' * Massflow conversions:','  lbh2kgs',lbh2kgs(x),'  lbm2kgs',lbm2kgs(x),'  kgh2kgs',kgh2kgs(x)
    print ' * Volumetric flow conversions:', '  cfm2cms',cfm2cms(x), 'cms2cfm(x)', cms2cfm(x)
    print ' * Energy conversions:',  '  kJ2J',kJ2J(x),'  J2kJ',J2kJ(x)
    print ' * Power conversions','  BTUh2W',BTUh2W(x),'  kW2W',kW2W(x)
    print ' * Pressure conversions', '  kPa2Pa',kPa2Pa(x),'  MPa2kPa',MPa2kPa(x),'  MPa2Pa',MPa2Pa(x)
    print ' * Length conversions', '  in2m',in2m(x),'  ft2m',ft2m(x)
    print ' * Area conversions', '  sqin2sqm',sqin2sqm(x), 'sqm2sqin', sqm2sqin(x)
    print  '* Composed properties conversions', 'ipK2siK', ipK2siK(x),'siK2ipK',siK2ipK(x)
    print " * Test for automatic list and array handeling", unitconvert(x,sqin2sqm), unitconvert([x,2*x,3*x],sqin2sqm), unitconvert(array([x,2*x,3*x]),sqin2sqm)