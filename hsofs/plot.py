import csdlpy
import numpy as np
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from datetime import datetime
from datetime import timedelta as dt
import matplotlib.dates as mdates

#==============================================================================
def ensColorsAndLines (e, isMain=False):
    """
    color table for ensembles
    """
    cols = ['indianred','cyan','powderblue','darkseagreen','mediumpurple',
           'tomato','cornflowerblue','rosybrown', 'plum', 'burlywood', 'mediumturquoise',
           'lavender','teal','sienna', 'indigo']
    lin = 1
    if isMain:
        col = 'navy'
        lin = 3
    elif e < len(cols):
        col = cols[e]
    else: 
        col = 'gray'
    return col, lin

#==============================================================================
def maxele (maxele, tracks, advTrk, grid, coast, pp, titleStr, plotFile):
    
    # Default plotting limits, based on advisory track, first position
    lonlim = np.min(grid['lon']), np.max(grid['lon'])
    latlim = np.min(grid['lat']), np.max(grid['lat'])
    clim   = 0.,4.5

    try:
        lonlim = advTrk['lon'][0]-3.5, advTrk['lon'][0]+3.5
        latlim = advTrk['lat'][0]-0.5, advTrk['lat'][0]+6.5
    except:
        pass

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
    if isinstance(maxmax,(list,)):
        maxmax = maxmax[0]
    lonmax = maxele['lon'][np.where(maxele['value']==maxmax)]
    latmax = maxele['lat'][np.where(maxele['value']==maxmax)]
    if isinstance(lonmax,(list,)):
        lonmax = lonmax[0]
        latmax = latmax[0]    
    if maxmax is np.ma.masked:
        maxmax = np.nan     
    print '[info]: max maxele = ',np.str(maxmax),'at ', np.str(lonmax),'x', np.str(latmax)

    f = csdlpy.plotter.plotMap(lonlim, latlim, fig_w=10., coast=coast)
    csdlpy.plotter.addSurface (grid, maxele['value'],clim=clim)
    ax = f.gca()
    try:
        csdlpy.atcf.plot.track(ax, advTrk, color='k',linestyle='--',markersize=1,zorder=11)
        csdlpy.atcf.plot.size (ax, advTrk, 'neq64', color='k',zorder=11)
    except:
        print '[warn]: advTrack not plotted...'
    
    if type(tracks) is list:
        for t in tracks:
            csdlpy.atcf.plot.track(ax, t, color='r',linestyle='-',markersize=1,zorder=10)
            csdlpy.atcf.plot.size (ax, t, 'neq64',color='r',zorder=10)
    else:
        csdlpy.atcf.plot.track(ax, tracks, color='r',linestyle='-',markersize=1,zorder=10)
        csdlpy.atcf.plot.size (ax, tracks, 'neq64',color='r',zorder=10)
    
    plt.text (lonlim[0]+0.01, latlim[0]+0.01, titleStr )
    if not np.isnan(maxmax):
        maxStr = 'MAX VAL='+ np.str(np.round(maxmax,1)) + ' '
        try:
            maxStr = maxStr + pp['General']['units'] +', '+ pp['General']['datum']
        except:
            pass # in case if there is a problem with pp
        plt.text (lonlim[0]+0.01, latlim[1]-0.1, maxStr)
        
    plt.plot(lonmax, latmax, 'ow',markerfacecolor='k',markersize=10)
    plt.plot(lonmax, latmax, 'ow',markerfacecolor='r',markersize=5)
    plt.text (lonmax,latmax, str(np.round(maxmax,1)),color='k',fontsize=10)
    try:
        csdlpy.plotter.save(titleStr, plotFile)
    except:
        print '[error]: cannot save maxele figure.'

    plt.close(f) 

