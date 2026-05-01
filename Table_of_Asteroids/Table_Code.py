# The 9 asteroids

# I'll be using a class to easily map out the different values associated to each asteroid

class Asteroid:
    def __init__(self, name, eccentricity, semi_major_axis, inclination_ecliptic):
        self.name = name
        self.e = eccentricity
        self.a = semi_major_axis
        self.i_eq = inclination_ecliptic