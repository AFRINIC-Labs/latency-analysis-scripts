# coding: utf-8

ccs = ['EG', 'BJ', 'CI', 'CV', 'GH', 'GM', 'GN', 'GW', 'AO', 'CF', 'CG', 'CM', 'GA', 'GQ', 'TD', 'BI', 'DJ', 'ER', 'ET', 'KM', 'BW', 'MA', 'SD', 'TN', 'LR', 'ML', 'MR', 'NE', 'NG', 'SL', 'SN', 'TG', 'ST', 'KE', 'MG', 'MU', 'MW', 'MZ', 'RE', 'RW', 'SC', 'SO', 'UG', 'LS', 'NA', 'SZ', 'ZA', 'DZ', 'EH', 'LY', 'BF', 'SH', 'CD', 'TZ', 'YT', 'ZM', 'ZW']
measurements = [
    '8459236', '8459161', '8459228', '8459135',
    '8459202', '8459184', '8459217', '8459172',
    '8459146', '8459168'
]

measurements = [
    '8459135', '8459202', '8459184', '8459217',
    '8459172', '8459146', '8459168']

from sys import stdout
from numpy import mean, median
import networkx as nx

def update_progress(progress):
    stdout.write("\rBuilding dict %.2f%%" % (1.0 * progress))
    stdout.flush()
    
def build_dict(results, weight_attribute='avg_rtt', origin_attribute='country_origin', destination_attribute='country_destination', min_squares=0):
    
    ccs = list(set([getattr(r, origin_attribute) for r in results] + [getattr(r, destination_attribute) for r in results]))
    N = len(ccs)
    region_dict = defaultdict(None)

    omitted = []
    for i, cc_o in enumerate(ccs):
        
        update_progress(100.0*i / N)
        
        rs = [r for r in results if getattr(r, origin_attribute) == cc_o]

        n = len(set([(getattr(r, origin_attribute), getattr(r, destination_attribute)) for r in results if getattr(r, origin_attribute) == cc_o]))
	if n < min_squares:
            omitted.append(cc_o)
            continue

        cc_dict = defaultdict(None)
        for cc_d in ccs:
            rtts = [getattr(r, weight_attribute) for r in rs if getattr(r, destination_attribute) == cc_d]
            if len(rtts) > 0:
                rtt = mean(rtts)
                cc_dict[cc_d] = rtt
        region_dict[cc_o] = cc_dict
    update_progress(100.0)
    if len(omitted) > 0:
	print
        print 'Omitted ', omitted
    return region_dict

from matplotlib import pyplot as plt
import numpy as np
import matplotlib
from datetime import datetime
from collections import defaultdict
import sys

def sort_from_dict(dictionary):
    def _sort(key):
        return dictionary[key]
    return _sort

def region_sort(key):
    return d_region[key]

import json

with open('data/restcountries.json') as f:
    restcountries = json.load(f)
    
def get_country_name(cc):
    for r in restcountries:
        if r['alpha2Code'] == cc:
            return r['name']
    return 'N/A'

def build_heatmap(
    dictionary, filename, plot_text=True, figsize=(12, 12), _max=400, _min=0, _ticks=10, banned=[], sort=None, title="", zero_colour=True, cmap=plt.cm.Blues, fontsize=8,
    yticklabels=None, xticklabels=None
):
    
#     if not DEBUG:
#         matplotlib.use('Agg')
    
#     build an empty matrix first
    origins = []
    destinations = []
    n = 0
    for o in sorted(dictionary):
        if o in banned: continue

        if o not in origins:
            origins.append(o)

        for d in sorted(dictionary[o]):
            if d in banned: continue

            if d not in destinations:
                destinations.append(d)