#==============================================================================
def maxwind (maxele, tracks, advTrk, grid, coast, pp, titleStr, plotFile):

    # Default plotting limits, based on advisory track, first position
    lonlim = advTrk['lon'][0]-3.5, advTrk['lon'][0]+3.5
    latlim = advTrk['lat'][0]-0.5, advTrk['lat'][0]+6.5
    clim   = 0.,50.
    try:
        lonlim = float(pp['Limits']['lonmin']),float(pp['Limits']['lonmax'])
        latlim = float(pp['Limits']['latmin']),float(pp['Limits']['latmax'])
        clim   = float(pp['Wind']['cmin']),  float(pp['Wind']['cmax'])
    except: #default limits, in case if not specified in ini file
        pass
    # Find maximal maxele value within the coord limits
    maxmax = np.max(maxele['value'][np.where( \
                   (lonlim[0] <= maxele['lon']) & (maxele['lon'] <= lonlim[1]) & \
                   (latlim[0] <= maxele['lat']) & (maxele['lat'] <= latlim[1]))])
    if isinstance(maxmax,(list,)):
        maxmax = maxmax[0]
    lonmax = maxele['lon'][np.where(maxele['value']==maxmax)]
    latmax = maxele['lat'][np.where(maxele['value']==maxmax)]
    if isinstance(lonmax,(list,)):
        lonmax = lonmax[0]
        latmax = latmax[0]
    if maxmax is np.ma.masked:
        maxmax = np.nan
    print '[info]: max maxwvel = ',np.str(maxmax),'at ', np.str(lonmax),'x', np.str(latmax)

    f = csdlpy.plotter.plotMap(lonlim, latlim, fig_w=10., coast=coast)
    csdlpy.plotter.addSurface (grid, maxele['value'],clim=clim)
    ax = f.gca()
    csdlpy.atcf.plot.track(ax, advTrk, color='k',linestyle='--',markersize=1,zorder=11)
    csdlpy.atcf.plot.size (ax, advTrk, 'neq64', color='k',zorder=11)

    if type(tracks) is list:
        for t in tracks:
            csdlpy.atcf.plot.track(ax, t, color='r',linestyle='-',markersize=1,zorder=10)
            csdlpy.atcf.plot.size (ax, t, 'neq64',color='r',zorder=10)
    else:
        csdlpy.atcf.plot.track(ax, tracks, color='r',linestyle='-',markersize=1,zorder=10)
        csdlpy.atcf.plot.size (ax, tracks, 'neq64',color='r',zorder=10)

    plt.text (lonlim[0]+0.01, latlim[0]+0.01, titleStr )
    if not np.isnan(maxmax):
        maxStr = 'MAX VAL='+ np.str(np.round(maxmax,1)) + ' '
        try:
            maxStr = maxStr + ' m/s' #pp['General']['units'] +', '+ pp['General']['datum']
        except:
            pass # in case if there is a problem with pp
        plt.text (lonlim[0]+0.01, latlim[1]-0.1, maxStr)

    plt.plot(lonmax, latmax, 'ow',markerfacecolor='k',markersize=10)
    plt.plot(lonmax, latmax, 'ow',markerfacecolor='r',markersize=5)
    plt.text (lonmax,latmax, str(np.round(maxmax,1)),color='k',fontsize=10)

    #add 10,20,30 nm radii to max val to aid RMW computation
    xiso, yiso = computeCircle(lonmax, latmax, 10.)
    plt.plot(xiso, yiso, color='w',ls='dashed',zorder=100)
    xiso, yiso = computeCircle(lonmax, latmax, 20.)
    plt.plot(xiso, yiso, color='w',ls='dashed',zorder=100)
    xiso, yiso = computeCircle(lonmax, latmax, 30.)
    plt.plot(xiso, yiso, color='w',ls='dashed',zorder=100)

    try:
        csdlpy.plotter.save(titleStr, plotFile)
    except:
        print '[error]: cannot save maxele figure.'

    plt.close(f)

#==============================================================================
def computeCircle(xo, yo, radius_nm):
    radius = radius_nm*1.852
    da   = np.pi/180.
    R    = 6370.
    xiso = []
    yiso = []
    for a in np.arange(0.,2.*np.pi, da):
        dx = 180./(np.pi*R)*radius/np.cos(np.radians(yo))
        dy = 180./(np.pi*R)*radius
        xiso.append(xo + dx*np.cos(a))
        yiso.append(yo + dy*np.sin(a))
    return xiso, yiso

