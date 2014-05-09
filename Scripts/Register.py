import os,sys


case = sys.argv[1]

# directory with all cases
rootDir = '/Users/fedorov/Documents/Projects/BRP/MR-US-registration'
# path to the Slicer executable
Slicer = '/Users/fedorov/local/builds/Slicer4-Release/Slicer-build/Slicer'

dtMRname = os.path.join(rootDir,'Case'+case,'case'+case+'-MR-DT.nrrd')
dtUSname = os.path.join(rootDir,'Case'+case,'case'+case+'-US-DT.nrrd')
tfmName = os.path.join(rootDir,'Case'+case,'case'+case+'-bspline.tfm')
registeredName = os.path.join(rootDir,'Case'+case,'case'+case+'-MR_registered-bspline.nrrd')
MRname = os.path.join(rootDir,'MR_volumes','Case'+case+'-MR.nrrd')


fixed = dtUSname
moving = dtMRname
tfm = tfmName

cmd = Slicer+' --launch BRAINSFit --fixedVolume '+fixed+' --movingVolume '+moving+' --useRigid --useBSpline '
cmd += ' --useAffine --splineGridSize 3,3,3 --numberOfSamples 10000 --bsplineTransform '+tfm+' --costMetric MSE'
print cmd

os.system(cmd)

cmd = Slicer+' --launch ResampleScalarVectorDWIVolume --Reference '+fixed+' --transformationFile '+tfm
cmd += ' '+MRname+' '+registeredName

print cmd
os.system(cmd)
