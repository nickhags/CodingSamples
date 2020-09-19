/*
 *  File:       fourier_transform.cpp
 *
 *  Description:
 *          Implement a Discrete and Fast Fourier Transform,
 *          (DFT and FFT).
 *          The FFT uses the Cooley-Tukey algorithm
 *
 *  Last Modified:  09-19-2020
 *  Copyright (C) 2020 hagertnl@miamioh.edu
 */

#include <fstream>
#include <iostream>
#include <cmath>
#include <sstream>
#include <vector>

#include "Complex.cpp"

/*
 *  Read data from file by column
 *    Currently, can only read real-valued data, but method is structured to
 *    allow functionality for Complex inputs
 *
 *  Args:
 *    std::vector<Complex> data: vector of complexes to read data into
 *    std::string filename: filename to read data from
 *    int target: column number to read data from (1-based)
 *
 *  Returns: None
 */
void readData(std::vector<Complex>& data, std::string& filename, int target) {
  double holder;
  std::ifstream is(filename);
  std::string line;
  int col;
  // begin while loop to parse line-by-line
  while (std::getline(is, line)) {
    // ignore traditional comment lines
    if (line[0] == '#') {
      continue;
    } else {
      std::istringstream isstr(line);
      col = 1;
      // read data until reach desired column
      while (col < target) {
        isstr >> holder;
        col++;
      }
      // read desired column
      isstr >> holder;
      Complex toPush(holder, 0.0);
      data.push_back(toPush);
    }
  }
  is.close();
}

/*
 *  Perform Fast-Fourier Transform using Cooley-Tukey method
 *
 *  Args:
 *    std::vector<Complex> x: vector of time-domain complexes to transform
 *    std::vector<Complex> y: store result of FFT
 *
 *  Returns: None
 */
void fft(std::vector<Complex>& x, std::vector<Complex>& y) {
  // initialize variables for use in FFT
  double bigN = (double) x.size(), sumRE, sumRO, sumIE, sumIO, inCos, inSin;
  double adjsumRO, adjsumIO;
  // begin outer loop
  for (int k = 0; k < bigN / 2; k++) {
    // naming convention: sum[Real | Imag][Even | Odd]
    sumRE = 0.0;
    sumIE = 0.0;
    sumRO = 0.0;
    sumIO = 0.0;
    // begin inner loop
    for (int j = 0; j < bigN / 2; j++) {
      // inCos, inSin used to store constant value within loop
      inCos = cos(-4 * M_PI * k * j / bigN);
      inSin = sin(-4 * M_PI * k * j / bigN);
      // even number FFT
      sumRE += (x[2 * j].r * inCos - x[2 * j].i * inSin);
      sumIE += (x[2 * j].r * inSin + x[2 * j].i * inCos);
      // odd number FFT
      sumRO += (x[2 * j + 1].r * inCos - x[2 * j].i * inSin);
      sumIO += (x[2 * j + 1].r * inSin + x[2 * j].i * inCos);
    } // end inner loop
    // multiple Odd_k by e^(2*pi*i*k/N)
    adjsumRO = sumRO * cos(-2 * M_PI * k / bigN)
                - sumIO * sin(-2 * M_PI * k / bigN);
    adjsumIO = sumIO * sin(-2 * M_PI * k / bigN)
                + sumIO * cos(-2 * M_PI * k / bigN);
    // create complex objects to assign
    Complex odd(adjsumRO, adjsumIO);
    Complex even(sumRE, sumIE);
    // assign to result vector
    y[k] = even.add(odd);
    y[k + bigN / 2] = even.sub(odd);
  } // end outer loop
}

/*
 *  Perform Discrete Fourier Transform
 *
 *  Args:
 *    std::vector<Complex> x: vector of time-domain complexes to transform
 *    std::vector<Complex> y: store result of DFT
 *
 *  Returns: None
 */
void dft(std::vector<Complex>& x, std::vector<Complex>& y) {
  double bigN = (double) x.size();
  double sumR, sumI, inSin, inCos;
  // outer loop
  for (int k = 0; k < bigN; k++) {
    sumR = 0.0;
    sumI = 0.0;
    // begin inner loop
    for (int j = 0; j < bigN; j++) {
      // Euler's formula for e^(-2 * PI * i * j * k / N)
      inCos = cos(-2 * M_PI * k * j / bigN);
      inSin = sin(-2 * M_PI * k * j / bigN);
      sumR += (x[j].r * inCos - x[j].i * inSin);
      sumI += (x[j].r * inSin + x[j].i * inCos);
    } // end inner loop
    // set k'th position in result vector
    Complex toPush(sumR, sumI);
    y[k] = toPush;
  } // end outer loop
}

/*
 *  Add/subtract elements from data to ensure size is a power of
 *  2 (necessary for FFT)
 *
 *  Args:
 *    std::vector<Complex> x: vector of time-domain complexes to transform
 *    int bigN: user-specified value for size of x vector
 *    bool roundDown: if true, round down to nearest power of 2, else use bigN
 *      and/or round up by adding 0's
 *
 *  Returns: None
 */
