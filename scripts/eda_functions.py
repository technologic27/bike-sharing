def plot_stations_map(ax, stns, noText=False):
    # determine range to print based on min, max lat and lon of the data
    lat = list(stns['latitude'])
    lon = list(stns['longitude'])
    siz = [(2) ** (x / 1000) for x in stns['flow_count']]
    margin = 0.01  # buffer to add to the range
    lat_min = min(lat) - margin
    lat_max = max(lat) + margin
    lon_min = min(lon) - margin
    lon_max = max(lon) + margin

    # create map using BASEMAP
    m = Basemap(llcrnrlon=lon_min,
                llcrnrlat=lat_min,
                urcrnrlon=lon_max,
                urcrnrlat=lat_max,
                lat_0=(lat_max - lat_min) / 2,
                lon_0=(lon_max - lon_min) / 2,
                projection='lcc',
                resolution='f', )

    m.drawcoastlines()
    m.fillcontinents(lake_color='aqua')
    m.drawmapboundary(fill_color='aqua')
    m.drawrivers()

    # convert lat and lon to map projection coordinates
    lons, lats = m(lon, lat)

    # plot points as red dots
    if noText:
        ax.scatter(lons, lats, marker='o', color='r', zorder=5, alpha=0.6, s=1)
        return
    else:
        ax.scatter(lons, lats, marker='o', color='r', zorder=5, alpha=0.3, s=siz)

    # annotate popular stations
    for i in range(len(siz)):
        if siz[i] >= 2 ** 6:
            plt.text(lons[i], lats[i], text[i])