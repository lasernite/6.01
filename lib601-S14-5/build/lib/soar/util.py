import math

class Pose:
    """
    Represent the x, y, theta pose of an object in 2D space
    """
    x = 0.0
    y = 0.0
    theta = 0.0
    def __init__(self, x, y, theta):
        self.x = x
        """x coordinate"""
        self.y = y
        """y coordinate"""
        self.theta = theta
        """rotation in radians"""

    def point(self):
        """
        Return just the x, y parts represented as a C{util.Point}
        """
        return Point(self.x, self.y)

    def transform(self):
        """
        Return a transformation matrix that corresponds to rotating by theta 
        and then translating by x,y (in the original coordinate frame).
        """
        cosTh = math.cos(self.theta)
        sinTh = math.sin(self.theta)
        return Transform([[cosTh, -sinTh, self.x],
                          [sinTh, cosTh, self.y],
                          [0, 0, 1]])

    def transformPoint(self, point):
        """
        Applies the pose.transform to point and returns new point.
        @param point: an instance of C{util.Point}
        """
        cosTh = math.cos(self.theta)
        sinTh = math.sin(self.theta)
        return Point(self.x + cosTh * point.x - sinTh * point.y,
                     self.y + sinTh * point.x + cosTh * point.y)

    def transformDelta(self, point):
        """
        Does the rotation by theta of the pose but does not add the
        x,y offset. This is useful in transforming the difference(delta)
        between two points.
        @param point: an instance of C{util.Point}
        @returns: a C{util.Point}.
        """
        cosTh = math.cos(self.theta)
        sinTh = math.sin(self.theta)
        return Point(cosTh * point.x - sinTh * point.y,
                     sinTh * point.x + cosTh * point.y)

    def transformPose(self, pose):
        """
        Make self into a transformation matrix and apply it to pose.
        @returns: Af new C{util.pose}.
        """
        return self.transform().applyToPose(pose)

    def near(self, pose, distEps, angleEps):
        """
        @returns: True if pose is within distEps and angleEps of self
        """
        return self.point().isNear(pose.point(), distEps) and \
               nearAngle(self.theta, pose.theta, angleEps)

    def diff(self, pose):
        """
        @param pose: an instance of C{util.Pose}
        @returns: a pose that is the difference between self and pose (in
        x, y, and theta)
        """
        return Pose(self.x-pose.x,
                    self.y-pose.y,
                    fixAnglePlusMinusPi(self.theta-pose.theta))

    def distance(self, pose):
        """
        @param pose: an instance of C{util.Pose}
        @returns: the distance between the x,y part of self and the x,y
        part of pose.
        """
        return self.point().distance(pose.point())

    def inverse(self):
        """
        Return a pose corresponding to the transformation matrix that
        is the inverse of the transform associated with this pose.  If this
        pose's transformation maps points from frame X to frame Y, the inverse
        maps points from frame Y to frame X.
        """
        return self.transform().inverse().pose()

    def xytTuple(self):
        """
        @returns: a representation of this pose as a tuple of x, y,
        theta values  
        """
        return (self.x, self.y, self.theta)
    
    def __repr__(self):
        return 'pose:'+ prettyString(self.xytTuple())

def valueListToPose(values):
    """
    @param values: a list or tuple of three values: x, y, theta
    @returns: a corresponding C{util.Pose}
    """
    return apply(Pose, values)

class Point:
    """
    Represent a point with its x, y values
    """
    x = 0.0
    y = 0.0
    def __init__(self, x, y):
        self.x = x
        """x coordinate"""
        self.y = y
        """y coordinate"""

    def isNear(self, point, distEps):
        """
        @param point: instance of C{util.Point}
        @param distEps: positive real number
        @returns: true if the distance between C{self} and C{util.Point} is less
        than distEps
        """
        return self.distance(point) < distEps

    def distance(self, point):
        """
        @param point: instance of C{util.Point}
        @returns: Euclidean distance between C{self} and C{util.Point}
        than distEps
        """
        return math.sqrt((self.x - point.x)**2 + (self.y - point.y)**2)

    def magnitude(self):
        """
        @returns: Magnitude of this point, interpreted as a vector in
        2-space 
        """
        return math.sqrt(self.x**2 + self.y**2)

    def xyTuple(self):
        """
        @returns: pair of x, y values
        """
        return (self.x, self.y)

    def __repr__(self):
        return 'point:'+ prettyString(self.xyTuple())

    def angleTo(self, p):
        """
        @param p: instance of C{util.Point} or C{util.Pose}
        @returns: angle in radians of vector from self to p
        """
        dx = p.x - self.x
        dy = p.y - self.y
        return math.atan2(dy, dx)

    def add(self, point):
        """
        Vector addition
        """
        return Point(self.x + point.x, self.y + point.y)
    def __add__(self, point):
        return self.add(point)
    def sub(self, point):
        """
        Vector subtraction
        """
        return Point(self.x - point.x, self.y - point.y)
    def __sub__(self, point):
        return self.sub(point)
    def scale(self, s):
        """
        Vector scaling
        """
        return Point(self.x*s, self.y*s)
    def __rmul__(self, s):
        return self.scale(s)
    def dot(self, p):
        """
        Dot product
        """
        return self.x*p.x + self.y*p.y

