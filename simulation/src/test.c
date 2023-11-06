#include <string.h>


int main(void) {
	int stack_arr1[256];
	int stack_arr2[256];

	memset(stack_arr1, 0, sizeof(int)*256);
	memset(stack_arr2, 5, sizeof(int)*256);
	for (int i = 0; i < 256; i++) {
		stack_arr1[i] += stack_arr2[i]; 
	}

	return 0;
	
}