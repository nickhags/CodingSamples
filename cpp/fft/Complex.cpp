/*
 *  File:       Complex.cpp
 *
 *  Description:
 *          Class to enable Complex number calculations and storage
 *
 *  Last Modified:  09-19-2020
 *  Copyright (C) 2020 hagertnl@miamioh.edu
 */

#include <cmath>

class Complex {
public:
  // real, imaginary components
  double r, i;

  // Constructors
  Complex() { Complex(0, 0); }
  Complex(double real, double imag) : r(real), i(imag) { }

  // perform Complex number multiplication
  Complex mult(Complex& c1) {
    double rc = this->r * c1.r - this->i * c1.i;
    double ic = this->r * c1.i + this->i * c1.r;
    Complex ret(rc, ic);
    return ret;
  }

  // perform Complex number addition
  Complex add(Complex& c1) {
    double rc = this->r + c1.r;
    double ic = this->i + c1.i;
    Complex ret(rc, ic);
    return ret;
  }

  // perform Complex number subtraction
  Complex sub(Complex& c1) {
    double rc = this->r - c1.r;
    double ic = this->i - c1.i;
    Complex ret(rc, ic);
    return ret;
  }

  // provide print method if preferred over overloaded<<
  void print(std::ostream& os) {
    os << this->r << " " << this->i << std::endl;
  }

  // overload stream insertion operator for Complex class
  friend std::ostream& operator<<(std::ostream& os, const Complex& c) {
    os << fabs(c.r) << " " << fabs(c.i);
    return os;
  }
};
