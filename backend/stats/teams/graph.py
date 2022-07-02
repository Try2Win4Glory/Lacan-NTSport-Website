import numpy as np
import os
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import statistics
def update_team_graph(stattype, data, limit=-7):
    if limit == None:
        limit = -7
    else:
        limit = int(limit)
    fig = Figure()
    plt = fig.add_subplot(1, 1, 1)
    if stattype == '10m':
        races = data['races']
        races = races[limit:]
        ypoints = np.array(races)
        xpoints = []
        i = 0
        for r in races:
            xpoints.insert(0, i)
            i += 10
        plt.plot(xpoints, ypoints)
        plt.axis(xmin=max(xpoints), xmax=min(xpoints), ymin=min(ypoints)-4, ymax=max(ypoints)+4)
        plt.set_xlabel("Minutes Ago")
        plt.set_ylabel("Races")
        plt.autoscale(False)
        plt.ticklabel_format(style="plain", useOffset=False)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return output.getvalue()
    
    if stattype == 'hourlyraces':
        hourly = data['hourly']
        perhour = {
            #hournumber: [datapoints]
        }
        lastraces = 0
        for x in hourly:
            if lastraces == 0:
                lastraces = x[0]
                continue
            if perhour.get(str(x[1])) != None:
                perhour[x[1]].append(x[0]-lastraces)
            else:
                perhour[x[1]] = [x[0]-lastraces,]
            lastraces = x[0]
        for k,v in perhour.items():
            perhour[k] = statistics.mean(v)
        hours = []
        for k in perhour.keys():
            hours.append(int(k))
        hours.sort()
        newhours = []
        for h in hours:
            newhours.append(str(h))
        races = []
        for v in perhour.values():
            races.append(v)
        plt.bar(newhours, races)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return output.getvalue()