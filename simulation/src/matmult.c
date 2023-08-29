#include <string.h>


double* matmult(int n, const double* A, const double* B, double* C) {
	for (int i = 0; i < n; i++) C[i]=0.0;
	for (int i = 0; i < n; ++i) {
		for (int j = 0; j < n; ++j) {
			double cij = C[i+j*n];
			for (int k = 0; k < n; k++) {
				cij += A[i+k*n]*B[k+j*n];
				C[i+j*n]=cij;
			}
		}
	}
}


int main(void) {
	int n = 9;
	double A[n];
	double B[n];
	double C[n];
	matmult(n, A,B,C);
	
	return 0;	
}