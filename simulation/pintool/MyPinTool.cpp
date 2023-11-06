#include "pin.H"
#include <iostream>
#include <fstream>
#include <stdint.h>
#include <string.h>

using namespace std;

enum class ExtraOpcodes {
	MEM_ACCESS=0x10000
};


static std::ofstream operands_file;
static std::ofstream context_file;
std::string convert_opcode_to_str(uint64_t opcode) {
	if (opcode == XED_ICLASS_ADD) {
		return "ADD";
	}
	else if (opcode == XED_ICLASS_SUB) {
		return "SUB";
	}
	else if (opcode == XED_ICLASS_LEA) {
		return "LEA";
	}
	else if (opcode == XED_ICLASS_MOV) {
		return "MOV";
	}
	else if (opcode == (uint64_t) ExtraOpcodes::MEM_ACCESS) {
		return "MEM";
	}
	else {
		perror("Unsupported opcode");
		exit(-1);
	}
}


enum class Notes {
	NONE=0,
	MEM_READ,
	MEM_WRITE	
};

const char* notes_arr[3] = {" ","This is a mem read", "This is a mem write"};

VOID write_ops_to_file(UINT64 ins_addr, UINT64 op1, UINT64 op2, uint64_t opcode, uint64_t note = 0) {
	static size_t ins_num = 0;
	operands_file << hex << op1 << "\\" << op2 << "\\" << convert_opcode_to_str(opcode) << "\\" << ins_addr << "\\" << dec << ins_num << "\\" << notes_arr[note] << std::endl;
	ins_num++;
}

VOID mem_write(UINT64 ins_addr, ADDRINT addr, UINT32 size, UINT64 op2, xed_iclass_enum_t type, uint64_t note) { // mem write
	uint64_t op1=0;
	memcpy(&op1, (uint8_t*) addr, size);
	write_ops_to_file(ins_addr,op1,op2,type, note);
}

VOID mem_read(UINT64 ins_addr, ADDRINT addr, UINT32 size, UINT64 op1, xed_iclass_enum_t type, uint64_t note) { // mem read
	uint64_t op2=0;
	memcpy(&op2, (uint8_t*) addr, size);
	write_ops_to_file(ins_addr,op1,op2,type, note);
}

VOID no_mem(UINT64 ins_addr, UINT64 op1, UINT64 op2, xed_iclass_enum_t type) {
	write_ops_to_file(ins_addr, op1, op2, type);
}


VOID mem_offset(UINT64 ins_addr, CONTEXT* ctxt, UINT64 displacement, UINT64 basereg, UINT64 indexreg, UINT64 scale, xed_iclass_enum_t opcode) {
	UINT64 base = (basereg == REG_INVALID()) ? 0 : PIN_GetContextReg(ctxt, (REG)basereg);
	UINT64 index = (indexreg == REG_INVALID()) ? 0 : PIN_GetContextReg(ctxt, (REG)indexreg);

	if (index == 0) {
		write_ops_to_file(ins_addr, displacement, base, opcode);
	}
	else {
		write_ops_to_file(ins_addr, displacement, basereg, opcode);
		write_ops_to_file(ins_addr, displacement+basereg, indexreg*scale, opcode);
	}
}



const char* map_reg_to_str(REG reg) {
	UINT64 adjusted_indx = ((UINT64) reg) - 3;
	const char* str_arr[16] = 
	{
		"RDI",
		"RSI",
		"RBP",
		"RSP",
		"RBX",
		"RDX",
		"RCX",
		"RAX",
		"R8",
		"R9",
		"R10",
		"R11",
		"R12",
		"R13",
		"R14",
		"R15"
	};
	if (reg == REG_INVALID()) {
		return "IMM";
	}
	else if (adjusted_indx >= 16) {
		return "Unknown";
	}

	return str_arr[adjusted_indx];
}


