#include <stdio.h>

int main() {
	int array[10];
	array[1] = 1;
	array[5] = 5;
	for (int i = 0; i < 10; i++)
		printf("%d: %d\n", i, array[i]);
	return 0;
}
