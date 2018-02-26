#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 13:12:59 2018

@author: Sergey.Vinogradov@noaa.gov
"""
import os,sys
import argparse
import glob
import csdlpy
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import numpy as np
import datetime

#==============================================================================
def timestamp():
    print '[    ]'
    print '[Time]: ' + str(datetime.datetime.utcnow()) + ' UTC'
    print '[    ]'
    
#==============================================================================
def read_cmd_argv (argv):

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i','--hsofsDir',       required=True)
    parser.add_argument('-s','--stormID',        required=True)
    parser.add_argument('-z','--stormCycle',     required=True)    
    parser.add_argument('-o','--outputDir',      required=False)
    parser.add_argument('-t','--tmpDir',         required=False)
    parser.add_argument('-p','--pltCfgFile',     required=False)
    
    args = parser.parse_args()    
    print '[info]: hsofs_post.py is configured with :', args
    return args


#==============================================================================
def plot_maxele (maxele, tracks, advTrk, grid, coast, pp, titleStr, plotFile):
    
    # Default plotting limits, based on advisory track, first position
    lonlim = advTrk['lon'][0]-3.5, advTrk['lon'][0]+3.5
    latlim = advTrk['lat'][0]-0.5, advTrk['lat'][0]+6.5
    clim   = 0.,4.5
    try:
        lonlim = float(pp['Limits']['lonmin']),float(pp['Limits']['lonmax'])
        latlim = float(pp['Limits']['latmin']),float(pp['Limits']['latmax'])
        clim   = float(pp['Limits']['cmin']),  float(pp['Limits']['cmax'])
    except: #default limits, in case if not specified in ini file
        pass
    # Find maximal maxele value within the coord limits
    maxmax = np.max(maxele['value'][np.where( \
                   (lonlim[0] <= maxele['lon']) & (maxele['lon'] <= lonlim[1]) & \
                   (latlim[0] <= maxele['lat']) & (maxele['lat'] <= latlim[1]))])
    lonmax = maxele['lon'][np.where(maxele['value']==maxmax)]
    latmax = maxele['lat'][np.where(maxele['value']==maxmax)]
    print '[info]: max maxele = ',str(maxmax),'at ',str(lonmax),'x',str(latmax)
        
    f = csdlpy.plotter.plotMap(lonlim, latlim, fig_w=10., coast=coast)
    csdlpy.plotter.addSurface (grid, maxele['value'],clim=clim)
    
    csdlpy.plotter.plotTrack(advTrk, color='k',linestyle='--',markersize=1,zorder=11)
    if type(tracks) is list:
        for t in tracks:
            csdlpy.plotter.plotTrack(t,  color='r',linestyle='-',markersize=1,zorder=10)
    else:
        csdlpy.plotter.plotTrack(tracks, color='r',linestyle='-',markersize=1,zorder=10)
    
    plt.text (lonlim[0]+0.01, latlim[0]+0.01, titleStr )
    maxStr = 'MAX VAL='+ str(np.round(maxmax,1)) + ' '
    try:
        maxStr = maxStr + pp['General']['units'] +', '+ pp['General']['datum']
    except:
        pass # in case if there is a problem with pp
    plt.text (lonlim[0]+0.01, latlim[1]-0.1, maxStr)
        
    plt.plot(lonmax, latmax, 'ow',markerfacecolor='k',markersize=10)
    plt.plot(lonmax, latmax, 'ow',markerfacecolor='r',markersize=5)
    plt.text (lonmax,latmax, str(np.round(maxmax,1)),color='k',fontsize=10)
    csdlpy.plotter.save(titleStr, plotFile)
    plt.close(f) 
    
#==============================================================================
def run_post(argv):

    #Receive command line arguments
    args = read_cmd_argv(argv)

    #Locate hsofs path
    hsofsPath = args.hsofsDir +'hsofs.'+ args.stormCycle[:-2] +'/'
    if not os.path.exists(hsofsPath):
        print '[error]: hsofs path ' +hsofsPath+ ' does not exist. Exiting'
        return
    
    ens   = [] #Compile the list of available ensemble members
    fls   = glob.glob(hsofsPath + '*.surfaceforcing')    
    for f in fls:
        s = os.path.basename(f).split('.')
        ens.append(s[3] +'.'+ s[4] +'.'+ s[5] +'.'+ s[6])
        if s[5] == 'ofcl':
            advisoryTrackFile = f
    print '[info]: ', str(len(ens)),' hsofs ensembles detected: ', ens
           
    # Try to create tmp directory
    if not os.path.exists(args.tmpDir):
        print '[warn]: tmpDir='+args.tmpDir+' does not exist. Trying to mkdir.'
        try:
            os.makedirs(args.tmpDir)
        except:
            print '[warn]: cannot make tmpDir=' +args.tmpDir
            args.tmpDir = os.path.dirname(os.path.realpath(__file__))
            print '[warn]: look for your output in a current dir='+args.tmpDir

    # Read plotting parameters                   
    pp = csdlpy.plotter.read_config_ini (args.pltCfgFile)
    
    # Define local files
    gridFile      = os.path.join(args.tmpDir,'fort.14')
    coastlineFile = os.path.join(args.tmpDir,'coastline.dat')
    citiesFile    = os.path.join(args.tmpDir,'cities.csv')
    
    timestamp()
    # Download files if they do not exist
    csdlpy.transfer.download (      pp['Grid']['url'],      gridFile)
    csdlpy.transfer.download ( pp['Coastline']['url'], coastlineFile)
    csdlpy.transfer.download (    pp['Cities']['url'],    citiesFile)
    
    timestamp()
    grid   = csdlpy.adcirc.readGrid(gridFile)
    coast  = csdlpy.plotter.readCoastline(coastlineFile)
    advTrk = csdlpy.atcf.readTrack(advisoryTrackFile)
    
    # Max elevations
    tracks = []
    for e in ens:
        timestamp()

        maxeleFile = \
                hsofsPath + 'hsofs.' + args.stormID + '.' + \
                args.stormCycle + '.' + e + '.fields.maxele.nc'
        trackFile = \
                hsofsPath + 'hsofs.' + args.stormID + '.' + \
                args.stormCycle + '.' + e + '.surfaceforcing'

        maxele = csdlpy.estofs.getFieldsWaterlevel (maxeleFile, 'zeta_max')    
        track = csdlpy.atcf.readTrack(trackFile)        
        tracks.append( track )
        
        titleStr = 'HSOFS experimental ' + args.stormID + \
                '.' + args.stormCycle + '.' + e + ' MAX ELEV ' + \
                pp['General']['units'] + ', ' + pp['General']['datum']

        plotFile = args.outputDir + args.stormID +'.'+ args.stormCycle +'.'+ e +'.maxele.png'
        plot_maxele (maxele, track, advTrk, grid, coast, pp, titleStr, plotFile)
        csdlpy.transfer.upload(plotFile,'svinogradov@emcrzdm','/home/ftp/polar/estofs/hsofs/.')

    # Plot ens statistics: maxPS
    timestamp()
    psFile = hsofsPath + 'hsofs.' + args.stormID + '.' + \
                args.stormCycle + '.fields.maxPS.nc'
    maxPS = csdlpy.estofs.getFieldsWaterlevel (psFile, 'zeta_max')
    titleStr = 'HSOFS experimental ' + args.stormID + \
                '.' + args.stormCycle + '.maxPS MAX ELEV ' + \
                pp['General']['units'] + ', ' + pp['General']['datum']
    plotFile = args.outputDir + args.stormID +'.'+ args.stormCycle +'.maxPS.png'
    plot_maxele (maxPS, tracks, advTrk, grid, coast, pp, titleStr, plotFile)
    csdlpy.transfer.upload(plotFile,'svinogradov@emcrzdm','/home/ftp/polar/estofs/hsofs/.')

    # Plot ens statistics: rangePS
    timestamp()
    psFile = hsofsPath + 'hsofs.' + args.stormID + '.' + \
                args.stormCycle + '.fields.rangePS.nc'
    maxPS = csdlpy.estofs.getFieldsWaterlevel (psFile, 'zeta_max')
    titleStr = 'HSOFS experimental ' + args.stormID + \
                '.' + args.stormCycle + '.rangePS MAX ELEV ' + pp['General']['units']
    plotFile = args.outputDir + args.stormID +'.'+ args.stormCycle +'.rangePS.png'
    pp['Limits']['cmax'] = 2.0
    plot_maxele (maxPS, tracks, advTrk, grid, coast, pp, titleStr, plotFile)
    csdlpy.transfer.upload(plotFile,'svinogradov@emcrzdm','/home/ftp/polar/estofs/hsofs/.')

    # Read all time series for all ensembles
    cwl = []
    for e in ens:
        stationsFile = \
                hsofsPath + 'hsofs.' + args.stormID + '.' + \
                args.stormCycle + '.' + e + '.points.waterlevel.nc'
        cwl.append ( csdlpy.estofs.getPointsWaterlevel (stationsFile) )   
    print cwl    
        

    #7. Clean up temporary folder

#==============================================================================    
if __name__ == "__main__":

    timestamp()
    run_post (sys.argv[1:])
    timestamp()
    
    