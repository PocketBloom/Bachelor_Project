# The 9 asteroids

# I'll be using a class to easily map out the different values associated to each asteroid

class Asteroid_Table:
    def __init__(self, name, eccentricity, semi_major_axis, inclination_ecliptic, longitude_of_ascending_node, argument_of_periapsis):
        self.name = name
        self.e = eccentricity
        self.a = semi_major_axis
        self.i_eq = inclination_ecliptic

        #For the conversion to i_eq (inclination wrt the Sun's equator)
        self.node = longitude_of_ascending_node


# On my first try, I choose all the units which exist on the SSD.JPL Website:

asteroids = [
    Asteroid_Class("Eros", 0.22, 1.46),
    Asteroid_Class("Ceres", 0.08, 2.77)
]

class Asteroids_Initial_Conds:
    def __init__(self, name, ):
        self.name = name