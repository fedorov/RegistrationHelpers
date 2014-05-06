#include <itkTransform.h>
#include <itkTransformFileReader.h>
#include <itkImageFileWriter.h>
#include <itkImageFileReader.h>
#include <itkBSplineDeformableTransform.h>
#include <itkAffineTransform.h>
#include <itkImageFileReader.h>
#include <itkImageRegionConstIterator.h>
#include <itkImageRegionConstIteratorWithIndex.h>
#include <itkIterativeInverseDeformationFieldImageFilter.h>
#include "TransformFiducialListCLP.h"
#include "itkOrientedImage.h"
#include "itkResampleImageFilter.h"
#include "itkNearestNeighborInterpolateImageFunction.h"
#include "itkVersorRigid3DTransform.h"

#include <vector>
#include <map>

#include <string.h>
#include <stdlib.h>

const int Dimension = 3;
typedef itk::OrientedImage<int, 3> ImageType;
typedef itk::TransformFileReader::Pointer TransformReaderPointer;
typedef itk::ImageFileWriter<ImageType> WriterType;
typedef itk::ImageFileReader<ImageType> ReaderType;
typedef itk::ImageRegionConstIterator<ImageType> ConstIterType;
typedef itk::ImageRegionConstIteratorWithIndex<ImageType> ConstIterWithIndexType;
typedef itk::BSplineDeformableTransform< double, Dimension , Dimension > 
BSplineDeformableTransformType;
typedef itk::AffineTransform< double, Dimension > AffineTransformType;
typedef itk::ResampleImageFilter<ImageType,ImageType,double> ResamplerType;
typedef itk::NearestNeighborInterpolateImageFunction<ImageType,double> NNType;
typedef itk::VersorRigid3DTransform<double> RigidTransformType;
typedef itk::Transform<ImageType> GenericTransformType;

typedef ImageType::PointType ImagePointType;

double DistanceBwPoints(ImageType::PointType, ImageType::PointType);

void ReadFiducials(const char* fname, std::vector<double*>&, std::vector<std::string>&);

