import SimpleITK as sitk
import string, sys, os

def resampleToIsotropic(inputImage, newSpacing):
  resample = sitk.ResampleImageFilter()
  resample.SetOutputDirection(segMR.GetDirection())
  resample.SetOutputOrigin(inputImage.GetOrigin())
  resample.SetOutputSpacing(newSpacing)
  resample.SetSize(newSize)
  resample.SetInterpolator(sitk.sitkNearestNeighbor)
  return resample.Execute()

def Smooth(inputImage, inputFileName, outputFileName):
  sitk.WriteImage(inputImage,inputFileName)

  smoother = '/Users/fedorov/local/builds/Slicer4-Release/Slicer-build/lib/Slicer-4.3/cli-modules/GaussianSmoothing'
  os.system(smoother+' '+inputFileName+' '+outputFileName)

  return sitk.ReadImage(outputFileName)

# define root directory as the directory where all of the cases
# are located
rootDir = '/Users/fedorov/Documents/Projects/BRP/MR-US-registration'

# read both images
case = sys.argv[1]
workingDir = os.path.join(rootDir,'Case'+case,'SmoothReg')
try:
  os.mkdir(workingDir)
except:
  print 'Looks like output dir exists!'

# segmentation of the prostate in MR
segMRname = os.path.join(rootDir,'Case'+case,'case'+case+'-MR-label.nrrd')
# segmentation of the prostate in resampled US
segUSname = os.path.join(rootDir,'Case'+case,'case'+case+'_US_resampled-label.nrrd')

# output distance map of the segmentation in MR
dtMRname = os.path.join(workingDir,'case'+case+'-MR-DT.nrrd')
# output distance map of the segmentation in US
dtUSname = os.path.join(workingDir,'case'+case+'-US-DT.nrrd')

segMR = sitk.ReadImage(segMRname)
segUS = sitk.ReadImage(segUSname)

cast = sitk.CastImageFilter()
cast.SetOutputPixelType(2)
segMR = cast.Execute(segMR)
segUS = cast.Execute(segUS)

#sitk.WriteImage(segMR,'/Users/fedorov/Temp/mr.nrrd',1)
#sitk.WriteImage(segUS,'/Users/fedorov/Temp/us.nrrd')

# get the bounding box of the images
union = segMR | segUS

size = union.GetSize()
print 'Input image size: ',size
'''
bbMin=(0,0,0)
bbMax=size
'''
bbMin = size
bbMax = (0,0,0)
for x in range(size[0]):
  for y in range(size[1]):
    for z in range(size[2]):
      if union.GetPixel(x,y,z):
        bbMin = (min(bbMin[0],x),min(bbMin[1],y),min(bbMin[2],z))
        bbMax = (max(bbMax[0],x),max(bbMax[1],y),max(bbMax[2],z))

print 'Min: ',bbMin,' Max: ',bbMax

# print 'What is the min? ',size[2],' and ',bbMax[2]+5
# add a margin and crop
bbMin = (max(0,bbMin[0]-30),max(0,bbMin[1]-30),max(0,bbMin[2]-5))
bbMax = (size[0]-min(size[0],bbMax[0]+30),size[1]-min(size[1],bbMax[1]+30),size[2]-(min(size[2],bbMax[2]+5)))

#sitk.WriteImage(union,'/Users/fedorov/Temp/union.nrrd')

# print 'Crop bounds: ',bbMin,' and ',bbMax

crop = sitk.CropImageFilter()
crop.SetLowerBoundaryCropSize(bbMin)
crop.SetUpperBoundaryCropSize(bbMax)
cropped = crop.Execute(union)

croppedMR = crop.Execute(segMR)
croppedUS = crop.Execute(segUS)

croppedMRfilename = os.path.join(workingDir,'case'+case+'-MR-cropped.nrrd')
croppedUSfilename = os.path.join(workingDir,'case'+case+'-US-cropped.nrrd')

smoothMRfilename = os.path.join(workingDir,'case'+case+'-MR-smooth.nrrd')
smoothUSfilename = os.path.join(workingDir,'case'+case+'-US-smooth.nrrd')

print 'Smoothing MR'
smoothMR = Smooth(croppedMR,croppedMRfilename,smoothMRfilename)
print 'Smoothing US'
smoothUS = Smooth(croppedUS,croppedUSfilename,smoothUSfilename)

dtFilter = sitk.SignedMaurerDistanceMapImageFilter()
dtFilter.SetSquaredDistance(0)

dtMR = dtFilter.Execute(smoothMR)
print 'MR DT done'
dtUS = dtFilter.Execute(smoothUS)
print 'US DT done'

sitk.WriteImage(dtMR, dtMRname,1)
print 'MR DT saved'
sitk.WriteImage(dtUS, dtUSname,1)
print 'US DT saved'
