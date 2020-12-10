#!/usr/bin/env python3

import re
import os
import copy


################################################################################
## The LammpsDatafile class is used to read and store information from a
## formatted data file. These files are formatted for the LAMMPS molecular
## dynamics engine.
################################################################################
## Last modified: 11-24-2020
################################################################################
## Copyright (C) 2020 hagertnl@miamioh.edu
################################################################################


class LammpsDatafile:
    def __init__(self, fileName):
        self.headerLine = ""
        self.bounds = {}
        self.masses = {}
        self.paircs = {}
        self.bondcs = {}
        self.anglecs = {}
        self.dihedcs = {}
        self.improcs = {}
        self.bbcs = {}
        self.bacs = {}
        self.aacs = {}
        self.aatcs = {}
        self.ebtcs = {}
        self.mbtcs = {}
        self.bb13cs = {}
        self.atcs = {}
        self.atoms = []
        self.bonds = {}
        self.angles = {}
        self.diheds = {}
        self.impros = {}
        self.atom_len = 10
        self.arr_per = []
        self.dd = []
        self.read(fileName)

    def read(self, i_file_name):
        """ Read input LAMMPS datafile """
        # regex to match basic counts
        matchCounts = re.compile(r"\s*\d+\s*[atomsbndgledihrp]")
        inFile = open(i_file_name, 'r')
        count_atoms = 0
        count_bonds = 0
        # Read In Data File ----------------------------------------------------
        for line in inFile:
            if line == "\n":
                continue
            # if type counts
            elif "types" in line:
                continue
            # if statement for doing nothing
            elif "LAMMPS" in line:
                self.headerLine = line
            # if the basic counts
            elif bool(matchCounts.match(line)) and not 'types' in line:
                if 'atoms' in line:
                    count_atoms = int(line.split()[0])
                elif 'bonds' in line:
                    count_bonds = int(line.split()[0])
                continue
            # if low/high bounds
            elif "xlo" in line:
                desc = line.split()
                self.bounds["x"] = desc
                line = next(inFile)
                desc = line.split()
                self.bounds["y"] = desc
                line = next(inFile)
                desc = line.split()
                self.bounds["z"] = desc
            # Masses
            elif "Masses" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.masses[int(desc[0])] = desc
                    line = next(inFile)
            elif "Pair Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.paircs[int(desc[0])] = desc
                    line = next(inFile)
            elif "AngleAngle Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.aacs[int(desc[0])] = desc
                    line = next(inFile)
            elif "Dihedral Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.dihedcs[int(desc[0])] = desc
                    line = next(inFile)
            elif "Improper Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.improcs[int(desc[0])] = desc
                    line = next(inFile)
            elif "BondBond Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.bbcs[int(desc[0])] = desc
                    line = next(inFile)
            elif "Bond Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.bondcs[int(desc[0])] = desc
                    line = next(inFile)
            elif "BondAngle Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.bacs[int(desc[0])] = desc
                    line = next(inFile)
            elif "Angle Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.anglecs[int(desc[0])] = desc
                    line = next(inFile)
            elif "AngleAngleTorsion Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.aatcs[int(desc[0])] = desc
                    line = next(inFile)
            elif "EndBondTorsion Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.ebtcs[int(desc[0])] = desc
                    line = next(inFile)
            elif "MiddleBondTorsion Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.mbtcs[int(desc[0])] = desc
                    line = next(inFile)
            elif "BondBond13 Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.bb13cs[int(desc[0])] = desc
                    line = next(inFile)
            elif "AngleTorsion Coeffs" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.atcs[int(desc[0])] = desc
                    line = next(inFile)
            # if atoms
            elif "Atoms" in line:
                self.atoms = [0.0] * (count_atoms + 1) * self.atom_len
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = (line.split())
                    for i in range(0, len(desc)):
                        self.atoms[int(desc[0]) * self.atom_len + i] = \
                                                            float(desc[i])
                    line = next(inFile)
            # if bonds
            elif "Bonds" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.bonds[int(desc[0])] = desc
                    line = next(inFile)
            # if angles
            elif "Angles" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.angles[int(desc[0])] = desc
                    line = next(inFile)
            # if dihedrals
            elif "Dihedrals" in line:
                next(inFile)
                line = next(inFile)
                while not line == "\n":
                    desc = line.split()
                    self.diheds[int(desc[0])] = desc
                    line = next(inFile)
            # if impropers
            elif "Impropers" in line:
                next(inFile)
                line = next(inFile)
                try:
                    while not line == "\n":
                        desc = line.split()
                        self.impros[int(desc[0])] = desc
                        line = next(inFile)
                except StopIteration:
                    pass
            # end of inFile file loop
        inFile.close()
        self.dd = [float(self.bounds['x'][1]) - float(self.bounds['x'][0]),\
                   float(self.bounds['y'][1]) - float(self.bounds['y'][0]),\
                   float(self.bounds['z'][1]) - float(self.bounds['z'][0])]
        self.getPeriodics()

    def getAllTypeStrings(self):
        """ Set all type strings for all forcefield params  """
        for key in range(1, len(self.bondcs) + 1):
            if not '#' in self.bondcs[key]:
                for bondKey in range(1, len(self.bonds) + 1):
                    if int(self.bonds[bondKey][1]) == key:
                        # find atom type strings
                        atom1 = int(self.bonds[bondKey][2])
                        atom2 = int(self.bonds[bondKey][3])
                        atom1Type = int(self.atoms[atom1][2])
                        atom2Type = int(self.atoms[atom2][2])
                        typeStr = str(self.masses[atom1Type][3]) + '-' + \
                                    str(self.masses[atom2Type][3])
                        self.bondcs[key].append('#')
                        self.bondcs[key].append(typeStr)
                        break
        for key in range(1, len(self.anglecs) + 1):
            if not '#' in self.anglecs[key]:
                for angleKey in range(1, len(self.angles) + 1):
                    if int(self.angles[angleKey][1]) == key:
                        # find atom type strings
                        atom1 = int(self.angles[angleKey][2])
                        atom2 = int(self.angles[angleKey][3])
                        atom3 = int(self.angles[angleKey][4])
                        atom1Type = int(self.atoms[atom1][2])
                        atom2Type = int(self.atoms[atom2][2])
                        atom3Type = int(self.atoms[atom3][2])
                        typeStr = str(self.masses[atom1Type][3]) + '-' \
                                    + str(self.masses[atom2Type][3]) + '-' \
                                    + str(self.masses[atom3Type][3])
                        self.anglecs[key].append('#')
                        self.anglecs[key].append(typeStr)
                        break
        for key in range(1, len(self.dihedcs) + 1):
            if not '#' in self.dihedcs[key]:
                for dihedKey in range(1, len(self.diheds) + 1):
                    if int(self.diheds[dihedKey][1]) == key:
                        # find atom type strings
                        atom1 = int(self.diheds[dihedKey][2])
                        atom2 = int(self.diheds[dihedKey][3])
                        atom3 = int(self.diheds[dihedKey][4])
                        atom4 = int(self.diheds[dihedKey][5])
                        atom1Type = int(self.atoms[atom1][2])
                        atom2Type = int(self.atoms[atom2][2])
                        atom3Type = int(self.atoms[atom3][2])
                        atom4Type = int(self.atoms[atom4][2])
                        typeStr = str(self.masses[atom1Type][3]) + '-' \
                                    + str(self.masses[atom2Type][3]) + '-' \
                                    + str(self.masses[atom3Type][3]) + '-' \
                                    + str(self.masses[atom4Type][3])
                        self.dihedcs[key].append('#')
                        self.dihedcs[key].append(typeStr)
                        break
        for key in range(1, len(self.improcs) + 1):
            if not '#' in self.improcs[key]:
                for improKey in range(1, len(self.impros) + 1):
                    if int(self.impros[improKey][1]) == key:
                        # find atom type strings
                        atom1 = int(self.impros[improKey][2])
                        atom2 = int(self.impros[improKey][3])
                        atom3 = int(self.impros[improKey][4])
                        atom4 = int(self.impros[improKey][5])
                        atom1Type = int(self.atoms[atom1][2])
                        atom2Type = int(self.atoms[atom2][2])
                        atom3Type = int(self.atoms[atom3][2])
                        atom4Type = int(self.atoms[atom4][2])
                        typeStr = str(self.masses[atom1Type][3]) + '-' \
                                    + str(self.masses[atom2Type][3]) + '-' \
                                    + str(self.masses[atom3Type][3]) + '-' \
                                    + str(self.masses[atom4Type][3])
                        self.improcs[key].append('#')
                        self.improcs[key].append(typeStr)
                        break

    def getPeriodics(self):
        """ Update max and min periodics of x, y, z in the system """
        nums = [0.0] * 6
        atom = self.atom_len
        while atom < len(self.atoms) - 1 * self.atom_len:
            if int(self.atoms[int(atom) + 7]) < nums[0]:  # min X periodic
                nums[0] = int(self.atoms[int(atom) + 7])
            if int(self.atoms[int(atom) + 7]) > nums[1]:  # max X periodic
                nums[1] = int(self.atoms[int(atom) + 7])
            if int(self.atoms[int(atom) + 8]) < nums[2]:  # min Y periodic
                nums[2] = int(self.atoms[int(atom) + 8])
            if int(self.atoms[int(atom) + 8]) > nums[3]:  # max Y periodic
                nums[3] = int(self.atoms[int(atom) + 8])
            if int(self.atoms[int(atom) + 9]) < nums[4]:  # min Z periodic
                nums[4] = int(self.atoms[int(atom) + 9])
            if int(self.atoms[int(atom) + 9]) > nums[5]:  # max Z periodic
                nums[5] = int(self.atoms[int(atom) + 9])
            atom += self.atom_len
        self.arr_per = nums

    def updateCoords(self, filename):
        """ Update atom coordinates from a file """
        updated_coords = open(filename, 'r')
        for line in updated_coords:
            if 'xlo' in line:
                desc = line.split()
                self.bounds['x'] = desc
                line = updated_coords.next()
                desc = line.split()
                self.bounds['y'] = desc
                line = updated_coords.next()
                desc = line.split()
                self.bounds['z'] = desc
                line = updated_coords.next()
            if 'Atoms' in line:
                # update atom coords and periodics
                updated_coords.next()
                line = updated_coords.next()
                while not line == '\n':
                    desc = line.split()
                    self.atoms[(int(desc[0])) * self.atomLen + 4] = \
                                                            float(desc[4])
                    self.atoms[(int(desc[0])) * self.atomLen + 5] = \
                                                            float(desc[5])
                    self.atoms[(int(desc[0])) * self.atomLen + 6] = \
                                                            float(desc[6])
                    self.atoms[(int(desc[0])) * self.atomLen + 7] = \
                                                            float(desc[7])
                    self.atoms[(int(desc[0])) * self.atomLen + 8] = \
                                                            float(desc[8])
                    self.atoms[(int(desc[0])) * self.atomLen + 9] = \
                                                            float(desc[9])
                    line = updated_coords.next()
        updated_coords.close()
        self.dd = [float(self.bounds['x'][1]) - float(self.bounds['x'][0]),\
                   float(self.bounds['y'][1]) - float(self.bounds['y'][0]),\
                   float(self.bounds['z'][1]) - float(self.bounds['z'][0])]
        self.getPeriodics()
        os.remove(filename)

    def write(self, oFileName):
        """ Write output to file with given name """
        # Writes output to outfile
        outFile = open(oFileName, 'w+')
        outFile.write(self.headerLine + '\n')

        outFile.write('  ' + str(len(self.atoms)) + ' ' + str('atoms'))
        outFile.write('\n  ' + str(len(self.bonds)) + ' ' + str('bonds'))
        outFile.write('\n  ' + str(len(self.angles)) + ' ' + str('angles'))
        outFile.write('\n  ' + str(len(self.diheds)) + ' ' + str('dihedrals'))
        outFile.write('\n  ' + str(len(self.impros)) + ' ' + str('impropers'))

        outFile.write('\n\n  ' + str(len(self.masses)) + ' atom types')
        outFile.write('\n  ' + str(len(self.bondcs)) + ' bond types')
        outFile.write('\n  ' + str(len(self.anglecs)) + ' angle types')
        outFile.write('\n  ' + str(len(self.dihedcs)) + ' dihedral types')
        outFile.write('\n  ' + str(len(self.improcs)) + ' improper types')

        toPrint = ' '.join(self.bounds['x'])
        outFile.write('\n\n  ' + toPrint)
        toPrint = ' '.join(self.bounds['y'])
        outFile.write('\n  ' + toPrint)
        toPrint = ' '.join(self.bounds['z'])
        outFile.write('\n  ' + toPrint)

        outFile.write("\n\nMasses\n\n")
        for key in range(1, len(self.masses) + 1):
            toPrint = "  " + " ".join(self.masses[key]) + "\n"
            outFile.write(toPrint)

        outFile.write("\nPair Coeffs\n\n")
        for key in range(1, len(self.paircs) + 1):
            toPrint = "  " + " ".join(self.paircs[key]) + "\n"
            outFile.write(toPrint)

        outFile.write("\nBond Coeffs\n\n")
        for key in range(1, len(self.bondcs) + 1):
            toPrint = "  " + "  ".join(self.bondcs[key]) + "\n"
            outFile.write(toPrint)

        outFile.write("\nAngle Coeffs\n\n")
        for key in range(1, len(self.anglecs) + 1):
            toPrint = "  " + "  ".join(self.anglecs[key]) + "\n"
            outFile.write(toPrint)
        outFile.write("\nDihedral Coeffs\n\n")
        for key in range(1, len(self.dihedcs) + 1):
            toPrint = "  " + "  ".join(self.dihedcs[key]) + "\n"
            outFile.write(toPrint)

        outFile.write("\nImproper Coeffs\n")
        for key in range(1, len(self.improcs) + 1):
            toPrint = "  ".join(self.improcs[key])
            outFile.write("\n  " + toPrint)

        outFile.write("\n\nBondBond Coeffs\n")
        for key in range(1, len(self.bbcs) + 1):
            toPrint = " ".join(self.bbcs[key])
            outFile.write("\n  " + toPrint)

        outFile.write("\n\nBondAngle Coeffs\n")
        for key in range(1, len(self.bacs) + 1):
            toPrint = " ".join(self.bacs[key])
            outFile.write("\n  " + toPrint)

        outFile.write('\n\nAngleAngle Coeffs\n')
        for key in range(1, len(self.aacs) + 1):
            toPrint = ' '.join(self.aacs[key])
            outFile.write('\n  ' + toPrint)

        outFile.write('\n\nAngleAngleTorsion Coeffs\n')
        for key in range(1, len(self.aatcs) + 1):
            toPrint = ' '.join(self.aatcs[key])
            outFile.write('\n  ' + toPrint)

        outFile.write('\n\nEndBondTorsion Coeffs\n')
        for key in range(1, len(self.ebtcs) + 1):
            toPrint = ' '.join(self.ebtcs[key])
            outFile.write('\n  ' + toPrint)

        outFile.write('\n\nMiddleBondTorsion Coeffs\n')
        for key in range(1, len(self.mbtcs) + 1):
            toPrint = ' '.join(self.mbtcs[key])
            outFile.write('\n  ' + toPrint)

        outFile.write('\n\nBondBond13 Coeffs\n')
        for key in range(1, len(self.bb13cs) + 1):
            toPrint = ' '.join(self.bb13cs[key])
            outFile.write('\n  ' + toPrint)

        outFile.write('\n\nAngleTorsion Coeffs\n')
        for key in range(1, len(self.atcs) + 1):
            toPrint = ' '.join(self.atcs[key])
            outFile.write('\n  ' + toPrint)

        outFile.write('\n\nAtoms\n')
        for key in range(1, len(self.atoms) + 1):
            toPrint = ' '.join(self.atoms[key])
            outFile.write('\n  ' + toPrint)

        outFile.write('\n\nBonds\n')
        for key in range(1, len(self.bonds) + 1):
            toPrint = ' '.join(self.bonds[key])
            outFile.write('\n  ' + toPrint)

        outFile.write('\n\nAngles\n')
        for key in range(1, len(self.angles) + 1):
            toPrint = ' '.join(self.angles[key])
            outFile.write('\n  ' + toPrint)

        outFile.write('\n\nDihedrals\n')
        for key in range(1, len(self.diheds) + 1):
            toPrint = ' '.join(self.diheds[key])
            outFile.write('\n  ' + toPrint)

        outFile.write('\n\nImpropers\n')
        for key in range(1, len(self.impros) + 1):
            toPrint = ' '.join(self.impros[key])
            outFile.write('\n  ' + toPrint)
        outFile.write("\n")
        outFile.close()

