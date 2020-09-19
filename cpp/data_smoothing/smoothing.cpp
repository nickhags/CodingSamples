/*
 *  File:       smoothing.cpp
 *
 *  Description:
 *          Smooth points in a data file using point-averaging
 *
 *  Last Modified:  09-19-2020
 *  Copyright (C) 2020 hagertnl@miamioh.edu
 */

#include <string.h>

#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>

/*
 * Read row from line, append to vector
 *
 * Args:
 *    std::vector<double>& output: store values from line in vector
 *    std::string line: line from input file to process
 * Returns: int - number of columns read from file
 */
int readRow(std::vector<double>& output, std::string& line) {
  // reject empty line
  if (line.length() == 0) return 0;
  int cols = 0;
  double temp;
  std::istringstream lineIn(line);
  // read values from stringstream, push_back to vector
  while (lineIn >> temp) {
    output.push_back(temp);
    cols++;
  }
  return cols;
}

/*
 * Read row from line, append to vector
 *
 * Args:
 *    std::vector<double>& output: store values from line in vector
 *    std::string line: line from input file to process
 * Returns: None
 */
void readData(std::vector< std::vector<double> >& data, std::string& datafile) {
  std::string line;
  int numRows;
  std::ifstream is(datafile);
  // read line-by-line through file
  while (std::getline(is, line)) {
    // check for empty line or traditional comment line (begin with #)
    if (line.length() > 0 && line[0] != '#') {
      std::vector<double> v;
      // split row into vector
      numRows = readRow(v, line);
      // print warning if empty row is read (triggered by line with spaces)
      if (numRows == 0) {
        std::cerr << "Read line with 0 numbers: " << line << std::endl;
      } else {
        data.push_back(v);
      } // end if numRows == 0
    } // end if line.length() > 0, line[0] != '#'
  } // end while
  is.close();
}

/*
 * Read row from line, append to vector
 *
 * Args:
 *    std::vector<double>& output: store values from line in vector
 *    std::string line: line from input file to process
 * Returns: None
 */
void smooth(std::vector< std::vector<double> >& data, int factor, int col) {
  int count;
  // number of points on either side of point i to use to smooth
  int move = (factor - 1) / 2;
  double sd, sum;
  // store column-smoothed point
  std::vector<double> smoothed;
  // begin for-loop for each point
  for (int i = 0; i < data.size(); i++) {
    sum = 0;
    count = 0;
    // sum entries pulled from before entry i
    for (int back = i - 1; back >= 0 && (i - back) < move; back--) {
      sum += data[back][col];
      count++;
    }
    sum += data[i][col];
    count++;
    // sum entries pulled from after entry i
    for (int front = i + 1; front < data.size() && (front - i) < move;
          front++) {
      sum += data[front][col];
      count++;
    }
    // average the sum of entries
    sd = sum / count;
    // store result to be copied later
    smoothed.push_back(sd);
  }
  // copy over smoothed data
  for (int j = 0; j < smoothed.size(); j++) {
    data[j][col] = smoothed[j];
  }
}

/*
 * Read row from line, append to vector
 *
 * Args:
 *    std::vector<double>& output: store values from line in vector
 *    std::string line: line from input file to process
 * Returns: None
 */
void printResult(std::vector<std::vector<double>>& data) {
  for (int i = 0; i < data.size(); i++) {
    for (int j = 0; j < data[i].size(); j++) {
      std::cout << data[i][j] << " ";
    }
    std::cout << std::endl;
  }
}

int main(int argc, char **argv) {
  int smoothFactor, column;
  std::string datafile;
  // check for correct number of args
  if (argc != 4) {
    std::cerr << "Usage: ./smooth <smoothPoints> <datafile> <column>" << std::endl;
    return 1;
  }
  /*
   *  argument type-checking is ignored, since this script is used in highly
   *  controlled environments
   */
  // read in arguments #########################################################
  smoothFactor = std::stoi(argv[1]);
  if (smoothFactor % 2 == 0) {
    std::cout << "SmoothPoints should be an odd number" << std::endl;
    return 1;
  }
  datafile = argv[2];
  column = std::stoi(argv[3]);
  // end read arguments ########################################################
  std::vector<std::vector<double>> data;
  // read data from data file
  readData(data, datafile);
  // smooth specified column of data file
  smooth(data, smoothFactor, column);
  // print resulting data to std::cout (user redirects from command-line)
  printResult(data);
}
