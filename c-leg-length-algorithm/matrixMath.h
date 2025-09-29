#include<stdio.h>
#include<math.h>


void print6x3Array(double arr[6][3]) {
	int row;
	int col;
	int counter = 0;
	for(row = 0; row < 6; row++) {
		printf("\n| ");
		counter = 0;
		for(col = 0; col < 3; col++) {

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

void matMult3by3(double mat1[3][3], double mat2[3][3], double resultingArray[3][3])
{
	int i, j;
	for(i = 0; i < 3; i++)
	{
		for(j = 0; j < 3; j++)
		{
			resultingArray[i][j] = 0;
			for (int k = 0; k < 3; k++) {
				resultingArray[i][j] += mat1[i][k] * mat2[k][j];
			}
		}
	}
}

void matMult3by3And3by6(double mat1[3][3], double mat2[3][6], double resultingArray[3][6])
{
	int i, j;
	for(i = 0; i < 3; i++)
	{
		for(j = 0; j < 6; j++)
		{
			resultingArray[i][j] = 0;
			for (int k = 0; k < 3; k++) {
				resultingArray[i][j] += mat1[i][k] * mat2[k][j];
			}
		}
	}
}



void extendMatrix(double result[3][6], double input[3]){
	int i, j;
	for(i = 0; i < 3; i++)
	{
		for(j = 0; j < 6; j++)
		{
			result[i][j] = input[i];
		}
	}
}


void transpose6by3(double result[3][6], double input[6][3]){
	int i, j;
	for(i = 0; i < 6; i++)
	{
		for(j = 0; j < 3; j++)
		{
			result[j][i] = input[i][j];
		}
	}
}

void calculateLegTranslations(double l[3][6], double translation[3][6], double home[3][6], double rotation[3][6], double B[3][6]){
	int row, col;
	for(row = 0; row < 3; row++)
	{
		for(col = 0; col < 6; col++)
		{
			l[row][col] = translation[row][col] + home[row][col] + rotation[row][col] - B[row][col];
		}
	}
}

void calculateLegVectorNorms(double ll[6], double l[3][6]){
	int row, col;
	double temp;
	for(col = 0; col < 6; col++)
	{
		temp = 0.0;
		for(row = 0; row < 3; row++)
		{
			temp += pow(l[row][col], 2);
		}
		ll[col] = sqrt(temp);
	}
}

