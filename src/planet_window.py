import wx.aui
import logging
import db
import util
import event
import config
import image
import unit_list

import  wx.lib.scrolledpanel as scrolled

log = logging.getLogger('dclord')

def get_unit_name(carapace):
    return {
        1: 'shuttle',
        2: 'comm shuttle',
        6: 'shuttle',
        11: 'probe',
        21: 'transport'
        }.get(carapace, '')
        
def get_unit_name(carapace):
	if carapace == 11:
		return 'probe'
	return ''

class StackedObject(wx.Window):
	def __init__(self, parent, unit):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.units = []
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.text = wx.StaticText(self, wx.ID_ANY, 'x%d'%(len(self.units),))
		sz.Add( self.text )
		sz.Add( unit_list.UnitPrototypeWindow(self, unit) )
		
		self.sizer.Add(sz)
		self.SetSizer(self.sizer)
		self.sizer.Layout()

		self.add(unit)
	
	def add(self, unit):
		self.units.append(unit)
		self.update()
		
	def update(self):
		self.text.SetLabel('x%d'%(len(self.units),))
		self.sizer.Layout()
	
class PlanetWindow(scrolled.ScrolledPanel):
	def __init__(self, parent, coord = None, turn = None, show_units = False):
		scrolled.ScrolledPanel.__init__(self, parent, wx.ID_ANY, size=(200,300))
		
		self.turn = turn if turn else db.getTurn()
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)

		self.coord = coord
		
		if not self.coord:
			self.sizer.Layout()
			return
		
		owner_id = 0
		planet_name = ''
		for planet in db.planets(self.turn, ['x=%d'%(coord[0],), 'y=%d'%(coord[1],)], ('x','y','owner_id','o','e','m','t','s', 'name')):
			planet_name = planet.get('name', '')
			owner = planet['owner_id']
			if not owner:
				break
			owner_id = int(owner)
			
		
		owner_name = 'unknown'
		if owner_id > 0:
			for res in db.players(self.turn, ['player_id=%s'%(owner_id,)]):
				owner_name = res['name']
		else:
			owner_name = '<empty>'
		
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, '%s:%s %s'%(coord[0],coord[1], planet_name)))
		self.sizer.Add(wx.StaticText(self, wx.ID_ANY, owner_name))
		
		if show_units:
			self.addUnits()
		#self.sizer.Layout()
		
		#self.SetSizer( self.vbox )
		self.SetAutoLayout( 1 )
		self.SetupScrolling()
				
		self.Bind(wx.EVT_SIZE, self.onSize, self)
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()

		
	def addUnits(self):
		gunits = {}
		coord = self.coord
		for gu in db.garrison_units(self.turn, ['x=%d'%(coord[0],), 'y=%d'%(coord[1],)]):
			
			cl = int(gu['class'])
			if cl in gunits:
				gunits[cl].add(gu)
			else:
				uwindow = StackedObject(self, gu)
				gunits[cl] = uwindow
				self.sizer.Add( uwindow )
		
		

class UnitStackWindow(wx.Window):
	def __init__(self, parent, owner_id, unit):
		wx.Window.__init__(self, parent, wx.ID_ANY)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add( unit_list.UnitPrototypeWindow(self, unit) )
		self.SetSizer(self.sizer)
		self.sizer.Layout()
		
		self.units = {}
		self.user_name = db.getUserName(owner_id)

		self.text = wx.StaticText(self, wx.ID_ANY, '%d units, [%s]'%(len(self.units), self.user_name))
		self.sizer.Add(self.text)
		self.sizer.Layout()
		
		self.add(unit)
	
	def add(self, unit):
		self.units[unit['id']] = unit
		self.update()
		
	def update(self):
		self.text.SetLabel('%d units, [%s]'%(len(self.units), self.user_name))

