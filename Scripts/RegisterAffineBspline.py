import os,sys,math

def readFiducials(fidName):
  f = open(fidName)
  fids = []
  for l in f:
    if l[0] == '#':
      continue
    fids.append([float(x) for x in l.split(',')[1:4]])
  return fids

def calculateErrors(fidName1,fidName2,errorName):
  f1 = readFiducials(fidName1)
  f2 = readFiducials(fidName2)
  fErrors = open(errorName,'w')
  for fId in range(len(f1)):
    fDiff = []
    fDiff.append(f1[fId][0]-f2[fId][0])
    fDiff.append(f1[fId][1]-f2[fId][1])
    fDiff.append(f1[fId][2]-f2[fId][2])

    error = math.sqrt(fDiff[0]*fDiff[0]+fDiff[1]*fDiff[1]+fDiff[2]*fDiff[2])
    print 'Error: ',error




def transformVolume(volumeIn, transform, volumeOut):
  ### done in Slicer!
  print 'Transforming ',volumeIn,' with ',transform,' to ',volumeOut
  volLogic = slicer.modules.volumes.logic()
  tfmLogic = slicer.modules.transforms.logic()
  fNames = vtk.vtkStringArray()
  fNames.InsertNextValue(volumeIn)
  vol = volLogic.AddArchetypeScalarVolume(volumeIn,'na',0,fNames)
  tfm = tfmLogic.AddTransform(transform, slicer.mrmlScene)
  vol.SetAndObserveTransformNodeID(tfm.GetID())
  tfmLogic.hardenTransform(vol)
  volLogic.SaveArchetypeVolume(volumeOut, vol)
  #slicer.mrmlScene.Clear()

def transformFiducials(fiducialsIn, transform, fiducialsOut):
  ### done in Slicer!
  fidLogic = slicer.modules.markups.logic()
  tfmLogic = slicer.modules.transforms.logic()
  fidId = fidLogic.LoadMarkupsFiducials(fiducialsIn, 'na')
  print 'Fiducials loaded:',fidId
  fid = slicer.mrmlScene.GetNodeByID(fidId)
  tfm = tfmLogic.AddTransform(transform, slicer.mrmlScene)
  fid.SetAndObserveTransformNodeID(tfm.GetID())
  tfmLogic.hardenTransform(fid)

  fidStorage = fid.GetStorageNode()
  fidStorage.SetFileName(fiducialsOut)
  fidStorage.WriteData(fid)
  #slicer.mrmlScene.Clear()

nArg = len(sys.argv)
case = sys.argv[nArg-1]

# directory with all cases
rootDir = '/Users/fedorov/Documents/Projects/BRP/MR-US-registration'
workingDir = os.path.join(rootDir,'Case'+case,'SmoothReg')
# path to the Slicer executable
Slicer = '/Users/fedorov/local/builds/Slicer4-Release/Slicer-build/Slicer'

dtMRname = os.path.join(workingDir,'case'+case+'-MR-DT.nrrd')
dtUSname = os.path.join(workingDir,'case'+case+'-US-DT.nrrd')
fiducialsMR = os.path.join(rootDir,'Annotation','Case'+case,'MR-fiducials.fcsv')
fiducialsUS = os.path.join(rootDir,'Annotation','Case'+case,'US-fiducials.fcsv')

affineTfmName = os.path.join(workingDir,'case'+case+'-affine.tfm')
bsplineTfmName = os.path.join(workingDir,'case'+case+'-bspline.tfm')

affineRegisteredNameDT = os.path.join(workingDir,'case'+case+'-MR_registered-affine-DT.nrrd')
bsplineRegisteredNameDT = os.path.join(workingDir,'case'+case+'-MR_registered-bspline-DT.nrrd')

affineRegisteredName = os.path.join(workingDir,'case'+case+'-MR_registered-affine.nrrd')
bsplineRegisteredName = os.path.join(workingDir,'case'+case+'-MR_registered-bspline.nrrd')

fidAffineRegisteredName = os.path.join(workingDir,'case'+case+'-MR_registered-affine-fid.fcsv')
fidBsplineRegisteredName = os.path.join(workingDir,'case'+case+'-MR_registered-bspline-fid.fcsv')
MRname = os.path.join(rootDir,'MR_volumes','Case'+case+'-MR.nrrd')

fixed = dtUSname
moving = dtMRname

cmd = Slicer+' --launch BRAINSFit --fixedVolume '+fixed+' --movingVolume '+moving+' --useRigid '
cmd += ' --useAffine --numberOfSamples 10000 --outputTransform '+affineTfmName+' --costMetric MSE'
print cmd
os.system(cmd)

transformVolume(MRname, affineTfmName, affineRegisteredName)
transformVolume(moving, affineTfmName, affineRegisteredNameDT)
transformFiducials(fiducialsMR, affineTfmName, fidAffineRegisteredName)

moving = affineRegisteredNameDT
cmd = Slicer+' --launch BRAINSFit --fixedVolume '+fixed+' --movingVolume '+moving+' '
cmd += ' --useBSpline --splineGridSize 3,3,3 --numberOfSamples 10000 --bsplineTransform '+bsplineTfmName+' --costMetric MSE'
print cmd

os.system(cmd)

transformVolume(affineRegisteredName, bsplineTfmName, bsplineRegisteredName)
transformVolume(affineRegisteredNameDT, bsplineTfmName, bsplineRegisteredNameDT)
transformFiducials(fidAffineRegisteredName, bsplineTfmName, fidBsplineRegisteredName)

errorInitial = os.path.join(workingDir,'case'+case+'-errors-initial.txt')
errorAffine = os.path.join(workingDir,'case'+case+'-errors-affine.txt')
errorBspline = os.path.join(workingDir,'case'+case+'-errors-bspline.txt')
print 'Initial errors'
calculateErrors(fiducialsUS,fiducialsMR,errorInitial)
print 'Affine errors'
calculateErrors(fiducialsUS,fidAffineRegisteredName,errorAffine)
print 'B-spline errors'
calculateErrors(fiducialsUS,fidBsplineRegisteredName,errorBspline)