#==============================================================================
def stations (ensFiles, ensNames, pp, titleStr, plotPath, args):

    clim = -0.5, 3.5
    try:
        clim = float(pp['Stations']['cmin']),  float(pp['Stations']['cmax'])
    except:
        pass
   
    # Download master list
    masterListRemote = pp['Stations']['url']
    masterListLocal  = 'masterlist.tmp'
    csdlpy.transfer.download(masterListRemote, masterListLocal)
    
    # Collect all ensembles
    cwl = []
    for e in ensFiles:
        cwl.append(csdlpy.estofs.getPointsWaterlevel (e))
    nStations = len(cwl[0]['stations'])
    print '[info]: Plotting ' + str(nStations) + ' point stations.'
    
    try:
        dates = datetime.strptime(pp['Dates']['start'],'%Y%m%d'), \
                datetime.strptime(pp['Dates']['finish'],'%Y%m%d')
        now   = dates[1]
    except:
        #now   = datetime.utcnow()
        #dates = (now-dt(days=1),now)
        dates  = (cwl[0]['time'][0]-dt(days=1), cwl[0]['time'][-1]+dt(days=1))
        now    = dates[1]

    # Plot limits
    xlim =    min(dates[0],  cwl[0]['time'][0] ),    \
              max(dates[-1], cwl[0]['time'][-1])
    ylim = clim[0], clim[1]

    for n in range(nStations):

        fullStationName = cwl[0]['stations'][n]
        print '[info]: plotting station ', fullStationName 
        # Get datums
        datums, floodlevels, nosid, stationTitle = \
            csdlpy.obs.parse.setDatumsFloodLevels (fullStationName, masterListLocal)

        # Stage the plot with datums and floodlevels
        fig, ax, ax2 = csdlpy.plotter.stageStationPlot (xlim, ylim, now, datums, floodlevels)
        plt.title(titleStr + ' @ ' + stationTitle, fontsize=9)

       # Get OBS
        obs   = csdlpy.obs.coops.getData(nosid,
                                         dates, product='waterlevelrawsixmin')
  
       # Plot OBS
        try:
            ax.plot(obs['dates'], obs['values'],
                    color='lime',label='OBSERVED',  linewidth=2.0)
        except:
            print '[warn]: cannot plot obs for ' + fullStationName
      
        # Plot Ensembles
        for e in range(len(ensFiles)):
            plotOfficial = False
            if 'ofcl' in ensFiles[e]:
                plotOfficial = True
            col, lin = ensColorsAndLines (e, plotOfficial)
            ax.plot(cwl[e]['time'], cwl[e]['zeta'][:,n], 
                      color=col, linewidth=lin, label=ensNames[e])

            if 'ofcl' in ensFiles[e] or len(ensFiles) < 3:
                peak_val = np.nanmax( cwl[e]['zeta'][:,n] )
                peak_dat = cwl[e]['time'][ np.argmax(cwl[e]['zeta'][:,n]) ]

                # Plot peak forecast value
                ax.text(peak_dat, 1.05*peak_val,
                        str(np.round(peak_val,1)) + "m (" +
                        str(np.round(3.28084*peak_val,1)) +"ft)", color='navy',fontsize=7)
                ax.plot([peak_dat, peak_dat], [ylim[0], peak_val], '--',color='navy')
                peak_str = str(peak_dat.hour).zfill(2) + ':' + str(peak_dat.minute).zfill(2) + 'z'
                ax.text(peak_dat+dt(hours=0.5), ylim[0], peak_str ,color='navy', fontsize=7)
                ax.plot(peak_dat, peak_val, 'o',markeredgecolor='navy',markerfacecolor='b')


        ax.legend(bbox_to_anchor=(0.8, 0.82), loc='center left',prop={'size':6})
        ax.text(xlim[0],ylim[1]+0.05,'NOAA / OCEAN SERVICE')
        ax.set_ylabel ('WATER LEVELS, meters MSL')
        ax2.set_ylabel('WATER LEVELS, feet MSL')
        ax.set_xlabel('DATE/TIME UTC')
        ax.grid(True,which='both')

        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n00:00'))
        ax.xaxis.set_minor_locator(MultipleLocator(0.5))

        ax.set_xlim (        xlim)
        ax.set_ylim (        ylim)
        ax2.set_ylim(3.28084*ylim[0], 3.28084*ylim[1])
        ax2.plot([],[])

        plt.tight_layout()

#        plt.title(stationName)
        figFile = plotPath + str(n+1).zfill(3) + '.png'
        plt.savefig(figFile)
        plt.close()
        csdlpy.transfer.upload(figFile, args.ftpLogin, args.ftpPath)

    csdlpy.transfer.cleanup()
        

