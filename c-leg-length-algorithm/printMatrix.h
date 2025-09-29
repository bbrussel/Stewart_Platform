#include<stdio.h>
#include<math.h>


void print1DArrayDoubles(double arr[], unsigned long int length) {
	int counter;
	printf("| ");
	for(counter = 0; counter < length; counter++)
		if (counter == 0) {
			printf("%.3f", arr[counter]);
		} else {
		printf(", %.3f", arr[counter]);
	}
   printf(" |");
}

void print1DArrayFloats(float arr[], unsigned long int length) {
	int counter;
	printf("| ");
	for(counter = 0; counter < length; counter++)
		if (counter == 0) {
			printf("%.3f", arr[counter]);
		} else {
		printf(", %.3f", arr[counter]);
	}
   printf(" |");
}

void print3x3Array(double arr[3][3]) {
	int row;
	int col;
	int counter = 0;
	for(row = 0; row < 3; row++) {
		printf("\n| ");
		counter = 0;
		for(col = 0; col < 3; col++) {

			if (counter == 0) {
				printf("%f",arr[row][col]);
			} else {
				printf(", ");
				printf("%f",arr[row][col]);
			}
			
			counter += 1;
		}
		printf(" |");
	}
}

void print3x6Array(double arr[3][6]) {
	int row;
	int col;
	int counter = 0;
	for(row = 0; row < 3; row++) {
		printf("\n| ");
		counter = 0;
		for(col = 0; col < 6; col++) {

			if (counter == 0) {
				printf("%.3f",arr[row][col]);
			} else {
				printf(", ");
				printf("%.3f",arr[row][col]);
			}
			
			counter += 1;
		}
		printf(" |");
	}
}