#include <iostream>
#include <vector>
#include <string>
#include <fstream>

#include <string.h>
#include <stdlib.h>

void ReadFiducials(const char* fname, std::vector<double*> &v, std::vector<std::string> &names){
  
  std::ifstream fIn(fname);
  if(!fIn.is_open()){
    std::cerr << "Failed to open " << fname << std::endl;
    return;
  }
  while(fIn.good()){
    double *pt = new double[3];
    char line[255];
    fIn.getline(line,255);
    if(!strlen(line))
      break;
    if(line[0] == '#')
      continue;
    char* item = strtok(line, ",");
    if(item==NULL){
      std::cerr << "Corrupted fiducials file!" << std::endl;
      return;
    }
    names.push_back(item);
    std::cout << "Reading fiducial " << item << std::endl;
    pt[0] = -1.*atof(strtok(NULL,","));
    pt[1] = -1.*atof(strtok(NULL,","));
    pt[2] = atof(strtok(NULL,","));
    std::cout << "Read " << pt[0] << ", " << pt[1] << ", " << pt[2] << std::endl;
    v.push_back(pt);
  }
}
