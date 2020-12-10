#!/usr/bin/env python3


################################################################################
## Validates crosslinked LAMMPS-style datafiles to check for long bonds that
## would cause simulation to crash.
################################################################################
## Last modified: 11-24-2020
################################################################################
## Copyright (C) 2020 hagertnl@miamioh.edu
################################################################################


import math
import sys
from lammps import LammpsDatafile


class Results(object):
    def __init__(self):
        self.num_xlinks = 0
        self.longest_bond = 0
        self.shortest_bond = 100
        self.avg_bond = 0

    def print(self):
        print(f"Number of crosslinks found: {self.num_xlinks}")
        print(f"Crosslink length breakdown:")
        print(f"\tLongest: {self.longest_bond}")
        print(f"\tShortest: {self.shortest_bond}")
        print(f"\tAverage: {self.avg_bond}")


def get_atom(lmp: LammpsDatafile, index: int):
    """ Get the array entries for atom of index """
    return lmp.atoms[index * lmp.atom_len:(index + 1) * lmp.atom_len]


def get_mol(lmp: LammpsDatafile, atom_index: int) -> int:
    """ Get molecule for atom number """
    return lmp.atoms[atom_index * lmp.atom_len + 1]


def get_closest_periodic(coord_1: float, coord_2: float, bound: float) -> [float, float]:
    """ Find closest distance between coords using periodic boundaries """
    if coord_1 > coord_2:
        while abs(coord_1 - coord_2) > bound / 2:
            coord_1 -= bound
    else:
        while abs(coord_2 - coord_1) > bound / 2:
            coord_2 -= bound
    return coord_1, coord_2


def get_bond_len(lmp: LammpsDatafile, atom_1: int, atom_2: int) -> float:
    """ Get length of bond, translating coordinates for periodic boundaries """
    a1_c = lmp.atoms[atom_1 * lmp.atom_len + 4:atom_1 * lmp.atom_len + 7]
    a2_c = lmp.atoms[atom_2 * lmp.atom_len + 4:atom_2 * lmp.atom_len + 7]
    a1_c[0], a2_c[0] = get_closest_periodic(a1_c[0], a2_c[0], lmp.dd[0])
    a1_c[1], a2_c[1] = get_closest_periodic(a1_c[1], a2_c[1], lmp.dd[1])
    a1_c[2], a2_c[2] = get_closest_periodic(a1_c[2], a2_c[2], lmp.dd[2])
    return math.sqrt(pow(a1_c[0] - a2_c[0], 2) + pow(a1_c[1] - a2_c[1], 2) \
                    + pow(a1_c[2] - a2_c[2], 2))


def main():
    if len(sys.argv) < 2:
        print("Usage: ./crosslink_check.py <datafile>")
        sys.exit(1)
    arg = sys.argv[1]
    lmp = LammpsDatafile(arg)
    res = Results()
    for b in lmp.bonds:
        bond = lmp.bonds[b]
        # if there's a bond between 2 different molecule numbers, it's a crosslink
        if get_mol(lmp, int(bond[2])) != get_mol(lmp, int(bond[3])):
            res.num_xlinks += 1
            bond_len = get_bond_len(lmp, int(bond[2]), int(bond[3]))
            # save bond_length
            if bond_len > res.longest_bond:
                res.longest_bond = bond_len
            elif bond_len < res.shortest_bond:
                res.shortest_bond = bond_len
            res.avg_bond = ((res.avg_bond * (res.num_xlinks - 1)) + bond_len) / res.num_xlinks
    res.print()

if __name__ == '__main__':
    main()
