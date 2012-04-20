import db
import csv
import config
import os
import os.path
import logging

log = logging.getLogger('dclord')

def saveTable(table_name, keys, filters, out_name = None):
	out_file_path = out_name if out_name else table_name
	path = os.path.join(config.options['data']['path'], '%s.csv'%(out_file_path,))
	f = open(path, 'wt')
	writer = csv.DictWriter(f, keys)
	writer.writeheader()
	for p in db.items(table_name, filters, keys):
		writer.writerow(p)

def saveGeoPlanets():
	saveTable('planet', ('x','y','o','e','m','t','s'), None, 'planets_geo')

def savePlanets():
	saveTable('planet', ('x','y','owner_id','o','e','m','t','s'), ['owner_id is not null'], 'planets')

def saveFleets():
	saveTable('fleet', ('id', 'x','y','owner_id','from_x','from_y','arrival_turn', 'is_hidden'), None, 'fleets')
		
def saveUnits():
	saveTable('unit', ('id', 'hp','class', 'fleet_id'), [], 'units')

def saveGarrisonUnits():
	saveTable('garrison_unit', ('id', 'hp','class', 'x', 'y'), [], 'garrison_units')

def saveAlienUnits():
	saveTable('alien_unit', ('id', 'carapace','color','weight','fleet_id'), [], 'alien_units')

def save():
	saveGeoPlanets()
	savePlanets()
	saveFleets()
	saveUnits()
	saveGarrisonUnits()
	saveAlienUnits()

def loadTable(table_name, file_name):
	try:
		path = os.path.join(config.options['data']['path'], '%s.csv'%(file_name,))
		for p in csv.DictReader(open(path, 'rt')):
			db.setData(table_name, p)
	except IOError, e:
		log.error('failed to load table %s: %s'%(table_name, e))
		
def loadPlanets():
	loadTable('planet', 'planets')

def loadFleets():
	loadTable('fleet', 'fleets')
	
def loadUnits():
	loadTable('unit', 'units')

def loadGarrisonUnits():
	loadTable('garrison_unit', 'garrison_units')

def loadAlienUnits():
	loadTable('alien_unit', 'alien_units')

def load():
	loadPlanets()
	loadFleets()
	loadUnits()
	loadGarrisonUnits()
	loadAlienUnits()