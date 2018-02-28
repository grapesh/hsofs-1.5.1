import csdlpy
import numpy as np
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt

#==============================================================================
def maxele (maxele, tracks, advTrk, grid, coast, pp, titleStr, plotFile):
    
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
def stations (ensFiles, pp, titleStr, plotPath):

    # Download master list
    masterListRemote = pp['Stations']['url']
    masterListLocal  = 'masterlist.tmp'
    csdlpy.transfer.download(masterListRemote, masterListLocal)
    master = csdlpy.obs.parse.stationsList (masterListLocal, ['NOSID','Name'])  
    print master
    
    # Collect all ensembles
    cwl = []
    for e in ensFiles:
        cwl.append(csdlpy.estofs.getPointsWaterlevel (e))
    nStations = len(cwl[0]['stations'])
    print '[info]: Plotting ' + str(nStations) + ' point stations.'
    
    for n in range(nStations):
        # Get data from master list
        station = cwl[0]['stations'][n]
        stationName = station
        for m in master:
            if station in m[0]:
                stationName = m[1]
                break
        print stationName
        
        plt.figure(figsize=(20,4.5))

        for e in range(len(ensFiles)):
            plt.plot(cwl[e]['time'], cwl[e]['zeta'][:,n], color='c',label='')
    
        plt.legend(bbox_to_anchor=(0.9, 0.35))
        plt.grid()
        plt.xlabel('DATE UTC')
        plt.ylabel('WL, meters LMSL')
        plt.title(stationName)
        plt.savefig(plotPath + str(n).zfill(3) + '.png')
        plt.close()
        