class Transform:
    """
    Rotation and translation represented as 3 x 3 matrix
    """
    def __init__(self, matrix = None):
        if matrix == None:
            self.matrix = make2DArray(3, 3, 0)
            """matrix representation of transform"""
        else:
            self.matrix = matrix

    def inverse(self):
        """
        Returns transformation matrix that is the inverse of this one
        """
        ((c, ms, x),(s, c2, y), (z1, z2, o)) = self.matrix
        return Transform([[c, s, (-c*x)-(s*y)],
                          [-s, c, (s*x)-(c*y)],
                          [0, 0, 1]])

    def compose(self, trans):
        """
        Returns composition of self and trans
        """
        return Transform(mm(self.matrix, trans.matrix))

    def pose(self):
        """
        Convert to Pose
        """
        theta = math.atan2(self.matrix[1][0], self.matrix[0][0])
        return Pose(self.matrix[0][2], self.matrix[1][2], theta)

    def applyToPoint(self, point):
        """
        Transform a point into a new point.
        """
        # could convert the point to a vector and do multiply instead
        return self.pose().transformPoint(point)

    def applyToPose(self, pose):
        """
        Transform a pose into a new pose.
        """
        return self.compose(pose.transform()).pose()

    def __repr__(self):
        return 'transform:'+ prettyString(self.matrix)

def nearAngle(a1, a2, eps):
    """
    @param a1: number representing angle; no restriction on range
    @param a2: number representing angle; no restriction on range
    @param eps: positive number
    @returns: C{True} if C{a1} is within C{eps} of C{a2}.  Don't use
    within for this, because angles wrap around!
    """
    return abs(fixAnglePlusMinusPi(a1-a2)) < eps

def mm(t1, t2):
    """
    Multiplies 3 x 3 matrices represented as lists of lists
    """
    result = make2DArray(3, 3, 0)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                result[i][j] += t1[i][k]*t2[k][j]
    return result

def fixAnglePlusMinusPi(a):
    """
    A is an angle in radians;  return an equivalent angle between plus
    and minus pi
    """
    return ((a+math.pi)%(2*math.pi))-math.pi

def make2DArray(dim1, dim2, initValue):
    """
    Return a list of lists representing a 2D array with dimensions
    dim1 and dim2, filled with initialValue
    """
    result = []
    for i in range(dim1):
        result = result + [makeVector(dim2, initValue)]
    return result

def make2DArrayFill(dim1, dim2, initFun):
    """
    Return a list of lists representing a 2D array with dimensions
    dim1 and dim2, filled by calling initFun with every pair of
    indices 
    """
    result = []
    for i in range(dim1):
        result = result + [makeVectorFill(dim2, lambda j: initFun(i, j))]
    return result

def make3DArray(dim1, dim2, dim3, initValue):
    """
    Return a list of lists of lists representing a 3D array with dimensions
    dim1, dim2, and dim3 filled with initialValue
    """
    result = []
    for i in range(dim1):
        result = result + [make2DArray(dim2, dim3, initValue)]
    return result

def mapArray3D(array, f):
    """
    Map a function over the whole array.  Side effects the array.  No
    return value.
    """
    for i in range(len(array)):
        for j in range(len(array[0])):
            for k in range(len(array[0][0])):
                array[i][j][k] = f(array[i][j][k])

def makeVector(dim, initValue):
    """
    Return a list of dim copies of initValue
    """
    return [initValue]*dim

def makeVectorFill(dim, initFun):
    """
    Return a list resulting from applying initFun to values from 0 to
    dim-1
    """
    return [initFun(i) for i in range(dim)]

def prettyString(struct):
    """
    Make nicer looking strings for printing, mostly by truncating
    floats
    """
    if type(struct) == list:
        return '[' + ', '.join([prettyString(item) for item in struct]) + ']'
    elif type(struct) == tuple:
        return '(' + ', '.join([prettyString(item) for item in struct]) + ')'
    elif type(struct) == dict:
        return '{' + ', '.join([str(item) + ':' +  prettyString(struct[item]) \
                                             for item in struct]) + '}'
    elif type(struct) == float:
        return "%5.6f" % struct
    else:
        return str(struct)
