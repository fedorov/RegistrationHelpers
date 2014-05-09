import SimpleITK as sitk
import string, sys, os

# define root directory as the directory where all of the cases
# are located
rootDir = '/Users/fedorov/Documents/Projects/BRP/MR-US-registration'

# read both images
case = sys.argv[1]

# segmentation of the prostate in MR
segMRname = os.path.join(rootDir,'Case'+case,'case'+case+'-MR-label.nrrd')
# segmentation of the prostate in resampled US
segUSname = os.path.join(rootDir,'Case'+case,'case'+case+'_US_resampled-label.nrrd')

# output distance map of the segmentation in MR
dtMRname = os.path.join(rootDir,'Case'+case,'case'+case+'-MR-DT.nrrd')
# output distance map of the segmentation in US
dtUSname = os.path.join(rootDir,'Case'+case,'case'+case+'-US-DT.nrrd')

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

#sitk.WriteImage(cropped, '/Users/fedorov/Temp/cropped.nrrd')

'''
#print segMR.GetPixelIDValue()
#print segUS.GetPixelIDValue()

#size = union.GetBufferedRegion().size()
'''

# resample to isotropic grid
cropSize = cropped.GetSize()
cropSpacing = cropped.GetSpacing()
newSize = (int(cropSize[0]*cropSpacing[0]/0.2),int(cropSize[1]*cropSpacing[1]/0.2),int(cropSize[2]*cropSpacing[2]/0.2))
#print 'New size: ',newSize
#print 'Origin: ',segMR.GetOrigin()
#print 'Direction: ',segMR.GetDirection()
resample = sitk.ResampleImageFilter()
resample.SetOutputDirection(segMR.GetDirection())
# may be inconsistent with the origin of the input image, but the data should
# be all in the right place
newOrigin = union.TransformIndexToPhysicalPoint(bbMin)
resample.SetOutputOrigin(newOrigin)
resample.SetOutputSpacing((0.2,0.2,0.2))
resample.SetSize(newSize)
#resample.SetOutputStartIndex((0,0,0))
resample.SetInterpolator(sitk.sitkNearestNeighbor)

segMRresampled = resample.Execute(segMR)
print 'MR resampled'
segUSresampled = resample.Execute(segUS)
print 'US resampled'

# clean up the boundaries
segMRresampled = sitk.BinaryMorphologicalClosing(segMRresampled, 20)
print 'MR closed'
segUSresampled = sitk.BinaryMorphologicalClosing(segUSresampled, 20)
print 'US closed'

#sitk.WriteImage(segMRresampled, '/Users/fedorov/Temp/mr_closed.nrrd')
#print 'MR crop saved'
#sitk.WriteImage(segUSresampled, '/Users/fedorov/Temp/us_closed.nrrd')
#print 'US crop saved'

dtFilter = sitk.SignedMaurerDistanceMapImageFilter()
dtFilter.SetSquaredDistance(0)

segMRresampled = dtFilter.Execute(segMRresampled)
print 'MR DT done'
segUSresampled = dtFilter.Execute(segUSresampled)
print 'US DT done'

sitk.WriteImage(segMRresampled, dtMRname,1)
print 'MR DT saved'
sitk.WriteImage(segUSresampled, dtUSname,1)
print 'US DT saved'
