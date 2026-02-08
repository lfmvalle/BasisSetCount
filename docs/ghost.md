[↩ README](../README.md) | [◀ Core-Effective Potential basis sets](cep.md)

# Ghost atoms

The script recognizes *ghost atoms* in the output and display the basis set of the proper element.

The information is collected from the `ATOMS TRANSFORMED INTO GHOSTS` section of the output file.

Ghost atoms are displayed as `Xx (Ee)` in the output, where *Ee* is the element corresponding to the basis set.

> **Example 1:** <br> If the output presents a ghost atom originating from a oxygen vacancy, it will be displayed as `Xx (O)`. 

> **Example 2:** <br> For an iron vacancy, it will be `Xx (Fe)`.