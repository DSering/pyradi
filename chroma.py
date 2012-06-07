#  $Id$
#  $HeadURL$

################################################################
# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/

# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
# License for the specific language governing rights and limitations
# under the License.

# The Original Code is part of the PyRadi toolkit.

# The Initial Developer of the Original Code is CJ Willers, 
# Portions created by CJ Willers are Copyright (C) 2006-2012
# All Rights Reserved.

# Contributor(s): ______________________________________.
################################################################
"""
This module provides functions for colour coordinate processing.

See the __main__ function for examples of use.
"""

#prepare so long for Python 3
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__version__= "$Revision$"
__author__= 'CJ Willers'
__all__= ['chromaticityforSpectralL']

import numpy

##############################################################################
##
def chromaticityforSpectralL(spectral,radiance,xbar,ybar,zbar):
    """ Calculate the CIE chromaticity coordinates for an arbitrary spectrum.
    
    Given a spectral radiance vector and CIE tristimulus curves, 
    calculate the CIE chromaticity coordinates. It is assumed that the 
    radiance spectral density is given in the same units as the spectral
    vector (i.e. [1/um] or [1/cm-1], corresponding to [um] or [cm-1] respectively.
    It is furthermore accepted that the tristimulus curves are also sampled at
    the same spectral intervals as the radiance. See 
    http://en.wikipedia.org/wiki/CIE_1931_color_space 
    for more information on CIE tristimulus spectral curves.
    
    Args:
        | spectral (np.array[N,] or [N,1]): spectral vector in  [um] or [cm-1].
        | radiance (np.array[N,] or [N,1]): the spectral radiance (any units), (sampled at spectral).
        | xbar (np.array[N,] or [N,1]): CIE x tristimulus spectral curve (sampled at spectral values).
        | ybar (np.array[N,] or [N,1]): CIE y tristimulus spectral curve (sampled at spectral values).
        | zbar (np.array[N,] or [N,1]): CIE z tristimulus spectral curve (sampled at spectral values).
        
    Returns:
        | [x,y,Y]: color coordinates x, y, and Y.
        
    Raises:
        | No exception is raised.
    """
    
    X=numpy.trapz(radiance.reshape(-1, 1)*xbar.reshape(-1, 1),spectral, axis=0)
    Y=numpy.trapz(radiance.reshape(-1, 1)*ybar.reshape(-1, 1),spectral, axis=0)
    Z=numpy.trapz(radiance.reshape(-1, 1)*zbar.reshape(-1, 1),spectral, axis=0)
    
    x=X/(X+Y+Z)
    y=Y/(X+Y+Z)
    
    return [x[0], y[0], Y[0]]



################################################################
##

if __name__ == '__init__':
    pass
    