#     Apply sorting
    if sort != None:
        origins = sorted(origins, key=sort)
        destinations = sorted(destinations, key=sort)

    res = []
    n = 0
    N = len(origins) * len(destinations)
    for o in origins:
        for d in destinations:
            try:
                rtt = dictionary[o][d]
                if _max == 0 and _min == 0:  # unbounded
                    rtt = rtt
                elif _min < rtt < _max:
                    rtt = rtt
                else:
                    rtt = 0
            except:
                rtt = 0
            finally:
                res.append(rtt)
                    
                n += 1
                sys.stdout.write("\r Preparing Data (1/2) %.1f%%" % (100 * float(n / N)))
                sys.stdout.flush()

    print ""
    print "Painting matrix (2/2)"

    data = np.reshape(res, (len(origins), len(destinations)))
    fig, ax = plt.subplots(figsize=figsize, dpi=500)

    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]
    if zero_colour:
        cmaplist[0] = plt.cm.Greys(10)
    cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)
        
    # define the bins and normalize
#     if _max and _min:
    bounds = np.linspace(_min, _max, _max+1)
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    
    heatmap = ax.pcolor(data, cmap=cmap, norm=norm)
    
    if plot_text:
        for y in range(data.shape[0]):
            for x in range(data.shape[1]):
                plt.text(x + 0.5, y + 0.5, "%.0f" % data[y, x],
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontsize=fontsize
                         )

    # put the major ticks at the middle of each cell
    plt.ylim(0, len(origins))
    plt.xlim(0, len(destinations))
    ax.set_xticks(np.arange(len(destinations)) + .5, minor=False)
    ax.set_yticks(np.arange(len(origins)) + .5, minor=False)

    # want a more natural, table-like display
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    
    if xticklabels:
        print ["%s" % xticklabels[d] for d in destinations]
        ax.set_xticklabels(["%s" % xticklabels[d] for d in destinations], minor=False, fontsize=fontsize)
    else:
        ax.set_xticklabels(destinations, minor=False, fontsize=fontsize)
        
    if yticklabels:
        ax.set_yticklabels(["%s" % yticklabels[o] for o in origins], minor=False, fontsize=fontsize)
    else:
        ax.set_yticklabels(["%s (%s)" % (get_country_name(o), o) for o in origins], minor=False, fontsize=fontsize)
    
    if not title:
        title = "Africa latency heatmap\n"
        if _max > 0: title += "Maxed at %d ms\n" % _max
        if banned != []:
            title += "Countries excluded:"
            for b in banned:
                title += " %s" % b.encode('utf-8')
            title += "\n"
    
    plt.tight_layout()
    plt.title(title)
    
    plt.colorbar(
        heatmap,
        ticks=range(_min, int(_max)+_ticks, _ticks),
        boundaries=range(_min, int(_max)+_ticks, _ticks)
    )
    
    plt.savefig(filename + '.png', dpi=500, bbox_inches='tight')
    plt.savefig(filename + '.pdf', dpi=500, bbox_inches='tight')

    plt.show()


def build_graph(dictionary, inverse=False):
    G = nx.Graph()
    for d in dictionary:
        if d not in G.nodes(): G.add_node(d)
        for e in dictionary[d]:
            if e not in G.nodes(): G.add_node(e)
            weight = dictionary[d][e]
            if inverse: weight=weight
            else: weight=1.0/weight
            G.add_edge(d, e, weight=weight)
    return G

def clusterize(G):
    # import matplotlib.pyplot as plt
    import community
    
    partition = community.best_partition(G)

    #drawing
#     pos = nx.spring_layout(G)
    # pos=nx.drawing.nx_agraph.graphviz_layout(G)

    # size = float(len(set(partition.values())))
    # colors = range(int(size))
#   #   plt.figure(figsize=(13,13))
    # plt.axis("off")
    # for i, com in enumerate(set(partition.values())):
    #     list_nodes = [nodes for nodes in partition.keys()
    #                                 if partition[nodes] == com]
    #     nx.draw_networkx_nodes(G, pos, list_nodes, with_labels=True, node_color="#81B3C1")

    # nx.draw_networkx_edges(G, pos, width=.250)
    # nx.draw_networkx_labels(G, pos, font_size=12)
