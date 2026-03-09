# HEP Constants

This is a project for the generation of C++ header files
automatically from CODATA values of physical constants.

It takes advantage of unit and SI prefix definitions from
the SciKit-HEP project [hepunits](https://github.com/scikit-hep/hepunits)
and uses some lightweight symbolic manipulation from
[sympy](https://docs.sympy.org/latest/index.html) to be able
to output C++ constexpr expressions.

Constants, units and prefixes are all are organised in namespaces.

*This is a work in progress, contributions welcome.*
