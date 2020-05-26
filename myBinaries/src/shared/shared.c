#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> //Header file for sleep(). man 3 sleep for details. 
#include <pthread.h> 

int array[10];

void print_array(){
	for (int i = 0; i < 10; i++)
		printf("%d: %d\n", i, array[i]);
}
void set_array(int v){
	for (int i = 0; i < 10; i++)
		array[i] = v;
}
void empty_loop(){
	for (int i = 0; i < 1000; i++)
		;
}

// A normal C function that is executed as a thread 
// when its name is specified in pthread_create() 
void *myThreadFun(void *vargp) 
{ 
	for (int i = 0; i < 100000; i++)
		print_array();
	return NULL; 
} 

int main() 
{ 
	pthread_t thread_id; 

	set_array(0);

	printf("Before Thread\n");
	pthread_create(&thread_id, NULL, myThreadFun, NULL); 

	for (int i = 0; i < 1000; i++) {
		empty_loop();
		set_array(i);
	}

	pthread_join(thread_id, NULL); 
	printf("After Thread\n"); 
	exit(0); 
}

