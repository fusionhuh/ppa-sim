# Project structure

`pyve.py` - Main script. Takes in adder description as an argument and generates the verilog for that adder
\+ synthesizes it. Adder description is formatted like `{base_type}.{adder_width}.{structure}-{block_width}`.
`base_type` is the type of PPA used. Available options are bk, skl, ks, hybrid, and serial. `structure` refers to the way
the PPA blocks will be organized. Likewise, `block_width` refers to the size of each of the PPA blocks. The value must be a power of two and not greater than `adder_width`. 
For adders with no complex structure, replace `{structure}-{block_width}` with `basic`. Available structures are cskip, cselect, ripple, and cla. 

`py_module/` - Contains helper modules used in pyve.py.

`verilog/base/` - Contains the high-level verilog generated for basic PPAs (no complex structure).

`verilog/structured/` - Contains the high-level verilog generated for complex adders.

`verilog/logic/` - Contains helper modules used in basic and complex designs.

`synthesis/` - Contains various scripts and technology files to facilitate the synthesis process.

`synthesis/verilog/` - Contains the synthesized verilog for adders. 