if __name__ == '__main__':
        
    import math
    import sys

    import pyradi.planck as radiometry
    import pyradi.ryplot as ryplot
    import pyradi.ryfiles as ryfiles

    figtype = ".png"  # eps, jpg, png
    #figtype = ".eps"  # eps, jpg, png

    ## ----------------------- wavelength------------------------------------------
    #create the wavelength scale to be used in all spectral calculations, 
    # wavelength is reshaped to a 2-D  (N,1) column vector
    wavelength=numpy.linspace(0.38, 0.72, 350).reshape(-1, 1)

    ## ----------------------- colour tristimulus ---------------------------------
    # read csv file with wavelength in nm, x, y, z cie tristimulus values (x,y,z).  
    # return values are 2-D  (N,1) column vectors scaled and interpolated.
    xbar = ryfiles.LoadColumnTextFile('data/ciexyz31_1.txt', abscissaOut=wavelength, \
                    loadCol=[1], comment='%', delimiter=',', abscissaScale=1e-3)
    ybar = ryfiles.LoadColumnTextFile('data/ciexyz31_1.txt', abscissaOut=wavelength, \
                    loadCol=[2],  comment='%', delimiter=',', abscissaScale=1e-3)
    zbar = ryfiles.LoadColumnTextFile('data/ciexyz31_1.txt', abscissaOut=wavelength, 
                    loadCol=[3],  comment='%', delimiter=',', abscissaScale=1e-3)

    ## ------------------------ sources ------------------------------------------
    #build a 2-D array with the source radiance values, where each column 
    #represents a different source. Wavelength extends along columns.
    #Spectral interval for all source spectra is the same, which is 'wavelength'
    #Blackbody radiance spectra are calculated at the required wavelength intervals
    #Data read from files are interpolated to the required wavelength intervals 
    #Use numpy.hstack to stack columns horizontally.

    sources = ryfiles.LoadColumnTextFile('data/fluorescent.txt', abscissaOut=wavelength, 
                            comment='%', normalize=1)
    sources = numpy.hstack((sources, radiometry.planckel(wavelength,5900)))
    sources = numpy.hstack((sources, radiometry.planckel(wavelength,2850)))
    sources = numpy.hstack((sources, ryfiles.LoadColumnTextFile(\
                            'data/LowPressureSodiumLamp.txt', \
                            abscissaOut=wavelength, comment='%', normalize=1)))
    #label sources in order of appearance
    sourcesTxt=['Fluorescent', 'Planck 5900 K', 'Planck 2850 K', 'Sodium']

    #normalize the source data (along axis-0, which is along columns)
    #this is not really necessary for CIE xy calc, which normalizes itself.
    #It is however useful for plotting the curves.
    sources /= numpy.max(sources,axis=0) 

    ##------------------------- samples ----------------------------------------
    # read space separated file containing wavelength in um, then samples.
    # select the samples to be read in and then load all in one call!
    # first line in file contains labels for columns.
    samplesSelect = [1,2,3,8,10,11]

    samples = ryfiles.LoadColumnTextFile('data/samples.txt', abscissaOut=wavelength, \
                loadCol=samplesSelect,  comment='%')
    samplesTxt=ryfiles.LoadHeaderTextFile('data/samples.txt',\
                loadCol=samplesSelect, comment='%')
    print(samples.shape)
    print(wavelength.shape)

    ##------------------------- plot sample spectra ------------------------------
    smpleplt = ryplot.plotter(1, 1, 1)
    smpleplt.Plot(1, "Sample reflectance", r'Wavelength $\mu$m',\
                r'Reflectance', wavelength, samples, \
                ['r-', 'g-', 'y-','g--', 'b-', 'm-'],samplesTxt,0.5)
    smpleplt.SaveFig('SampleReflectance'+figtype)

    ##------------------------- plot source spectra ------------------------------
    srceplt = ryplot.plotter(2, 1, 1)
    srceplt.Plot(1, "Normalized source radiance", \
                r'Wavelength $\mu$m', r'Radiance', wavelength, sources, \
                ['k:', 'k-.', 'k--', 'k-'],sourcesTxt,0.5 )
    srceplt.SaveFig('SourceRadiance'+figtype)

    ##------------------------- plot cie tristimulus spectra ---------------------
    cietriplt = ryplot.plotter(3, 1, 1)
    cietriplt.Plot(1,"CIE tristimulus values",r'Wavelength $\mu$m',\
            r'Response', wavelength, xbar, 'k-', ['$\\bar{x}$'],0.5)
    cietriplt.Plot(1,"CIE tristimulus values",r'Wavelength $\mu$m',\
            r'Response', wavelength, ybar, 'k-.', ['$\\bar{y}$'],0.5)
    cietriplt.Plot(1,"CIE tristimulus values",r'Wavelength $\mu$m',\
            r'Response', wavelength, zbar, 'k--', ['$\\bar{z}$'],0.5)
    cietriplt.SaveFig('tristimulus'+figtype)


    ##------------------------- calculate cie xy for samples and sources ---------
    xs = numpy.zeros((samples.shape[1],sources.shape[1]))
    ys = numpy.zeros((samples.shape[1],sources.shape[1]))
    for iSmpl in range(samples.shape[1]):
        for iSrc in range(sources.shape[1]):
            [ xs[iSmpl,iSrc], ys[iSmpl,iSrc], Y]=\
                chromaticityforSpectralL(wavelength,\
                (samples[:,iSmpl]*sources[:,iSrc]).reshape(-1, 1) \
                ,xbar,ybar,zbar)
            #print('{0:15s} {1:15s} ({2:.4f},{3:.4f})'.format(samplesTxt[iSmpl], \
            #    sourcesTxt[iSrc], xs[iSmpl,iSrc], ys[iSmpl,iSrc]))

    ##---------------------- calculate cie xy for monochromatic  -----------------
    xm=numpy.zeros(wavelength.shape)
    ym=numpy.zeros(wavelength.shape)
    #create a series of data points with unity at specific wavelength
    for iWavel in range(wavelength.shape[0]):
        monospectrum=numpy.zeros(wavelength.shape)
        monospectrum[iWavel] = 1
        #calc xy for single mono wavelength point
        [xm[iWavel],ym[iWavel],Y]=chromaticityforSpectralL(wavelength,\
                monospectrum,xbar,ybar,zbar)
        #print('{0} um ({1},{2})'.format(wavelength[iWavel],xm[iWavel],ym[iWavel]))

    ##---------------------- plot chromaticity diagram  ---------------------------
    ciexyplt = ryplot.plotter(4, 1, 1)
    #plot monochromatic horseshoe
    ciexyplt.Plot(1,"CIE chromaticity diagram", r'x', r'y', \
            xm, ym, ['k-'])
    #plot chromaticity loci for samples
    styleSample=['r--', 'g-.', 'y-', 'g-', 'b-', 'k-']
    for iSmpl in range(samples.shape[1]):
        ciexyplt.Plot(1,"CIE chromaticity diagram", r'x', r'y', \
                xs[iSmpl],ys[iSmpl],[styleSample[iSmpl]] ,[samplesTxt[iSmpl]],0.5 )
    #plot source markers
    styleSource=['bo', 'yo', 'ro', 'go']
    for iSmpl in range(samples.shape[1]):
        for iSrc in range(sources.shape[1]):
            if iSmpl==0:
                legend=sourcesTxt[iSrc]
            else:
                legend=''
               
            ciexyplt.Plot(1,"CIE chromaticity diagram", r'x',r'y',\
                    xs[iSmpl,iSrc],ys[iSmpl,iSrc],[styleSource[iSrc]],legend,0.5 )

    ciexyplt.SaveFig('chromaticity'+figtype)