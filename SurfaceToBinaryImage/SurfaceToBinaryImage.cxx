#include "itkImageFileWriter.h"

#include "itkSmoothingRecursiveGaussianImageFilter.h"

#include "itkPluginUtilities.h"
#include "itkMeshFileReader.h"
#include "itkImageFileWriter.h"
#include "itkImageFileReader.h"
#include "itkTriangleMeshToBinaryImageFilter.h"
#include "itkSignedMaurerDistanceMapImageFilter.h"

#include "SurfaceToBinaryImageCLP.h"

// Use an anonymous namespace to keep class types and function names
// from colliding when module is used as shared object module.  Every
// thing should be in an anonymous namespace except for the module
// entry point, e.g. main()
//

int main( int argc, char * argv[] )
{
  PARSE_ARGS;

  const unsigned int Dimension = 3;

  typedef itk::Mesh<float, Dimension>           MeshType;
  typedef itk::MeshFileReader< MeshType >       ReaderType;

  ReaderType::Pointer  polyDataReader = ReaderType::New();

  polyDataReader->SetFileName(inputMeshName);

  try
    {
    polyDataReader->Update();
    std::cout << "Mesh read" << std::endl;
    }
  catch( itk::ExceptionObject & excp )
    {
    std::cerr << "Error during Update() " << std::endl;
    std::cerr << excp << std::endl;
    return EXIT_FAILURE;
    }

  typedef itk::Image<unsigned char, 3> ImageType;
  typedef itk::Image<float, 3> DistanceImageType;

  typedef itk::TriangleMeshToBinaryImageFilter< MeshType, ImageType >  TriangleImageType;

  TriangleImageType::Pointer imageFilter = TriangleImageType::New();

  imageFilter->SetInput( polyDataReader->GetOutput() );

  typedef itk::ImageFileReader<ImageType > ImageReaderType;
  ImageReaderType::Pointer imageReader = ImageReaderType::New();
  imageReader->SetFileName( inputImageName );
  imageReader->Update();

  ImageType::Pointer refImage = imageReader->GetOutput();

  imageFilter->SetSize(refImage->GetBufferedRegion().GetSize());
  imageFilter->SetOrigin(refImage->GetOrigin());
  imageFilter->SetSpacing(refImage->GetSpacing());
  imageFilter->SetDirection(refImage->GetDirection());
  imageFilter->Update();

  typedef itk::ImageFileWriter<ImageType > WriterType;

  WriterType::Pointer imageWriter = WriterType::New();
  imageWriter->SetInput(imageFilter->GetOutput() );
  imageWriter->SetFileName( outputImageName );
  imageWriter->UseCompressionOn();
  imageWriter->Update();

  return EXIT_SUCCESS;
}
