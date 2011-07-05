#!/usr/bin/env python
# encoding: utf-8

__author__ = "Telmo Menezes (telmo@telmomenezes.com)"
__date__ = "Jun 2011"


"""
Copyright (C) 2011 Telmo Menezes.

This program is free software; you can redistribute it and/or modify
it under the terms of the version 2 of the GNU General Public License 
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""


import sqlite3
from syn.core import *


class Net:
    def __init__(self, dbpath, verbose=False):
        self.verbose = verbose
        self.conn = sqlite3.connect(dbpath)
        self.cur = self.conn.cursor()
        self.create_db()

    def __del__(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def log(self, message):
        if self.verbose:
            print message

    def safe_execute(self, query):
        try:
            self.cur.execute(query)
            print('Executed query: %s' % query)
        except sqlite3.OperationalError:
            print('Failed query: %s' % query)

    def create_db(self):
        #create interval table
        self.safe_execute("CREATE TABLE interval (id INTEGER PRIMARY KEY)")
        self.safe_execute("ALTER TABLE interval ADD COLUMN pos INTEGER")
        self.safe_execute("ALTER TABLE interval ADD COLUMN ts_start INTEGER")
        self.safe_execute("ALTER TABLE interval ADD COLUMN ts_end INTEGER")
        
        # create node table
        self.safe_execute("CREATE TABLE node (id INTEGER PRIMARY KEY)")
        self.safe_execute("ALTER TABLE node ADD COLUMN label TEXT")
        self.safe_execute("ALTER TABLE node ADD COLUMN super_node INTEGER")
        self.safe_execute("ALTER TABLE node ADD COLUMN interval INTEGER")

        self.safe_execute("ALTER TABLE node ADD COLUMN ts_start INTEGER")
        self.safe_execute("ALTER TABLE node ADD COLUMN ts_end INTEGER")
        
        self.safe_execute("ALTER TABLE node ADD COLUMN in_degree INTEGER")
        self.safe_execute("ALTER TABLE node ADD COLUMN out_degree INTEGER")

        self.safe_execute("ALTER TABLE node ADD COLUMN in_pr REAL")
        self.safe_execute("ALTER TABLE node ADD COLUMN out_pr REAL")

        # create edge table
        self.safe_execute("CREATE TABLE edge (id INTEGER PRIMARY KEY)")
        self.safe_execute("ALTER TABLE edge ADD COLUMN orig INTEGER")
        self.safe_execute("ALTER TABLE edge ADD COLUMN targ INTEGER")
        self.safe_execute("ALTER TABLE edge ADD COLUMN ts_start INTEGER")
        self.safe_execute("ALTER TABLE edge ADD COLUMN ts_end INTEGER")

        # create indexes
        self.safe_execute("CREATE INDEX node_id ON node (id)")
        self.safe_execute("CREATE INDEX node_super_node ON node (super_node)")
        self.safe_execute("CREATE INDEX edge_id ON edge (id)")
        self.safe_execute("CREATE INDEX edge_orig ON edge (orig)")
        self.safe_execute("CREATE INDEX edge_orig_targ ON edge (orig, targ)")
        self.safe_execute("CREATE INDEX edge_ts ON edge (ts)")

    def load_net(self, min_ts=-1, max_ts=-1):
        net = create_net()

        self.cur.execute("SELECT id FROM node")
        
        nodes = {}
        for row in self.cur:
            nid = row[0]
            nodes[nid] = add_node_with_id(net, nid, 0)

        if min_ts >= 0:
            if max_ts >= 0:
                self.cur.execute("SELECT orig, targ, ts FROM edge WHERE ts>=%f AND ts<%f" % (min_ts, max_ts))
            else:
                self.cur.execute("SELECT orig, targ, ts FROM edge WHERE ts>=%f" % (min_ts))
        else:
            self.cur.execute("SELECT orig, targ, ts FROM edge")

        for row in self.cur:
            add_edge_to_net(net, nodes[row[0]], nodes[row[1]], int(row[2]))

        return net

    def add_node(self, super_node=-1, label=''):
        self.cur.execute("INSERT INTO node (super_node, label) VALUES (%d, '%s')" % (super_node, label))    
        return self.cur.lastrowid

    def add_edge(self, orig, targ, timestamp):
        self.cur.execute("INSERT INTO edge (orig, targ, ts) VALUES (%d, %d, %f)" % (orig, targ, timestamp))    
        return self.cur.lastrowid

    def min_edge_ts(self):
        self.cur.execute("SELECT min(ts) FROM edge WHERE ts > 0")
        row = self.cur.fetchone()
        return row[0]

    def max_edge_ts(self):
        self.cur.execute("SELECT max(ts) FROM edge WHERE ts > 0")
        row = self.cur.fetchone()
        return row[0]

    def divide_in_intervals(self, n_intvls):
        self.log('Dividing network in intervals.')
        min_ts = self.min_edge_ts()
        max_ts = self.max_edge_ts()
        interval = (max_ts - min_ts) / n_intvls
        cur_ts = min_ts + interval

        self.log('min ts: %d; max ts: %d; interval: %d; number of intervals: %d' % (min_ts, max_ts, interval, n_intvls))
        for i in range(n_intvls):
            self.log('generating interval %d' % i)
            self.cur.execute("INSERT INTO interval (pos, ts_start, ts_end) VALUES (?, ?, ?)", i, min_ts, cur_ts)
            int_id = self.cur.lastrowid
            syn_net = self.load_net(min_ts, cur_ts)

            node = net_first_node(syn_net)
            while node != 0:
                nid = node_id(node)
                in_degree = node_in_degree(node)
                out_degree = node_out_degree(node)
                degree = in_degree + out_degree

                if degree > 0:
                    self.cur.execute("INSERT INTO node (super_node, interval, in_degree, out_degree) VALUES (?, ?, ?, ?)", nid, int_id, in_degree, out_degree)

                node = node_next_node(node)

            destroy_net(syn_net)

            cur_ts += interval

    def compute_page_ranks(self):
        pass
