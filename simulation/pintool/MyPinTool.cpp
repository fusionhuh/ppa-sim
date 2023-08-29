#include "pin.H"
#include <iostream>
#include <fstream>
#include <stdint.h>

static std::ofstream outFile;
std::string convert_opcode_to_str(int64_t opcode) {
	if (opcode == XED_ICLASS_ADD) {
		return "ADD";
	}
	else if (opcode == XED_ICLASS_SUB) {
		return "SUB";
	}
	else if (opcode == XED_ICLASS_LEA) {
		return "LEA";
	}
	else {
		perror("Unsupported opcode");
		exit(-1);
	}
}

VOID write_ops_to_file(UINT64 op1, UINT64 op2, uint64_t opcode) {
	outFile << op1 << "\\" << op2 << "\\" << convert_opcode_to_str(opcode) <<  std::endl;
}

VOID mem_write(ADDRINT addr, UINT32 size, UINT64 op2, xed_iclass_enum_t type) { // mem write
	if (size == 1) {
		uint8_t* ptr = (uint8_t*) addr;
		uint8_t op1 = *ptr;
		write_ops_to_file(op1, op2, type);
	}
	else if (size == 2) {
		uint16_t* ptr = (uint16_t*) addr;
		uint16_t op1 = *ptr;
		write_ops_to_file(op1, op2, type);
	}
	else if (size == 4) {
		uint32_t* ptr = (uint32_t*) addr;
		uint32_t op1 = *ptr;
		write_ops_to_file(op1, op2, type);
	}
	else if (size == 8) {
		uint64_t* ptr = (uint64_t*) addr;
		uint64_t op1 = *ptr;
		write_ops_to_file(op1, op2, type);
	}
	else {
		perror("Unrecognized write size");
		exit(-1);
	}
}

VOID mem_read(ADDRINT addr, UINT32 size, UINT64 op1, xed_iclass_enum_t type) { // mem read
	if (size == 1) {
		uint8_t* ptr = (uint8_t*) addr;
		uint8_t op2 = *ptr;
		write_ops_to_file(op1, op2, type);
	}
	else if (size == 2) {
		uint16_t* ptr = (uint16_t*) addr;
		uint16_t op2 = *ptr;
		write_ops_to_file(op1, op2, type);
	}
	else if (size == 4) {
		uint32_t* ptr = (uint32_t*) addr;
		uint32_t op2 = *ptr;
		write_ops_to_file(op1, op2, type);
	}
	else if (size == 8) {
		uint64_t* ptr = (uint64_t*) addr;
		uint64_t op2 = *ptr;
		write_ops_to_file(op1, op2, type);
	}
	else {
		perror("Unrecognized read size");
		exit(-1);
	}
}

VOID no_mem(UINT64 op1, UINT64 op2, xed_iclass_enum_t type) {
	write_ops_to_file(op1, op2, type);
}

VOID lea(CONTEXT* ctxt, UINT64 displacement, UINT64 basereg, UINT64 indexreg, UINT64 scale, UINT64 op1) {
	UINT64 base = (basereg == REG_INVALID()) ? 0 : PIN_GetContextReg(ctxt, (REG)basereg);
	UINT64 index = (indexreg == REG_INVALID()) ? 0 : PIN_GetContextReg(ctxt, (REG)indexreg);
	if (index == 0) {
		write_ops_to_file(displacement, base, XED_ICLASS_LEA);
	}
	else {
		write_ops_to_file(displacement, basereg, XED_ICLASS_LEA);
		write_ops_to_file(displacement+basereg, indexreg*scale, XED_ICLASS_LEA);
	}
}


// This function is called before each instruction is executed
VOID Instruction(INS ins, VOID *v)
{


	// ------------- PROBABLY USEFUL FUNCTIONS ---------------------
	// 1) INS_IsMemoryRead()
	// 2) INS_IsMemoryWrite()
	// 3) INS_OperandIsReg()

	// if ins is read, then op2 should be memory read
	// if ins is write, then op1 should be memory write (assuming intel syntax order)
	// assign different callback functions for different situations

    // Check if the instruction is an "add" or "sub" instruction
    auto opcode = INS_Opcode(ins);
    if (opcode == XED_ICLASS_ADD || opcode == XED_ICLASS_SUB) {
    	if (INS_OperandCount(ins) != 3) {
	    	cout << INS_Mnemonic(ins);
    		perror("Error: Invalid instruction picked up");
    		return;
    	}
		if (INS_IsMemoryRead(ins) && !INS_IsMemoryWrite(ins)) {
			INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_read), IARG_MEMORYREAD_EA, IARG_MEMORYREAD_SIZE, IARG_REG_VALUE, INS_OperandReg(ins,0), IARG_UINT64, opcode, IARG_END);
		}
		else if (INS_IsMemoryWrite(ins)) {
			if (INS_OperandIsReg(ins,1)) {
				INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_write), IARG_MEMORYWRITE_EA, IARG_MEMORYWRITE_SIZE, IARG_REG_VALUE, INS_OperandReg(ins, 1), IARG_UINT64, opcode, IARG_END);
			}
			else if (INS_OperandIsImmediate(ins,1)) {
				INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_write), IARG_MEMORYWRITE_EA, IARG_MEMORYWRITE_SIZE, IARG_UINT64, INS_OperandImmediate(ins,1), IARG_UINT64, opcode, IARG_END);
			}
			else {
				printf("Error: unrecognized operand 2\n");
				exit(-1);
			}
		}
		else {
			if (INS_OperandIsReg(ins, 1)) {
				INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(no_mem), IARG_REG_VALUE, INS_OperandReg(ins,0), IARG_REG_VALUE, INS_OperandReg(ins, 1), IARG_UINT64, opcode, IARG_END);
			} 
			else if (INS_OperandIsImmediate(ins, 1)) {
				INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(no_mem), IARG_REG_VALUE, INS_OperandReg(ins,0), IARG_UINT64, INS_OperandImmediate(ins, 1), IARG_UINT64, opcode, IARG_END);
			}
			else {
				perror("Error: unrecognized 2nd operand type");
				exit(-1);
			}
		}
    }
    else if (opcode == XED_ICLASS_LEA) {
    	if (INS_IsMemoryWrite(ins) || INS_IsMemoryRead(ins)) {
    		printf("Unexpected LEA behavior\n");
    		exit(-1);
    	}
    	INT64 displacement = INS_OperandMemoryDisplacement(ins, 1);
		UINT64 basereg = INS_OperandMemoryBaseReg(ins,1);
    	UINT64 index = INS_OperandMemoryIndexReg(ins,1);
    	UINT64 scale = INS_OperandMemoryScale(ins,1);
    	/*if (basereg == REG_INVALID()) {
    		perror("Wrong base register");
    		exit(-1);
    	}
    	if (index == REG_INVALID()) {
			index = basereg;
			exit(-1);
    	}
    	else {
    	}*/
    	INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(lea), IARG_CONST_CONTEXT, IARG_UINT64, displacement, IARG_UINT64, basereg, IARG_UINT64, index, IARG_UINT64, scale, IARG_END);
    }
}

// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
    outFile.close();
}

int main(int argc, char *argv[])
{
    // Initialize Pin
    if (PIN_Init(argc, argv)) return 1;

    outFile.open("operands_output.txt");

    INS_AddInstrumentFunction(Instruction, 0);

    PIN_AddFiniFunction(Fini, 0);

    // Start the program, never returns
    PIN_StartProgram();

    return 0;
}
