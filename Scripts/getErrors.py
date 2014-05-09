'''
Calculate errors between the corresponding figudials for registration TRE assessment
'''

import sys, string, math
import numpy

def readFiducials(fName):
  f = open(fName,'r')
  fid = []
  for l in f:
    if l[0] == '#':
      continue
    fid.append([float(x) for x in l.split(',')[1:4]])
  return fid

def fidDist(f1,f2):
  return math.sqrt((f1[0]-f2[0])*(f1[0]-f2[0])+(f1[1]-f2[1])*(f1[1]-f2[1])+(f1[2]-f2[2])*(f1[2]-f2[2]))

mrFidFile = sys.argv[1]
usFidFile = sys.argv[2]
regFidFile = sys.argv[3]

try:
  mrFid = readFiducials(mrFidFile)
  usFid = readFiducials(usFidFile)
  regFid = readFiducials(regFidFile)
except:
  sys.exit()

distBefore = numpy.array([fidDist(mrFid[x],usFid[x]) for x in range(len(mrFid))])
distAfter= numpy.array([fidDist(regFid[x],usFid[x]) for x in range(len(mrFid))])

print 'Distances before: ', distBefore 
print 'Mean (SD): ',distBefore.mean(),'(',distBefore.std(),')'
print 'Distances after: ', distAfter
print 'Mean (SD): ',distAfter.mean(),'(',distAfter.std(),')'
