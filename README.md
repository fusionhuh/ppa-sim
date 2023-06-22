# Dependencies

**Python modules**: matplotlib, cvxopt, numpy

**Other**: yosys, iverilog, vvp (all must be on PATH)

# Project Structure

`main.py` - This is the main script. It takes an adder description as an argument and generates the verilog for that adder \+ synthesizes it.

`py_module/` - Contains helper modules used in the main script.

`verilog/base/` - Contains the high-level verilog generated for basic PPAs (no complex structure).

`verilog/structured/` - Contains the high-level verilog generated for complex adders.

`verilog/logic/` - Contains helper verilog modules.

`synthesis/` - Contains various scripts and technology files to facilitate the synthesis process.

`synthesis/verilog/` - Contains the synthesized verilog for adders (same organization as top-level `verilog/` directory). 

# Usage

`main.py` accepts an adder description in the form of `{base_type}.{width}.{structure-block_size}`.

`base_type` refers to the type of PPA used in the design. Accepted values:

1. ks (Kogge-Stone)
2. bk (Brent-Kung)
3. skl (Sklansky)
4. hybrid-`{levels}` (ks and bk hybrid structure with additional `levels` field)
5. serial (Ordinary ripple carry adder)

`width` is the width of the adder. Acceptable values are any power of two greater than 2.

`structure` refers to the organization of PPA blocks in the design. `block_size` refers to the width of each of those adder
blocks. `block_size` must be a power of two that is greater than 2 and less than `width`.

Accepted structure values:

1. basic (Design is just one PPA block, truncate `block_size`)
2. rc (PPA blocks are chained in a ripple carry fashion)
3. cskip (Carry skip)
4. cselect (Carry select)
5. cla (Carry lookahead)

**Examples**:

1. ks.16.basic (16-bit Kogge-Stone with just one PPA block)
2. bk.32.rc-8 (32-bit adder with four 8-bit Brent-Kung blocks chained like a ripple carry adder)
3. hybrid-2.64.cselect-16 (64-bit adder with four 16-bit two-level hybrid blocks in a carry select structure)