int main( int argc , char * argv[] )
{
  PARSE_ARGS;


  TransformReaderPointer transformFile = itk::TransformFileReader::New() ;
  transformFile->SetFileName(transformationFile.c_str()) ;
  transformFile->Update() ;
  std::cerr << "Found "<< transformFile->GetTransformList() ->size() << " transforms from file" << std::endl;
  BSplineDeformableTransformType::Pointer BSplineTransform = NULL;
  AffineTransformType::Pointer affineTfm = NULL;
  RigidTransformType::Pointer rigidTfm = NULL;

  ReaderType::Pointer mReader = ReaderType::New();
  mReader->SetFileName(MovingImage.c_str());
  mReader->Update();

  ReaderType::Pointer rReader = ReaderType::New();
  rReader->SetFileName(ReferenceImage.c_str());
  rReader->Update();

  ImageType::Pointer mImage = mReader->GetOutput();
  ImageType::Pointer rImage = rReader->GetOutput();

  rImage->FillBuffer(0);
  mImage->FillBuffer(0);

  if ( transformFile->GetTransformList()->size() == 0  ) 
    { 
    std::cerr << "Error, the second transform does not exist." << std::endl;
    return EXIT_FAILURE;
    }

  if(transformFile->GetTransformList()->size() == 2)
    {

    if (!dynamic_cast<BSplineDeformableTransformType* > ( transformFile->GetTransformList()->front().GetPointer()))
      {       
      std::cerr << "Error, the second transform is not BSpline." << std::endl;
      return EXIT_FAILURE;
      }
    BSplineTransform = dynamic_cast<BSplineDeformableTransformType* > ( transformFile->GetTransformList()->front().GetPointer());
    std::cerr << "Read BSpline transform successful." << std::endl;
    transformFile->GetTransformList()->pop_front();
    if(!dynamic_cast<AffineTransformType*>(transformFile->GetTransformList()->front().GetPointer()))
      {
      std::cerr << "Error: expected affine transform first" << std::endl;
      return EXIT_FAILURE;
      }
    affineTfm = dynamic_cast<AffineTransformType*> (transformFile->GetTransformList()->front().GetPointer());

    BSplineTransform->SetBulkTransform(affineTfm);
    std::cout << "Transforms set" << std::endl;
    }
  else
    {
    if(!dynamic_cast<AffineTransformType*>(transformFile->GetTransformList()->front().GetPointer())){
      if(!dynamic_cast<RigidTransformType*>(transformFile->GetTransformList()->front().GetPointer())){
        std::cerr << "Input transform is neither rigid, nor affine!" << std::endl;
        return EXIT_FAILURE;
      } else {
        rigidTfm = dynamic_cast<RigidTransformType*> (transformFile->GetTransformList()->front().GetPointer());
      }
    } else {
      affineTfm = dynamic_cast<AffineTransformType*> (transformFile->GetTransformList()->front().GetPointer());
    }
  }


  std::vector<double*> inputFiducialList;
  std::vector<ImageType::PointType> outputFiducialList;
  std::map<int,double> fiducialId2Distance;
  ::size_t nFiducials = inputFiducialList.size(), i;
  std::vector<std::string> fiducialsNames;

  if(FiducialsFileName != ""){
    ReadFiducials(FiducialsFileName.c_str(), inputFiducialList, fiducialsNames);
    std::cout << "Read " << inputFiducialList.size() << " fiducials" << std::endl;
    outputFiducialList.resize(inputFiducialList.size());
    for(int i=0;i<inputFiducialList.size();i++)
      outputFiducialList[i] = new double[3];
  } else {
    std::cerr << "fiducials not specified!" << std::endl;
    return -1;
  }

  nFiducials = inputFiducialList.size();

  for(i=0;i<nFiducials;++i){
    ImageType::PointType pIn;
    ImageType::IndexType idx;

    pIn = inputFiducialList[i];

    fiducialId2Distance[i] = 10000.;

    mImage->FillBuffer(0);

    int searchRadius = 1;
    mImage->TransformPhysicalPointToIndex(pIn, idx);
    //std::cout << "Output index: " << idx[0] << ", " << idx[1] << ", " << idx[2] << std::endl;
    for(int ii=-searchRadius;ii<=searchRadius+1;ii++){
      for(int jj=-searchRadius;jj<=searchRadius+1;jj++){
        for(int kk=-searchRadius;kk<=searchRadius+1;kk++){
          ImageType::IndexType idx1;
          idx1[0] = idx[0]+ii;
          idx1[1] = idx[1]+jj;
          idx1[2] = idx[2]+kk;
          if(mImage->GetBufferedRegion().IsInside(idx1)){
            mImage->SetPixel(idx1, i+1);
          }
        }
      }
    }

    NNType::Pointer nnInterp = NNType::New();
    ResamplerType::Pointer resampler = ResamplerType::New();
    resampler->SetInput(mImage);
    if(BSplineTransform)
      resampler->SetTransform(BSplineTransform);
    else if(affineTfm)
      resampler->SetTransform(affineTfm);
    else if(rigidTfm)
      resampler->SetTransform(rigidTfm);
    else {
      std::cerr << "Unknown transform" << std::endl;
      return -1;
    }
  
    resampler->SetOutputParametersFromImage(rImage);
    resampler->SetInterpolator(nnInterp);  
    resampler->Update();

    ImageType::Pointer resampledImage = resampler->GetOutput();
    ConstIterWithIndexType iter(resampledImage, resampledImage->GetBufferedRegion());

    // 1) get bounding box of the voxels
    // 2) iterate over the bounding box in 0.1 mm increments to find the point
    // that maps to a closest point to the fiducial

    ImageType::PointType bbMin, bbMax;
    bbMin[0] = 1000;
    bbMin[1] = 1000;
    bbMin[2] = 1000;
    bbMax[0] = 0;
    bbMax[1] = 0;
    bbMax[2] = 0;

    // iterate over all non-zero voxels
    for(iter.GoToBegin();!iter.IsAtEnd();++iter){

      if(!iter.Get())
        continue;

      ImageType::IndexType iterIdx = iter.GetIndex();
      ImageType::PointType iterPt;
      resampledImage->TransformIndexToPhysicalPoint(iterIdx, iterPt);
      bbMin[0] = fmin(iterPt[0],bbMin[0]);
      bbMin[1] = fmin(iterPt[1],bbMin[1]);
      bbMin[2] = fmin(iterPt[2],bbMin[2]);

      bbMax[0] = fmax(iterPt[0],bbMax[0]);
      bbMax[1] = fmax(iterPt[1],bbMax[1]);
      bbMax[2] = fmax(iterPt[2],bbMax[2]);
    }

    //std::cout << "Bounding box: " << bbMin << ", " << bbMin << std::endl;

    double minDistance = 1000;
    ImageType::PointType closestPt;
    for(float x=bbMin[0];x<bbMax[0];x+=0.1){
      for(float y=bbMin[1];y<bbMax[1];y+=0.1){
        for(float z=bbMin[2];z<bbMax[2];z+=0.1){
          ImageType::PointType pPtFixed, pPtMoving;
          pPtFixed[0] = x;
          pPtFixed[1] = y;
          pPtFixed[2] = z;
          if(BSplineTransform)
            pPtMoving = BSplineTransform->TransformPoint(pPtFixed);
          else if(affineTfm)
            pPtMoving = affineTfm->TransformPoint(pPtFixed);
          else if(rigidTfm)
            pPtMoving = rigidTfm->TransformPoint(pPtFixed);

          double thisDistance = DistanceBwPoints(pPtMoving, inputFiducialList[i]);
          if(thisDistance<minDistance){
            minDistance=thisDistance;
            closestPt=pPtFixed;
          }
        }
      }
    } 

    outputFiducialList[i][0] = closestPt[0];
    outputFiducialList[i][1] = closestPt[1];
    outputFiducialList[i][2] = closestPt[2];
  }

  std::ofstream outFiducialFile(outputFile.c_str());
  for(i=0;i<nFiducials;i++){
    outFiducialFile << fiducialsNames[i] << ", " << -1.*outputFiducialList[i][0] << ", " 
      << -1.*outputFiducialList[i][1] << ", " << outputFiducialList[i][2] << ", 1, 1" << std::endl;
    std::cout << fiducialsNames[i] << ", " << -1.*outputFiducialList[i][0] << ", " 
      << -1.*outputFiducialList[i][1] << ", " << outputFiducialList[i][2] << ", 1, 1" << std::endl;
  }
  outFiducialFile.close();

  return EXIT_SUCCESS;
}

double DistanceBwPoints(ImageType::PointType p0, ImageType::PointType p1){
  return sqrt((p0[0]-p1[0])*(p0[0]-p1[0])+
              (p0[1]-p1[1])*(p0[1]-p1[1])+
              (p0[2]-p1[2])*(p0[2]-p1[2]));
}
