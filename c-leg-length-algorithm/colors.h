#include<stdio.h>

void red(){
	printf("\033[1;31m");
}

void yellow(){
	printf("\033[0;33m");
}

void cyan(){
	printf("\033[0;36m");
}

void purple(){
	printf("\033[0;35m");
}

void green(){
	printf("\033[0;32m");
}

void reset(){
	printf("\033[0m");
}