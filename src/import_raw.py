import xml.sax
import logging
import db
import serialization
import os
import os.path
import config
import util

log = logging.getLogger('dclord')

def getAttrs(src, conv):
	d={}
	for attr in src.keys():
		if attr in conv:
			d[conv[attr]]=src[attr]
	return d

#<dc user="" id="" turn="" turn-n="" worldsize="1000" 

class XmlHandler(xml.sax.handler.ContentHandler):
	
	NodeDC = 'dc'
	UserInfo = 'this-player'
	UserPlanets = 'user-planets'
	Planet = 'planet'
	Fleet = 'fleet'
	AlienFleet = 'allien-fleet'
	Unit = 'u'
	AlienUnit = 'allien-ship'
	Garrison = 'harrison'
	
	def __init__(self):
		xml.sax.handler.ContentHandler.__init__(self)
		self.user = {}
		self.read_level = None
		self.obj_id = None
		self.pos = None

	def startElement(self, name, attrs):
		if XmlHandler.NodeDC == name:
			self.user.update( getAttrs(attrs, {'user':'name', 'id':'id', 'turn-n':'turn'}) )
		elif XmlHandler.UserInfo == name:
			self.user.update( getAttrs(attrs, {'homeworldx':'hw_x', 'homeworldy':'hw_y', 'race-id':'race_id', 'login':"login"}) )
		elif XmlHandler.UserPlanets == name:
			self.read_level = XmlHandler.UserPlanets
		elif XmlHandler.Planet == name:
			data = getAttrs(attrs, {'x':'x', 'open':'is_open', 'owner-id':'owner_id', 'y':'y', 'name':'name','o':'o','e':'e','m':'m','t':'t','temperature':'t','s':'s','surface':'s'})
			if XmlHandler.UserPlanets == self.read_level:
				data['owner_id'] = self.user['id']
			db.setData('planet', data)
		elif XmlHandler.Fleet == name or XmlHandler.AlienFleet == name:
			fleetDict = {'x':'x','y':'y','id':'id','fleet-id':'id','player-id':'owner_id','from-x':'from_x','from-y':'from_y','name':'name', 'tta':'tta', 'hidden':'is_hidden'}
			data = getAttrs(attrs, fleetDict)
			self.obj_id = int(data['id'])
			if 'tta' in data:
				tta = int(data['tta'])
				if tta > 0:
					data['arrival_turn'] = int(self.user['turn'])+tta
				del data['tta']
			if name==XmlHandler.Fleet:
				data['owner_id'] = self.user['id']
			db.setData('fleet', data)
		elif XmlHandler.Garrison == name:
			self.pos = getAttrs(attrs, {'x':'x', 'y':'y'})
		elif XmlHandler.AlienUnit == name:
			data = getAttrs(attrs, {'class-id':'class', 'id':'id', 'weight':'weight', 'carapace':'carapace', 'color':'color'})
			data['fleet_id'] = self.obj_id
			db.setData('alien_unit', data)
		elif XmlHandler.Unit == name:
			data = getAttrs(attrs, {'bc':'class', 'id':'id', 'hp':'hp'})
			if self.obj_id:
				data['fleet_id'] = self.obj_id
				db.setData('unit', data)
			elif self.pos:
				data.update(self.pos)
				db.setData('garrison_unit', data)

	def endElement(self, name):
		if name==XmlHandler.UserInfo:
			db.setData('user', self.user)
		elif name==XmlHandler.Fleet or name==XmlHandler.AlienFleet:
			self.obj_id = None
		elif XmlHandler.Garrison == name:
			self.pos = None
			
def load_xml(path):
	p = xml.sax.make_parser()
	p.setContentHandler(XmlHandler())
	p.parse( open(path) )

def processRawData(path):
	log.debug('processing raw data %s'%(path,))
	xml_dir = os.path.join(config.options['data']['path'], config.options['data']['raw-xml-dir'])
	util.assureDirExist(xml_dir)
	base = os.path.basename(path)
	xml_path = os.path.join(xml_dir, base[:-3])
	util.unpack(path, xml_path)
	load_xml(xml_path)

def processAllUnpacked():
	xml_dir = os.path.join(config.options['data']['path'], config.options['data']['raw-xml-dir'])
	log.debug('processing all found data at %s'%(xml_dir,))
	at_least_one = False
	for file in os.listdir(xml_dir):
		if not file.endswith('.xml'):
			continue
		log.debug('loading %s'%(file,))
		load_xml( os.path.join(xml_dir, file) )
		at_least_one = True
	if at_least_one:
		serialization.save()
	