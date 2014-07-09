#!/usr/bin/python
class Unit(object):
	#static fields
	basisOrdering = ["m","kg","s","A","K","mol","cd"]

	def __init__(self, m, kg, s, A, K, mol, cd, scalar = 1):
		# initialize dimensions
		self.m = m
		self.kg = kg
		self.s = s
		self.A = A
		self.K = K
		self.mol = mol
		self.cd = cd
		self.scalar = scalar

	@property
	def dimensions(self):
		return [self.m, self.kg, self.s, self.A, self.K, self.mol, self.cd]

	
	def units(self):
		positives, negatives = [], []
		dims = self.dimensions
		for d in Unit.basisOrdering:
			q = self.__getattribute__(d)
			if q != 0:
				power = (lambda q: '' if q == 1 else '^' + str(q))(abs(q))
				(positives if q > 0 else negatives).append(d + power)

		bridge = " per " if negatives else ""
		return '-'.join(positives) + bridge + '-'.join(negatives)
	
	def compatibleWith(self, other):
		return self.dimensions == other.dimensions

	def __repr__(self):
		return str(self.scalar) + ' ' + self.units()

	def __eq__(self, other):
		return self.dimensions == other.dimensions and \
			   self.scalar == other.scalar

	def __add__(self, other):
		if self.compatibleWith(other):
			return Unit(*self.dimensions, scalar = self.scalar + other.scalar)
		else: 
			msg = self.units() + " is not compatible with " + other.units()
			raise UnitCompatibilityError(msg)

	def __mul__(self, other):
		if type(other) is not Unit:
			return self.__rmul__(other)
		dims = map(lambda x, y: x+y, self.dimensions, other.dimensions)
		return Unit(*dims, scalar = self.scalar*other.scalar)	

	def __rmul__(self, other):
		return Unit(*self.dimensions, scalar = other*self.scalar)
	
	def __div__(self, other):
		return self.__mul__(other**-1)

	def __pow__(self, p):
		return Unit(*map(lambda x: x*p, self.dimensions))

class Derived(Unit):
	#static fields
	derivedUnits = {
		"J"  : {"m" : 2, "kg" : 1, "s" : -2},
		"C"  : {"s" : 1, "A": 1},
		# "Hz" : {"s" : -1}
	}

	def __init__(self, u):
		Unit.__init__(self, *u.dimensions, scalar = u.scalar)

	def units(self):
		tokens = {}
		positives, negatives = [],[]
		dims = self.dimensions
		for d in Unit.basisOrdering:
			q = self.__getattribute__(d)
			if q != 0:
				tokens[d] = q

		for derivedUnit, baseUnits in Derived.derivedUnits.items():
			if all(base in tokens for base in baseUnits):
				for base in baseUnits:
					tokens[base] -= baseUnits[base]
					if tokens[base] == 0:
						tokens.pop(base)
				tokens[derivedUnit] = 1 + tokens.get(derivedUnit, 0)

		for token, val in tokens.items():
			power = (lambda q: '' if q == 1 else '^' + str(q))(abs(val))
			(positives if val > 0 else negatives).append(token+power)


		bridge = " per " if negatives else ""
		return '-'.join(positives) + bridge + '-'.join(negatives)

class UnitCompatibilityError(Exception): pass

def parse(expr):
	tokens = expr.split(" ")

mtr = Unit(1, 0, 0, 0, 0, 0, 0)
kg  = Unit(0, 1, 0, 0, 0, 0, 0)
sec = Unit(0, 0, 1, 0, 0, 0, 0)
amp = Unit(0, 0, 0, 1, 0, 0, 0)
amp = Unit(0, 0, 0, 1, 0, 0, 0)
deg = Unit(0, 0, 0, 0, 1, 0, 0)
mol = Unit(0, 0, 0, 0, 0, 1, 0)

def test_representation(u = amp):
	print u

def test_addition(u = sec):
	print u + u

def test_right_mul(u = mol):
	print 2*u

def test_left_mul(u = deg):
	print u*4

def test_exponentiation(u = mtr):
	print u**2

def test_division(u1 = mtr, u2 = sec):
	print u1/(2*u2)

def test_multiplying_unlike_units(u1 = amp, u2 = sec):
	print u1*u2
	print Derived(u1*u2)

def test_adding_unlike_units(u1 = sec, u2 = amp):
	try: 
		u1 + u2
	except UnitCompatibilityError as e:
		print e

def test_particle_energy():
	mass = 3*kg
	velocity = 12*mtr/sec
	kinetic_energy = 0.5 * mass * velocity**2

	gravity = 10 * mtr/sec**2
	height = 0.1*mtr
	potential_energy = mass * gravity * height

	energy = kinetic_energy + potential_energy

	print kinetic_energy
	print potential_energy
	print energy
	print Derived(energy)
	
def test_gas_constant_units():
	newton = kg * mtr/(sec**2)
	pascal = newton/mtr**2
	gas_constant_units = (pascal * mtr**3)/(mol * deg)

	print gas_constant_units
	print Derived(gas_constant_units)

if __name__ == '__main__':
	test_representation()
	test_addition()
	test_right_mul()
	test_left_mul()
	test_exponentiation()
	test_division()
	test_multiplying_unlike_units()
	test_adding_unlike_units()
	test_particle_energy()
	test_gas_constant_units()
