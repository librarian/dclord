import logging
import unit
from loader import get_attr, get_attrs
from xml.dom import minidom

log = logging.getLogger('dclord')

class FleetBase:
	def __init__(self, id = None, name = None, owner_id = None, pos = None):
		self.id = id
		self.name = name
		self.pos = pos
		self.incoming_opts = None
		self.units = []
		
		self.flying = None
		self.tta = None
		self.from_pos = None

	def load_from_xml(self, node):
		self.name = get_attr(node, 'name', unicode)
		self.pos = get_attrs(node, 'x','y')
		# don't really need this
		#self.flying = get_attr(node, 'in-transit', bool)
		
		if self.flying:
			self.from_pos = get_attrs(node,'from-x', 'from-y')
			if not self.from_pos:
				log.error('unable to get start pos for flying fleet %s - %s, %s'%(self.pos, self.name))
			
	def save(self, node):
		set_attr(node, 'id', self.id)
		set_attrs(node, (x,y), 'x','y')
		set_attr(node, 'tta', self.tta)
		for u in self.units:
			u_node = node.createElement('u')
			u.save(u_node)
			node.appendChild(u_node)

class Fleet(FleetBase):
	def __init__(self, node):
		FleetBase.__init__(self)
		
		self.fly_opts = None
		self.hide_opts = None
		self.owner_id = None
		self.owner = None
		
		if node:
			self.load_from_xml(node)
		
	def load_from_xml(self, node):
		self.id = get_attr(node, 'id')
		self.tta = get_attr(node, 'tta')
		if self.tta > 0:
			self.flying = True		
		
		# load some flight specific info
		FleetBase.load_from_xml(self, node)
		
		for unit_node in node.getElementsByTagName('u'):
			u = unit.Unit(unit_node)
			u.fleet_id = self.id
			u.fleet = self
			self.units.append( u )
	
	def load(self, node):
		return self.load_from_xml(node)
		
	def set_proto(self, protos):
		for u in self.units:
			if not u.bc in protos:
				log.error('unknown unit %d proto %d'%(u.id,u.bc))
				continue
			u.proto = protos[u.bc]
		
		
class AlienFleet(FleetBase):
	def __init__(self, node):
		FleetBase.__init__(self)
		self.weight = None
		if node:
			self.load_from_xml(node)
				
	def load_from_xml(self, node):
		self.id = get_attr(node, 'fleet-id')
		self.weight = get_attr(node, 'sum-weight')
		self.owner_id = get_attr(node, 'player-id')
		self.tta = get_attr(node, 'turns-till-arrival')
		if self.tta > 0:
			self.flying = True
		FleetBase.load_from_xml(self, node)

		for unit_node in node.getElementsByTagName('allien-ship'):
			self.units.append( unit.AlienUnit(unit_node) )

	def save(self, node):
		Fleet.save(self, node)
		set_attr(node, 'sum-weight', self.weight)
		set_attr(node, 'player-id', self.owner_id)
	
	def load(self, node):
		return self.load_from_xml(node)
