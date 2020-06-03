#include <stdio.h> 
#include <stdlib.h> 
#include <stdint.h>
#include <unistd.h> //Header file for sleep(). man 3 sleep for details. 
#include <string.h>
#include <pthread.h> 
#include <errno.h>
#include <sys/time.h>

#define KEY_RANGE 268435456
//#define KEY_RANGE 1
#define ENTRY_SIZE 32

//#define SEPERATE 10000 // NIC0: 0~TEST_RANGE, NIC1: SEPERATE~(SEPERATE+TEST_RANGE)
//#define TEST_RANGE 2
//#define TEST_REPEAT 300
//#define INTERVAL 1
//#define SHARDED false
//#define READ true
//#define WRITE true

#define LOG_LEVEL 1 // 0: print all, higher print less

#define my_print(level, fmt, ...) \
            do { if (level > LOG_LEVEL) fprintf(stdout, fmt, ##__VA_ARGS__); } while (0)

typedef struct Entry{
	uint64_t value[ENTRY_SIZE/8];
} Entry;

Entry *array;;

typedef struct ThreadArgv{
	int tid;
} ThreadArgv;

void copy(Entry *src, Entry *dst) {
	dst->value[0] = src->value[0];
	dst->value[1] = src->value[1];
	dst->value[2] = src->value[2];
	dst->value[3] = src->value[3];
}
void inc(Entry *e) {
	e->value[0] += 1;
	e->value[1] += 1;
	e->value[2] += 1;
	e->value[3] += 1;
}
uint64_t* read(Entry *e){
	e->value[0];
	e->value[1];
	e->value[2];
	e->value[3];
	return e->value;
}
void write(Entry *e, const uint64_t *v){
	e->value[0] = v[0];
	e->value[1] = v[1];
	e->value[2] = v[2];
	e->value[3] = v[3];
}

FILE *fp;
pthread_cond_t cond1 = PTHREAD_COND_INITIALIZER;
pthread_cond_t cond2 = PTHREAD_COND_INITIALIZER;
pthread_mutex_t lock1 = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t lock2 = PTHREAD_MUTEX_INITIALIZER;
int *numRequests;

void *schedThreadFun(void *vargp) 
{
	// Entry *array = (Entry*) malloc(KEY_RANGE*sizeof(Entry));
	Entry local;

	// main thread is waiting for NIC threads to finish reading file 
	pthread_mutex_lock(&lock1);
	ThreadArgv *argv = (ThreadArgv*)vargp;
	int numReq = numRequests[argv->tid];
	my_print(1, "nic thread %d start reading\n", argv->tid);
	const int MAX_EVENTS = 4;
	const int schedMetaSize = 2;
	int64_t *time  = (int64_t*) malloc(sizeof(int64_t)*numReq);
	int64_t *key   = (int64_t*) malloc(sizeof(int64_t)*numReq);
	int *readWrite = (int*)     malloc(sizeof(int)*numReq);
	for (int i = 0; i < numReq; i++) {
		fscanf(fp, "%ld %ld %d", &time[i], &key[i], &readWrite[i]);
	}
	my_print(1,"nic thread %d finish reading\n", argv->tid);
	pthread_cond_signal(&cond1); // notify main thread to continue to new the next thread
	pthread_mutex_unlock(&lock1);

	// NIC threads are waiting main thread to finish all threads' creation
	my_print(1,"nic thread %d wait main thread\n", argv->tid);
	pthread_mutex_lock(&lock2);
	pthread_cond_wait(&cond2, &lock2);
	pthread_mutex_unlock(&lock2);
	my_print(1,"nic thread %d start working\n", argv->tid);

	for (int i = 0; i < numReq; i++) {
		// if (i == 0)
		// 	usleep(time[i]);
		// else
		// 	usleep(time[i]-time[i-1]);

		// read(&array[0]);
		// write(&array[0], "test");
		// copy(&array[0], &local); // read
		// copy(&local, &array[0]); // write

		// struct timeval t;
		// if (LOG_LEVEL < 1)
		// 	gettimeofday(&t, NULL);
		// char buffer[32] = "test";
		switch (readWrite[i]){
		  case 0: // readonly
			// my_print(1,"[%ld, %d] cmd: r, %ld: %s\n", t.tv_sec * (int)1e6 + t.tv_usec, argv->tid, key[i], read(&array[key[i]]));
			copy(&array[key[i]], &local); // read
			//char *temp = read(i);
			break;
		  case 1: // writeonly
			// snprintf(buffer, sizeof(buffer), "%d", i);
			// my_print(1,"[%ld, %d] cmd: w, %ld: %s\n", t.tv_sec * (int)1e6 + t.tv_usec, argv->tid, key[i], buffer);
			// write(&array[key[i]], buffer);
			// copy(&local, &array[key[i]]); // write
			inc(&array[key[i]]); // inc (read and then write itself
			break;
		  case 2: // read and then write
			//char *temp = read(i);
			// snprintf(buffer, sizeof(buffer), "%d", i);
			// my_print(1,"[%ld, %d] cmd: rw, %ld: %s -> %s\n", t.tv_sec * (int)1e6 + t.tv_usec, argv->tid, key[i], read(&array[key[i]]), buffer);
			// write(&array[key[i]], buffer);
			copy(&array[key[i]], &local); // read
			copy(&local, &array[key[i]]); // write
			break;
		  default:
			break;
		}
	}

//	// sharded	
//	int64_t shardedSchedule[NIC_NUM][MAX_EVENTS*schedMetaSize] = {
//		{
//			1000000, 0, 
//			1000000, 1, 
//			-1, -1,
//			0, 0},
//		{
//			2000000, 10000, 
//			1000000, 10001,
//			1000000, 10000,
//			-1, -1}
//	};
//	// shared	
//	int64_t sharedSchedule[NIC_NUM][MAX_EVENTS*schedMetaSize] = {
//		{
//			1000000, 0, 
//			1000000, 1, 
//			-1, -1,
//			0, 0},
//		{
//			2000000, 0, 
//			1000000, 1,
//			1000000, 0,
//			-1, -1}
//	};
//	
//	int counter = 0;
//	int64_t *nextPtr = shardedSchedule[argv->tid];
//	while (*nextPtr != -1) {
//		usleep(nextPtr[0]);
//		struct timeval t;
//		gettimeofday(&t, NULL);
//		if (READ) {
//			my_print(1,"[%ld] %ld: %s\n", t.tv_sec * (int)1e6 + t.tv_usec, nextPtr[1], read(nextPtr[1]));
//			//char *temp = read(i);
//		}
//		if (WRITE) {
//			char buffer[32];
//			snprintf(buffer, sizeof(buffer), "%d", counter++);
//			write(nextPtr[1], buffer);
//		}
//
//		nextPtr += schedMetaSize;
//	}
}

//void *myThreadFun(void *vargp) 
//{ 
//	ThreadArgv *argv = (ThreadArgv*)vargp;
//	int start, end;
//	if (SHARDED) {
//		start = argv->tid*SEPERATE; // TODO access pattern
//		end = start + TEST_RANGE;
//	} else {
//		start = 0;
//		end = TEST_RANGE;
//	}
//	for (int j = 0; j < TEST_REPEAT; j++) {
//		for (int i = start; i < end; i+=INTERVAL){
//			if (READ) {
//				//my_print(1,"%d: %s\n", i, read(i));
//				char *temp = read(i);
//			}
//			if (WRITE) {
//				char buffer[32];
//				snprintf(buffer, sizeof(buffer), "%d", i);
//				write(i, buffer);
//			}
//		}
//	}
//	my_print(1,"thread: %d, before free\n", argv->tid);
//	free(argv);
//	my_print(1,"after free\n");
//	return NULL; 
//} 
int main(int argc, char **argv) 
{
	array = (Entry*) malloc(KEY_RANGE*sizeof(Entry));
	if (array == NULL) {
		my_print(10,"Malloc fail, errno: %d\n", errno);
		exit(-1);
	}

	fp = fopen(argv[1], "r");
	int numThread;
	fscanf(fp, "%d", &numThread);
	pthread_t *thread_id = (pthread_t*) malloc (sizeof(pthread_t)*numThread);
	numRequests = (int*) malloc(sizeof(int)*numThread);
	for (int i = 0; i < numThread; i++) {
		fscanf(fp, "%d", &(numRequests[i]));
	}
	int num_cores = sysconf(_SC_NPROCESSORS_ONLN);
	my_print(2,"Number cores: %d\n", num_cores);
	
	cpu_set_t cpuset;
	CPU_ZERO(&cpuset);
	CPU_SET(0, &cpuset);
	pthread_t thisThread = pthread_self();
	pthread_setaffinity_np(thisThread, sizeof(cpu_set_t), &cpuset);

	my_print(1,"Before Thread\n");
	for (int i = 0; i < numThread; i++) {
		pthread_mutex_lock(&lock1); // main thread wait the just-created nic thread to finish reading
		my_print(1,"start creating thread %d\n", i);
		ThreadArgv *argv = (ThreadArgv*)malloc(sizeof(ThreadArgv));
		argv->tid = i;
		pthread_create(&thread_id[i], NULL, schedThreadFun, argv);
		CPU_ZERO(&cpuset);
		CPU_SET(i+1, &cpuset);
		pthread_setaffinity_np(thread_id[i], sizeof(cpu_set_t), &cpuset);

		my_print(1,"wait thread %d to finish reading\n", i);
		pthread_cond_wait(&cond1, &lock1);
		pthread_mutex_unlock(&lock1);
	}
	usleep(100);
	my_print(1,"all threads are created, broadcast them to start\n");
	pthread_mutex_lock(&lock2);
	pthread_cond_broadcast(&cond2);
	pthread_mutex_unlock(&lock2);

	struct timeval t;
	int64_t start_time, end_time;
	gettimeofday(&t, NULL);
	start_time = t.tv_sec * (int)1e6 + t.tv_usec;
	my_print(2,"start_time: %ld\n", start_time);

	for (int i = 0; i < numThread; i++) {
		pthread_join(thread_id[i], NULL);
	}
	my_print(1,"After Thread\n"); 

	gettimeofday(&t, NULL);
	end_time = t.tv_sec * (int)1e6 + t.tv_usec;
	my_print(2, "end_time: %ld\n", end_time);
	my_print(2, "elapsed: %ld\n", end_time - start_time);

	free(array);

	exit(0); 
}

