#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python3-Skript zum Erzeugen des Zonefiles für knoten.freifunk-muesnterland.de
# Aufruf: create_db_knoten.py nodes_processed.json Beispiel-Zonefile > Ausgabe-Zonefile

import sys, re, json, time

# Our IPv6 prefix
prefix6 = '2a03:2260:115:'

if len(sys.argv) != 3:
    print("Aufruf: create_db_knoten.py nodes_processed.json Beispiel-Zonefile > Ausgabe", file=sys.stderr)
    sys.exit(2)
file_nodes = sys.argv[1]
file_db = sys.argv[2]

nodes_processed = {}
nodes_json = json.load(open(file_nodes, 'r'))
for node in nodes_json['nodes'].values():
    try:
        hostname = re.sub(r'[^a-z0-9\-]',"", node["nodeinfo"]["hostname"].lower())[0:63]
        for address in node["nodeinfo"]["network"]["addresses"]:
            if address.lower().startswith(prefix6):
                online = node['flags']['online']
                lastseen = node['lastseen']
                if hostname in nodes_processed:
# hostname already exists. Let the node win which fits better:
                    if not online and nodes_processed[hostname]['online']:
# online beats offline
                        continue
                    if not online and nodes_processed[hostname]['lastseen'] > lastseen:
# bigger lastseen wins if both are offline
                        continue
                    if (online or nodes_processed[hostname]['lastseen'] > lastseen) and online == nodes_processed[hostname]['online'] and nodes_processed[hostname]['address'] > address:
# otherwise bigger IP address wins
                        continue
                nodes_processed[hostname] = {'address': address, 'online': online, 'lastseen': lastseen}
    except:
        pass

print(
'''; zonefile for knoten.freifunk-muensterland.de.
$TTL    3600
@       IN      SOA     service.freifunk-muensterland.de. info.freifunk-muensterland.de. (
                     {}         ; Serial
                          86400         ; Refresh
                           7200         ; Retry
                        2419200         ; Expire
                          86400 )       ; Negative Cache TTL
'''.format(time.strftime("%s")), end=""
)
for line in open(file_db, 'r'):
    if re.search('IN\s*NS', line):
        print(line, end="")
for hostname in sorted(nodes_processed):
    print(hostname + "  AAAA  " + nodes_processed[hostname]['address'])