void trimToPow2(std::vector<Complex>& x, int bigN, bool roundDown) {
  int xlen = x.size();
  if (!roundDown) {
    // check if user entered a bigN value, and if it is a power of 2
    if (bigN > 0 && (bigN & (bigN - 1)) != 0) {
      std::cerr << "Warning: specific size is not a power of 2" << std::endl;
    }
    // if user entered valid bigN value, trim x vector
    if (bigN > 0 && bigN < xlen) {
      x.erase(x.begin() + bigN, x.end());
    } else {
      std::cerr << "Warning: bigN either larger than data or not set: ";
      std::cerr << bigN << std::endl;
    }
    // get new x.size()
    xlen = x.size();
    if (xlen == 0) return;
    // append 0's to achieve vector-length as power of 2
    while ((xlen & (xlen - 1)) != 0) {
      std::cerr << "Non-power of 2 length, appending 0's" << std::endl;
      // default constructor initializes to 0's
      Complex c;
      x.push_back(c);
      xlen++;
    }
  } else {
    // if roundDown = true, use log2 to quickly get nearest power of 2 < xlen
    int newSz = pow(2, (int) log2(xlen));
    x.erase(x.begin() + newSz, x.end());
  }
}

/*
 *  Print usage string
 *  Args:
 *    None
 *
 *  Returns: None
 */
void printUsage() {
  std::string usage = "Usage: \n\t./prg\n";
  std::string opts = "\t-n <N>: number of samples to include in FFT (use power of 2)\n";
  opts += "\t-roundSize <dir>: [up | down] - rounding the size of array to power of 2\n";
  opts += "\t\tThe -n flag is ignored if this flag is set as down\n";
  opts += "\t-infile <infile>: input file (col 1 is assumed as x-values)\n";
  opts += "\t-outfile <outfile>: output file\n";
  opts += "\t-col <colNum>: column number for input data, default: 1\n";
  opts += "\t-step <stepsize>: step-size of x-values\n";
  opts += "\t-alg <algorithm>: fast | discrete, default: fast\n";
  usage += opts;
  std::cerr << usage << std::endl;
}

int main(int argc, char **argv) {
  // initialize variables for arguments
  std::string fname, ofname;
  int target = 1, bigN = -1;
  double timeshft = 1;
  bool fastF = true, roundSizeDown = false;
  // BEGIN Parse Args BLOCK ##################################################
  if (argc < 2) {
    printUsage();
    return 1;
  } else {
    try {
      int argnum = 1;
      std::string argstr;
      // parse arguments
      while (argnum < argc) {
        argstr = argv[argnum];
        if (argstr.compare("-infile") == 0) {
          argnum++;
          fname = argv[argnum];
        } else if (argstr.compare("-outfile") == 0) {
          argnum++;
          ofname = argv[argnum];
        } else if (argstr.compare("-alg") == 0) {
          argnum++;
          argstr = argv[argnum];
          if (argstr.compare("fast") == 0) {
            fastF = true;
          } else {
            fastF = false;
          }
        } else if (argstr.compare("-n") == 0) {
          argnum++;
          bigN = std::stoi(argv[argnum]);
        } else if (argstr.compare("-col") == 0) {
          argnum++;
          target = std::stoi(argv[argnum]);
        } else if (argstr.compare("-step") == 0) {
          argnum++;
          timeshft = std::stod(argv[argnum]);
        } else if (argstr.compare("-roundSize") == 0) {
          argnum++;
          argstr = argv[argnum];
          if (argstr.compare("up") == 0) {
            roundSizeDown = false;
          } else {
            roundSizeDown = true;
          }
        } else {
          std::cerr << "Unrecognized flag: " << argstr << std::endl;
          return 1;
        }
        argnum++;
      }
    } catch (...) {
      std::cerr << "Error processing arguments" << std::endl;
      printUsage();
    }
  }
  if (bigN != -1 && roundSizeDown) {
    std::cerr << "Warning: -n " << bigN << " ignored" << std::endl;
  }
  // END Parse Args BLOCK ####################################################
  std::vector<Complex> x;
  // read data file
  readData(x, fname, target);
  // trim to length power of 2 for FFT/DFT
  trimToPow2(x, bigN, roundSizeDown);
  // initialize FFT vector
  std::vector<Complex> y(x.size());
  // call Fast-Fourier or Discrete based on user input
  if (fastF) {
    fft(x, y);
  } else {
    dft(x, y);
  }
  // use this variable in algebraic operations with doubles
  double xrealSizeDbl = x.size();
  // use this variable for loop counters, etc
  int xrealSizeInt = xrealSizeDbl;
  // initialize frequency vector
  std::vector<double> freq;
  // populate frequency vector
  for (int i = 0; i < xrealSizeInt / 2; i++) {
    freq.push_back(i / (timeshft * xrealSizeDbl));
  }
  // print results to user-specified file
  std::ofstream os(ofname);
  os << "# Format: freq x.real x.imag y.real y.imag";
  os << std::endl;
  // skip zero-element
  for (int i = 1; i < xrealSizeInt / 2; i++) {
    y[i].r /= (double) xrealSizeDbl;
    y[i].i /= (double) xrealSizeDbl;
    os << freq[i] << " " << x[i] << " " << y[i] << std::endl;
  }
  os.close();
  return 0;
}