class FleetWindow(scrolled.ScrolledPanel):
	def __init__(self, parent, coord = None, turn = None):
		scrolled.ScrolledPanel.__init__(self, parent, -1, size=(200,200))
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		
		self.tree = wx.TreeCtrl(self, wx.ID_ANY, style=wx.TR_HAS_BUTTONS)
		#self.alien_fleets = wx.TreeCtrl(self, wx.ID_ANY, style=wx.TR_HAS_BUTTONS)
		
		self.vbox.Add(self.tree, 1, wx.EXPAND)
		#self.vbox.Add(self.alien_fleets, 1, wx.EXPAND)

		self.setUnits(coord, turn)
		#self.setAlienUnits(coord, turn)
		
		self.SetSizer( self.vbox )
		self.SetAutoLayout( 1 )
		self.SetupScrolling()
				
		self.Bind(wx.EVT_SIZE, self.onSize, self)
				
	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
	
	def setUnits(self, coord, turn):
		units = {}
		if not coord:
			return
		
		self.tree.DeleteAllItems()
		image_list = wx.ImageList(40, 40)
		self.tree.AssignImageList(image_list)
		img_list_data = {}
		root = self.tree.AddRoot('Fleets')
		for user in db.users():
			user_id = user['id']
			tree_user = None
			for fleet in db.fleets(turn, util.filter_coord(coord) + ['owner_id=%s'%(user_id,)]):
				if not tree_user:
					tree_user = self.tree.AppendItem(root, user['name'])
				tree_fleet = self.tree.AppendItem(tree_user, fleet['name'])
				for unit in db.units(turn, ['fleet_id=%s'%(fleet['id'],)]):					
					proto = db.get_prototype(unit['class'], ('carapace', 'color', 'name'))
					obj_carp = int(unit['class']), int(proto['carapace']), int(proto['color'])
					img_item = None
					if obj_carp in img_list_data:
						img_item = img_list_data[obj_carp]
					else:
						img_item = image.add_image(image_list, obj_carp)
						img_list_data[obj_carp] = img_item
					name = proto['name']
					if not name:
						name = get_unit_name(int(proto['carapace']))
					self.tree.AppendItem(tree_fleet, name, image=img_item)
					
		for user in db.alien_players(turn):
			user_id = int(user['player_id'])
			tree_user = None
			for fleet in db.fleets(turn, util.filter_coord(coord) + ['owner_id=%s'%(user_id,)]):
				if not tree_user:
					tree_user = self.tree.AppendItem(root, user['name'])
				tree_fleet = self.tree.AppendItem(tree_user, fleet['name'])

				for unit in db.alienUnits(turn, ['fleet_id=%s'%(fleet['id'],)]):
					print 'get alient unit %s'%(unit,)
					obj_carp = unit['class'], int(unit['carapace']), int(unit['color'])
					img_item = None
					if obj_carp in img_list_data:
						img_item = img_list_data[obj_carp]
					else:
						img_item = image.add_image(image_list, obj_carp)
						img_list_data[obj_carp] = img_item

					self.tree.AppendItem(tree_fleet, get_unit_name(int(unit['carapace'])), image=img_item)
				
					
		self.tree.ExpandAll()
			
		
		#log.info('requesting fleet info at %s'%(coord,))
		#for fleet,unit in db.all_ownedUnits(turn, coord):
		#	cl = int(fleet['owner_id']), int(unit['class'])
		#	if cl in units:
		#		units[cl].add(unit)
		#	else:
		#		uwindow = UnitStackWindow(self, cl[0], unit)
		#		self.vbox.Add( uwindow)
		#		units[cl] = uwindow
		#for u in units.values():
		#	u.update()
	
	def setAlienUnits(self, coord, turn):
		units = {}
		if not coord:
			return
			
	
		#type of alien unit: (carapase, weight)
		#TODO: develop kind of alien Ship Unit Type, and evristicly fit ships into some of them
		# based on real unit id it's speed, transport capacity, invisibility ability and war attributes can be determined
		# it's name can be read when unit destroyed
		
		#  some values could be entered manually
		keys = {}
		for fleet,unit in db.all_alienUnits(turn, coord):
			key = int(fleet['owner_id']), int(unit['carapace']), int(unit['weight'])
			if key in keys:
				keys[key].add(unit)
			else:
				uwindow = UnitStackWindow(self, fleet['owner_id'], unit)
				keys[key] = uwindow
				uwindow.update()
				self.vbox.Add( uwindow)
		
class InfoPanel(wx.Panel):
	def __init__(self, parent):
		wx.Window.__init__(self, parent, -1, size=(120,200))			
		self.sizer = wx.BoxSizer(wx.VERTICAL)	
		self.SetSizer(self.sizer)
		self.sizer.Layout()
		self.pos = (0,0)
		self.Bind(wx.EVT_SIZE, self.onSize, self)
		self.turn = db.getTurn()

	def selectObject(self, evt):
		self.pos = evt.attr1
		log.info('object select %s, updating'%(self.pos,))
		self.update()

	def onSize(self, evt):
		if self.GetAutoLayout():
			self.Layout()
			
	def update(self, turn = None):
		if turn:
			self.turn = turn
		log.info('updating info panel, pos %s turn %d'%(self.pos, self.turn))
		self.sizer.DeleteWindows()
		self.sizer.Add( PlanetWindow(self, self.pos, self.turn, True) )
		self.sizer.Add( FleetWindow(self, self.pos, self.turn), 1, flag=wx.EXPAND | wx.ALL)
		self.sizer.Layout()
