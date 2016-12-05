import csv
import plotly
plotly.offline.init_notebook_mode()
import plotly.tools as tls
tls.set_credentials_file(username='gabox8888', api_key='sRqo9qh0pxO75YVceKfJ')
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
from plotly.offline.offline import _plot_html


import igraph
from igraph import *

class TreeNode(object):
    def __init__(self,node_id,stream_id,length,length_origin,x_start,y_start,x_end,y_end,is_dam,is_carp,lat,lon):
        self.node_id = node_id
        self.stream_id = stream_id
        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end
        self.dist_self = length
        self.dist_origin = length_origin
        self.is_dam = is_dam
        self.is_carp = is_carp
        self.lat = lat
        self.lon = lon
        self.longest_unin = 0
        self.children = []
    
    def add_child(self,child):
        self.children.append(child)
        
class TreeRiver(object):

    def __init__(self,csv_file):
        self.roots = []
        self.data_dictionary = []
        self.edgesX = [] 
        self.edgesY = [] 
        self.nodesX = [] 
        self.nodesY = []      
        self.damX = []
        self.damY = []   
        self.nodes = {}
        self.parse_data(csv_file)
        self.build_forest()
    
    def parse_data(self,csv_file):
        csv.register_dialect('mydialect',delimiter = ',',skipinitialspace = True)
        terminals = set()
        origins = set()
        dams = set()
        with open(csv_file, 'r') as mycsvfile:
            reader = csv.reader(mycsvfile, dialect='mydialect')
            first = True
            for row in reader:
                if not first : 
                    self.data_dictionary.append(row)
                    if row[11].isdigit():
                        origins.add(int(row[11]))
                    if row[7] == 'TRUE':
                        terminals.add(int(row[0]))
                    if row[12].isdigit():
                        dams.add(int(row[0]))
                first = False
        self.dams = list(dams) 
        self.origins = list(origins)
        self.terminals = list(terminals)

    def build_forest(self):
        for i in self.terminals:
            node_id = int(self.data_dictionary[i-1][0])
            stream_id = int(self.data_dictionary[i-1][1])
            length = float(self.data_dictionary[i-1][6])
            length_origin = float(self.data_dictionary[i-1][10])
            x_start = float(self.data_dictionary[i-1][2])
            y_start = float(self.data_dictionary[i-1][3])
            x_end = float(self.data_dictionary[i-1][4])
            y_end = float(self.data_dictionary[i-1][5])
            if self.data_dictionary[i-1][12].isdigit():
                is_dam = True
            else:
                is_dam = False
            if self.data_dictionary[i-1][13].isdigit():
                is_carp = True
                lat = x_start #float(self.data_dictionary[i-1][14])
                lon = y_start #float(self.data_dictionary[i-1][15])
            else:
                is_carp = False
                lat = x_start
                lon = y_start
            new_node = TreeNode(node_id,stream_id,length,length_origin,x_start,y_start,x_end,y_end,is_dam,is_carp,lat,lon)
            self.nodes[node_id] = new_node
            if self.data_dictionary[i-1][9] != 'NA':
                prev = int(self.data_dictionary[i-1][9])
                self.build_tree(prev,new_node)
        return

    def build_tree(self,prev_id,node):
        if prev_id in self.nodes:
            self.nodes[prev_id].add_child(node)
            return
        else:
            node_id = int(self.data_dictionary[prev_id-1][0])
            stream_id = int(self.data_dictionary[prev_id-1][1])
            length = float(self.data_dictionary[prev_id-1][6])
            length_origin = float(self.data_dictionary[prev_id-1][10])
            x_start = float(self.data_dictionary[prev_id-1][2])
            y_start = float(self.data_dictionary[prev_id-1][3])
            x_end = float(self.data_dictionary[prev_id-1][4])
            y_end = float(self.data_dictionary[prev_id-1][5])
            if self.data_dictionary[prev_id-1][12].isdigit():
                is_dam = True
            else:
                is_dam = False
            if self.data_dictionary[prev_id-1][13].isdigit():
                is_carp = True
                lat = x_start#float(self.data_dictionary[prev_id-1][14])
                lon = y_start#float(self.data_dictionary[prev_id-1][15])
            else:
                is_carp = False
                lat = x_start
                lon = y_start
            new_node = TreeNode(node_id,stream_id,length,length_origin,x_start,y_start,x_end,y_end,is_dam,is_carp,lat,lon)
            new_node.add_child(node)
            self.nodes[node_id] = new_node
        
        if prev_id in self.origins:
            return 
        else :
            prev = int(self.data_dictionary[prev_id-1][9])
            self.build_tree(prev,self.nodes[prev_id])
    
    def traverse(self,node):
        self.nodesX.append(node.x_start)
        self.nodesY.append(node.y_start)
        if node.is_dam:
            self.damX.append(node.x_start)
            self.damY.append(node.y_start)
        for c in node.children:
            self.edgesX += [node.x_start,c.x_start,None]
            self.edgesY += [node.y_start,c.y_start,None]
            self.traverse(c)
    
    def dist_to_next_dam(self,node,init):
        all_paths = []
        if (node.is_dam and init):
            return (1,[[node.node_id]])
        elif len(node.children) == 0:
            return (2,[[node.node_id]])
        is_inpath = 3
        for c in node.children:
            (in_path,paths) = self.dist_to_next_dam(c,True)
            if in_path  < 3:
                is_inpath = is_inpath if in_path > is_inpath else in_path
                for p in paths:
                    p+= [node.node_id]
            all_paths += paths
        return (is_inpath, all_paths)

    def traverse_all_dams(self,starting_node):
        all_paths = []
        (end_state,paths_to_next) = self.dist_to_next_dam(starting_node,False)
        if end_state < 3  and len(paths_to_next) > 0:
            for path in paths_to_next:
                all_paths.append((starting_node.node_id,path))
                if end_state == 1:
                    all_paths += self.traverse_all_dams(self.nodes[path[0]])
        return all_paths

    def all_dams_from_origins(self):
        all_paths = []
        for o in self.origins:
            all_paths+= self.traverse_all_dams(self.nodes[o])
        return all_paths

    def get_dist(self,path):
        dist = 0
        for n in path:
            dist += self.nodes[n].dist_self
        return dist
    
    def assign_dist(self,path):
        for n in path:
            dist = self.get_dist(path)
            if dist > self.nodes[n].longest_unin:
                self.nodes[n].longest_unin = dist
    
    def assign_all_dist(self,all_paths):
        for path in all_paths:
            self.assign_dist(path[1])
    
    def get_all_dist(self):
        all_dist = []
        for n in self.nodes:
            all_dist.append([self.nodes[n].node_id,self.nodes[n].longest_unin,self.nodes[n].lat,self.nodes[n].lon,self.nodes[n].is_carp])
        return all_dist


    def gen_tree_from_node(self,node):
        self.nodesX = []
        self.nodesY = []
        self.edgesX = []
        self.edgesY = []
        self.traverse(node)
        lines = go.Scatter(x=self.edgesX,
                   y=self.edgesY,
                   mode='lines',
                   line=dict(color='rgb(210,210,210)', width=1),
                   hoverinfo='none'
                   )
        dots = go.Scatter(x=self.nodesX,
                  y=self.nodesY,
                  mode='markers',
                  name='',
                  marker=dict(symbol='dot',
                                size=7, 
                                color='#6175c1',    #'#DB4551', 
                                line=dict(color='rgb(50,50,50)', width=1)
                                ),
                  opacity=0.8
                  )
        dams = go.Scatter(x=self.damX,
                  y=self.damY,
                  mode='markers',
                  name='',
                  marker=dict(symbol='dot',
                                size=7, 
                                color='#DB4551', 
                                line=dict(color='rgb(50,50,50)', width=1)
                                ),
                  opacity=0.8
                  )
        data=go.Data([lines, dots,dams])
        fig=dict(data=data)
        py.iplot(fig, filename='Tree-RiverGL')


def save_data(csvArr):
    with open("../data/lonegst_uninterruptedMiss_final.csv", "w",newline='') as f:
        writer = csv.writer(f,delimiter=',')
        writer.writerows(csvArr)
            

def main():
    TreeRivers = TreeRiver('../data/Miss_processed2.csv')
    # dam_id = TreeRivers.dams[200]
    # dam  = TreeRivers.nodes[dam_id]
    # node = TreeRivers.nodes[13563]
    # TreeRivers.gen_tree_from_node(node)
    # a = TreeRivers.dist_to_next_dam(node,False)
    a = TreeRivers.all_dams_from_origins()
    TreeRivers.assign_all_dist(a)
    save_data(TreeRivers.get_all_dist())
    # print(len(TreeRivers.nodes[58087].children))
    # print(a)

if __name__ == '__main__' : main()
