from sys import stderr, argv, exc_info
from os.path import isfile
from functools import reduce


class MarsRover:

	# Map <current heading>:<new heading> for left and right spins
	spin_left =  { 'N':'W', 'E':'N', 'S':'E', 'W':'S' }
	spin_right = { 'N':'E', 'E':'S', 'S':'W', 'W':'N' }

	# Map <heading>:<coordinate offset> along x-axis and y-axis for a move
	delta_x = { 'N': 0, 'E':+1, 'S': 0, 'W':-1 }
	delta_y = { 'N':+1, 'E': 0, 'S':-1, 'W': 0 }

	def __init__(self, x = 0, y = 0, heading = 'N', rightmost = 0, uppermost = 0):
		self.x, self.y  = x, y
		self.heading = heading
		# Upper-right grid corner
		self.rightmost, self.uppermost = rightmost, uppermost

	def left(self):
		"""Spin left, 90 degrees counter-clockwise."""
		self.heading = MarsRover.spin_left[self.heading]
		return self

	def right(self):
		"""Spin right, 90 degrees clockwise."""
		self.heading = MarsRover.spin_right[self.heading]
		return self

	def inside(self, x, y):
		"""True if (x, y) is inside the valid rectangle."""
		return x >= 0 and x <= self.rightmost and y >=0 and y <= self.uppermost

	def crash(self, rover, x, y):
		"""True if (x, y) is already occupied by another rover."""
		return x == rover.x and y == rover.y

	def move(self, others = None):
		"""Move forward, check possible collision with others (array of other rovers)."""
		x = self.x + MarsRover.delta_x[self.heading]
		y = self.y + MarsRover.delta_y[self.heading]

		if not self.inside(x, y):
			houston("ignoring move, I would fall off a cliff!")
		elif others and reduce(lambda me, other: me or other, [self.crash(rover, x, y) for rover in others]):
			houston("ignoring move, another rover is blocking the way")
		else:
			self.x, self.y = x, y
		return self

def houston(error):
	print(f"rover says \"{error}\"", file = stderr)


def land(line, rightmost, uppermost):
	x, y, heading = line.split()
	x, y = int(x), int(y)
	if x > rightmost or y > uppermost or heading not in 'NESW':
		raise Exception("Invalid landing coordinates or heading")
	return x, y, heading


if __name__ == "__main__":
	if len(argv) > 1 and isfile(argv[1]):
		with open(argv[1]) as input:
			try:
				line = input.readline()  # Upper-right grid corner: X Y
				if line:
					rightmost, uppermost = map(lambda v: int(v), line.split())
				others = []
				line = input.readline().upper()  # Rover landing point: X Y HEADING
				while line:
					rover = MarsRover(*land(line, rightmost, uppermost), rightmost, uppermost)
					line = input.readline().upper()  # Move directives: LRM...
					if line:
						for c in line:
							if c == 'M':
								rover.move(others)
							elif c == 'L':
								rover.left()
							elif c == 'R':
								rover.right()
						print(rover.x, rover.y, rover.heading)
						others.append(rover)
					line = input.readline().upper()  # Rover landing point: X Y HEADING
			except:
				houston("Error on input line: %s, %s" % (line.rstrip(), exc_info()[1]))