#   #   nx.draw_networkx_edge_labels(G, pos, edge_labels={k: "%.0f"%v for k, v in nx.get_edge_attributes(G,'weight').iteritems()})
    # plt.figure()
    # print "Graph G modularity: %.5f" % community.modularity(partition, G)
    # print "Graph G information:\n%s" % nx.info(G)
    # 
    # G_i = community.induced_graph(partition=partition, graph=G)
    # plt.axis("off")
    # pos = nx.spring_layout(G_i, iterations=5)
    # nx.draw_networkx_nodes(G_i, pos=pos, node_color="#81B3C1")
    # nx.draw_networkx_edges(G_i, pos=pos)
    # nx.draw_networkx_labels(G_i, pos=pos)
    # plt.figure()
    
    return partition

import geoip2.database as geo

def get_cc_from_ip_address(ip_address):
    
    cc = get_geo_info_from_ip_address(ip_address)
    if cc is None:
        return 'XX'

    return cc

def get_geo_info_from_ip_address(ip_address):
    try:
        reader = geo.Reader("data/GeoLite2-City.mmdb")
        return reader.city(ip_address)
    except Exception as e:
        return None

import json
from requests import get

def atlas_reader(url):
    return json.loads(get(url).text)





# cluster_speed = {'BF': 0, 'DJ': 0, 'BI': 1, 'BJ': 2, 'BW': 3, 'DZ': 2, 'TZ': 1, 'NA': 3, 'NG': 0, 'TN': 2, 'LR': 2, 'LS': 3, 'TG': 0, 'TD': 0, 'LY': 2, 'ZM': 3, 'CI': 0, 'CM': 0, 'EG': 2, 'ZA': 3, 'CD': 0, 'GA': 0, 'GM': 0, 'ZW': 3, 'GH': 0, 'MG': 2, 'MA': 2, 'KE': 1, 'ML': 2, 'MW': 3, 'SO': 0, 'SN': 2, 'SL': 0, 'SC': 2, 'UG': 1, 'MZ': 3, 'SD': 2}
# cluster_atlas = {'BF': 0, 'BI': 1, 'BJ': 0, 'BW': 2, 'DZ': 0, 'RW': 3, 'TZ': 0, 'CM': 0, 'NA': 4, 'NG': 0, 'TN': 0, 'RE': 0, 'LR': 0, 'LS': 5, 'TG': 0, 'LY': 0, 'ZM': 5, 'CI': 0, 'GQ': 0, 'EG': 0, 'MR': 0, 'CG': 0, 'ZA': 5, 'AO': 0, 'CD': 0, 'GA': 0, 'ET': 6, 'GM': 0, 'ZW': 5, 'CV': 0, 'GH': 0, 'SZ': 5, 'MG': 7, 'MA': 0, 'KE': 0, 'ML': 0, 'MU': 0, 'MW': 0, 'SO': 6, 'SN': 0, 'SL': 0, 'SC': 0, 'UG': 8, 'SD': 0, 'MZ': 5}
# cluster_names_speed = {
#     0: 'Western',
#     1: 'Eastern',
#     2: 'Northern',
#     3: 'Southern',
#     5: 'S. America',
#     6: 'N. America',
#     7: 'Europe',
#     8: 'Arabia',
#     9: 'Asia'
# }
# cluster_colors = {
#     0: '#00B1E2',
#     1: '#A8C023',
#     2: '#FF9D00',
#     3: '#DB3B29',
#     4: 'cyan',
#     5:'grey',
#     6:'grey',
#     7:'grey',
#     8:'grey',
#     9:'grey'
# }

import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def generate_graph(rs, inverse=False):

    dictionary = build_dict(rs)
    G = build_graph(dictionary, inverse=inverse)

    # remove inner latencies
    for e in G.copy().edges():
        if e[0] == e[1]:
            G.remove_edge(e[0], e[1])
    return G