// This function is called before each instruction is executed
VOID Instruction(INS ins, VOID *v)
{
	uint64_t curr_ins_address = INS_Address(ins);



	UINT64 op_count = INS_OperandCount(ins);
	if (op_count < 2) {
		return;
	}


	// PLEASE FIX, BELOW CODE IS WONKY WITH INSTRUCTIONS THAT ACCESS MEMORY

	
	bool is_op1_reg = ((REG) INS_OperandReg(ins, 0) != REG_INVALID());
	//UINT64 op1_type = is_op1_reg ? IARG_REG_VALUE : IARG_UINT64;
	REG op1_identifier = is_op1_reg ? INS_OperandReg(ins, 0) : REG_INVALID(); // -1 should be replaced by imm
	
	bool is_op2_reg = ((REG) INS_OperandReg(ins, 1) != REG_INVALID());
	//UINT64 op2_type = is_op2_reg ? IARG_REG_VALUE : IARG_UINT64;
	REG op2_identifier = is_op2_reg ? INS_OperandReg(ins, 1) : REG_INVALID(); // -1 should be replaced by imm



	bool instruction_match = true;
	bool duplicate = false;
	
    auto opcode = INS_Opcode(ins);
    if (opcode == XED_ICLASS_ADD || opcode == XED_ICLASS_SUB) {
    	if (INS_OperandCount(ins) != 3) {
	    	cout << INS_Mnemonic(ins);
    		perror("Error: Invalid instruction picked up");
    		exit(-1);
    	}
		if (INS_IsMemoryRead(ins) && !(INS_IsMemoryWrite(ins))) {
    		INT64 displacement = INS_OperandMemoryDisplacement(ins, 1);
			UINT64 basereg = INS_OperandMemoryBaseReg(ins,1);
    		UINT64 index = INS_OperandMemoryIndexReg(ins,1);
    		UINT64 scale = INS_OperandMemoryScale(ins,1);			
    		INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_offset), IARG_UINT64, curr_ins_address, IARG_CONST_CONTEXT, IARG_UINT64, displacement, IARG_UINT64, basereg, IARG_UINT64, index, IARG_UINT64, scale, IARG_UINT64, ExtraOpcodes::MEM_ACCESS, IARG_END);
			INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_read), IARG_UINT64, curr_ins_address, IARG_MEMORYREAD_EA, IARG_MEMORYREAD_SIZE, IARG_REG_VALUE, INS_OperandReg(ins,0), IARG_UINT64, opcode, IARG_UINT64, Notes::MEM_READ, IARG_END);
			
		}
		else if (INS_IsMemoryWrite(ins)) {
    		INT64 displacement = INS_OperandMemoryDisplacement(ins, 0);
			UINT64 basereg = INS_OperandMemoryBaseReg(ins,0);
    		UINT64 index = INS_OperandMemoryIndexReg(ins,0);
    		UINT64 scale = INS_OperandMemoryScale(ins,0);
    		INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_offset), IARG_UINT64, curr_ins_address, IARG_CONST_CONTEXT, IARG_UINT64, displacement, IARG_UINT64, basereg, IARG_UINT64, index, IARG_UINT64, scale, IARG_UINT64, ExtraOpcodes::MEM_ACCESS, IARG_END);
			if (INS_OperandIsReg(ins,1)) {
				INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_write), IARG_UINT64, curr_ins_address, IARG_MEMORYWRITE_EA, IARG_MEMORYWRITE_SIZE, IARG_REG_VALUE, INS_OperandReg(ins, 1), IARG_UINT64, opcode, IARG_UINT64, Notes::MEM_WRITE, IARG_END);
			}
			else if (INS_OperandIsImmediate(ins,1)) {
				INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_write), IARG_UINT64, curr_ins_address, IARG_MEMORYWRITE_EA, IARG_MEMORYWRITE_SIZE, IARG_UINT64, INS_OperandImmediate(ins,1), IARG_UINT64, opcode, IARG_UINT64, Notes::MEM_WRITE, IARG_END);
			}
			else {
				printf("Error: unrecognized operand 2\n");
				exit(-1);
			}
		}
		else {
			if (INS_OperandIsReg(ins, 1)) {
				INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(no_mem), IARG_UINT64, curr_ins_address, IARG_REG_VALUE, INS_OperandReg(ins,0), IARG_REG_VALUE, INS_OperandReg(ins, 1), IARG_UINT64, opcode, IARG_END);
			} 
			else if (INS_OperandIsImmediate(ins, 1)) {
				INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(no_mem), IARG_UINT64, curr_ins_address, IARG_REG_VALUE, INS_OperandReg(ins,0), IARG_UINT64, INS_OperandImmediate(ins, 1), IARG_UINT64, opcode, IARG_END);
			}
			else {
				perror("Error: unrecognized 2nd operand type");
				exit(-1);
			}
		}
    }
    else if (opcode == XED_ICLASS_LEA) {
    	if (INS_IsMemoryWrite(ins) || INS_IsMemoryRead(ins)) {
    		perror("Unexpected LEA behavior\n");
    		exit(-1);
    	}
    	
    	INT64 displacement = INS_OperandMemoryDisplacement(ins, 1);
		UINT64 basereg = INS_OperandMemoryBaseReg(ins,1);
    	UINT64 index = INS_OperandMemoryIndexReg(ins,1);
    	UINT64 scale = INS_OperandMemoryScale(ins,1);
		
    	INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_offset), IARG_UINT64, curr_ins_address, IARG_CONST_CONTEXT, IARG_UINT64, displacement, IARG_UINT64, basereg, IARG_UINT64, index, IARG_UINT64, scale, IARG_UINT64, XED_ICLASS_LEA, IARG_END);
    }
    else if (opcode == XED_ICLASS_MOV) {
    	int mem_write = (int) INS_OperandIsMemory(ins,0), mem_read = (int) INS_OperandIsMemory(ins,1);
    	if ((mem_write | mem_read) == 0) {
    		return;
    	}
    	if ((mem_write^mem_read) == 0) {
    		perror("Unexpected MOV behavior\n");
    		exit(-1);
    	}
    	
    	UINT64 mem_index = (mem_write) ? 0 : 1;
    	INT64 displacement = INS_OperandMemoryDisplacement(ins, mem_index);
		UINT64 basereg = INS_OperandMemoryBaseReg(ins,mem_index);
    	UINT64 index = INS_OperandMemoryIndexReg(ins,mem_index);
    	UINT64 scale = INS_OperandMemoryScale(ins,mem_index);
		
    	INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_offset), IARG_UINT64, curr_ins_address, IARG_CONST_CONTEXT, IARG_UINT64, displacement, IARG_UINT64, basereg, IARG_UINT64, index, IARG_UINT64, scale, IARG_UINT64, XED_ICLASS_MOV, IARG_END);
    }
    else {
    	instruction_match = false;
    }
    //else if (opcode == XED_ICLASS_CMP) {
    	// instruction format:
    	// accumulator (reg, mem), reference (register, immediate)
		
    	
    	
    //}
    //else if (opcode == XED_ICLASS_PUSH) {
    	
    //}
    //else if (opcode == XED_ICLASS_POP) {
    	
    //}


    if (instruction_match == true) {
		context_file << hex << curr_ins_address << "/";
    	context_file << dec << map_reg_to_str(op1_identifier) << "/" << map_reg_to_str(op2_identifier) << endl; 
    }
}

// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
    operands_file.close();
}

int main(int argc, char *argv[])
{
    // Initialize Pin

	cout << "REG_RDI: " << REG_RDI << endl;
	cout << "REG_RSI: " << REG_RSI << endl;
	cout << "REG_RBP: " << REG_RBP << endl;
	cout << "REG_RSP: " << REG_RSP << endl;
	cout << "REG_RBX: " << REG_RBX << endl;
	cout << "REG_RDX: " << REG_RDX << endl;
	cout << "REG_RCX: " << REG_RCX << endl;
	cout << "REG_RAX: " << REG_RAX << endl;
	cout << "REG_R15: " << REG_R15 << endl;
    
    if (PIN_Init(argc, argv)) return 1;

    operands_file.open("extracted_operands.txt");
    context_file.open("context.txt");

    INS_AddInstrumentFunction(Instruction, 0);

    PIN_AddFiniFunction(Fini, 0);

    // Start the program, never returns
    PIN_StartProgram();

    return 0;
}
