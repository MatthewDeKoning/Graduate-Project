
/*******************************************************************************
#             uvccapture: USB UVC Video Class Snapshot Software                #
#This package work with the Logitech UVC based webcams with the mjpeg feature  #
#.                                                                             #
# 	Orginally Copyright (C) 2005 2006 Laurent Pinchart &&  Michel Xhaard   #
#       Modifications Copyright (C) 2006  Gabriel A. Devenyi                   #
#                                                                              #
# This program is free software; you can redistribute it and/or modify         #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation; either version 2 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# This program is distributed in the hope that it will be useful,              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with this program; if not, write to the Free Software                  #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    #
#                                                                              #
*******************************************************************************/
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <jpeglib.h>
#include <time.h>
#include <linux/videodev2.h>
#include <pthread.h>
#include <stdarg.h>

#include "v4l2uvc.h"

//figure out how to get UTC!!!!!

#define STARTX      77
#define ENDX        82
#define STARTY		57
#define ENDY		62

#define W           6
#define H			6
#define D			32
#define V			2
#define WIDTH		160
#define HEIGHT		120
#define MAGIC 		0.6745

static uint16_t previousValues[W][H][D][V];
static uint16_t currentValues[W][H];

static uint16_t MADArray[D];
static uint8_t alertCount;

struct pixelTracker{
	uint16_t median; 
	float mean;
	float stdDev;
	uint8_t index;
	uint8_t first;
};

static struct pixelTracker pixels[W][H];

uint8_t testValue(uint16_t value, uint8_t x, uint8_t y){
	float upper, lower, sixStdDev;
	sixStdDev = pixels[x][y].stdDev*6;
	upper = pixels[x][y].mean + sixStdDev;
	lower = pixels[x][y].mean - sixStdDev;
	if(value > upper){
		return 1;
	}
	else if(value < lower){
		return 1;
	}
	return 0;
}

void updatePixel(uint16_t value, uint8_t x, uint8_t y){
	if(pixels[x][y].index == D){
		updatePixelFull(value, x, y);
	}
	else{
		updatePixelFilling(value, x, y);
	}
	
}
float calculateMAD(uint8_t x, uint8_t y, uint16_t median, uint8_t index){
	uint8_t i, j;
	int16_t diff;
	for(i = 0; i < index; i++){
		diff = previousValues[x][y][i][0] - pixels[x][y].median;
		if(diff < 0){
			diff = ~diff + 1;
		}
		MADArray[i] = diff;
	}
	//now sort the list of differences
	for(i = 0; i < index; i++){
		for(j = 0; j < index; j++){
			if(MADArray[i] < MADArray[j]){
				diff = MADArray[i];
				MADArray[i] = MADArray[j];
				MADArray[j] = diff;
			}
		}
	}
	//return the median
	if (MADArray[index>>1] == 0){
		return 0.5;
	}
	return (float)MADArray[index>>1];
}
void updatePixelFilling(uint16_t value, uint8_t x, uint8_t y){
	uint8_t low, mid, high, i, j;
	struct pixelTracker * pixel;
	
	pixel = &pixels[x][y];
	
	high = pixel->index;
	low = 0; 
	mid = (low+high)>>1;
	while((high-low) > 1){
		if(value > previousValues[x][y][mid][0]){
			low = mid;
			mid = (low+high)>>1;
		}
		else{
			high = mid;
			mid = (low+high)>>1;
		}
	}
	if((previousValues[x][y][mid][0] < value) && (mid+1 <= pixel->index))
		mid+=1;
	else if((previousValues[x][y][mid][0] > value) && (mid-1 >= 0)){
		mid-=1;
	}
	
	for(j = pixel->index; j > mid; j--){
		previousValues[x][y][j][0] = previousValues[x][y][j-1][0];
		previousValues[x][y][j][1] = previousValues[x][y][j-1][1];
		if(previousValues[x][y][j][1] == 1){
			pixel->first = j;
		}
	}
	pixel->index++;
	previousValues[x][y][mid][0] = value;
	previousValues[x][y][mid][1] = pixel->index;
	pixel->mean = (pixel->mean*(pixel->index-1) + value)/pixel->index;
	pixel->median = previousValues[x][y][(pixel->index)>>1][0];
	pixel->stdDev = calculateMAD(x, y, pixel->median, pixel->index)/ MAGIC;
	
}

void updatePixelFull(uint16_t value, uint8_t x, uint8_t y){
	uint8_t low, mid, high, i, j, f;
	uint32_t currentTotal;
	struct pixelTracker * pixel;
	
	pixel = &pixels[x][y];
	
	f = pixel->first;
	previousValues[x][y][f][0] = 0;
	previousValues[x][y][f][1] = -1;
	
	currentTotal = 0;
	
	for(i = 0; i < 31; i++){
		if(i < f){
			currentTotal+=previousValues[x][y][i][0];
			previousValues[x][y][i][1]--;
			if(previousValues[x][y][i][1] == 1){
				pixel->first = i;
			}
		}
		else{
			previousValues[x][y][i][0] = previousValues[x][y][i+1][0];
			previousValues[x][y][i][1] = previousValues[x][y][i+1][1];
			currentTotal+=previousValues[x][y][i][0];
			previousValues[x][y][i][1]--;
			if(previousValues[x][y][i][1] == 1){
				pixel->first = i;
			}
		}
	}
	
	low = 0;
	high = D-1;
	mid = (low+high)>>1;
	while((high-low) > 1){
		if(value > previousValues[x][y][mid][0]){
			low = mid;
			mid = (low+high)>>1;
		}
		else{
			high = mid;
			mid = (low+high)>>1;
		}
	}
	if((previousValues[x][y][mid][0] < value) && (mid+1 <= pixel->index))
		mid+=1;
	
	for(i = 31; i > mid; i--){
		previousValues[x][y][i][0] = previousValues[x][y][i-1][0];
		previousValues[x][y][i][1] = previousValues[x][y][i-1][1];
		if(previousValues[x][y][i][1] == 1){
			pixel->first = i;
		}
	}
	
	previousValues[x][y][mid][0] = value;
	previousValues[x][y][mid][1] = D;
	
	pixel->mean = (currentTotal + value) >> 5;;
	pixel->median = previousValues[x][y][15][0];
	
	
	pixel->stdDev = calculateMAD(x, y, pixel->median, 32)/ MAGIC;
}
void updateAndCheck(char * videodevice){
	uint8_t i, j, alert;
	alertCount = 0;
	for(i = 0; i < W; i++){
		for(j = 0; j < H; j++){
			//DO SOMETHING WIHT ALERT
			alert = testValue(currentValues[i][j], i, j);
			if(alert){
				alertCount++;
			}
			updatePixel(currentValues[i][j], i, j);
		}
	}
}

void printMAD(){
	int i;
	printf("MAD %d\n", calculateMAD(0,0, pixels[0][0].median, pixels[0][0].index));
	for(i = 0; i < pixels[0][0].index; i++){
		printf("%i ", MADArray[i]);
	}
	printf("\n");
}
void printArray(){
	int j, k, l;
	//for(i = 0; i < W; i++){
		//for(j = 0; j < H; j++){
			for(k = 0; k < D; k++){
				for(l = 0; l < V; l++){
					printf("%d ", previousValues[0][0][k][l]);
				}
				printf("\n");
			}
		//}
	//}
	printf("MEAN: %f\nMEDIAN: %d\nSTDDEV %f\n", pixels[0][0].mean, pixels[0][0].median, pixels[0][0].stdDev);
	printf("\n\n");
}

void initValues(){
	int i, j, k, l;
	for(i = 0; i < W; i++){
		for(j = 0; j < H; j++){
			for(k = 0; k < D; k++){
				for(l = 0; l < V; l++){
					previousValues[i][j][k][l] = 0;
				}
			}
		}
	}
}
static pthread_mutex_t printf_mutex;
int sync_printf(const char *format, ...)
{
    va_list args;
    va_start(args, format);

    pthread_mutex_lock(&printf_mutex);
    vprintf(format, args);
    pthread_mutex_unlock(&printf_mutex);

    va_end(args);
}

//make this loop handle all camera grabs
void
*camera ( char * videodevice)
{
	int format = 1;
	int grabmethod = 1;
	int width = WIDTH;
	int height = HEIGHT;
	struct vdIn *videoIn;
	int i, j, k;
	uint16_t value;
	int count = 0;
	clock_t t0, t1;
	int index_1, index_2, index;
	int run = 1;
	FILE *f;
	//initialize the array to 0
	initValues();

	//set up the video structure
	videoIn = (struct vdIn *) calloc (1, sizeof (struct vdIn));
	if (init_videoIn(videoIn, (char *) videodevice, width, height, format, grabmethod) < 0){
		exit (1);
	}
	//begin grabbing data
	if(videodevice[10] == '0'){
		f = fopen("output0.txt", "a");
	}
	else{
		f = fopen("output1.txt", "a");
	}
	while(run){
		if (uvcGrab (videoIn) < 0) {
		    printf ( "Error grabbing\n");
		    close_v4l2 (videoIn);
		    free (videoIn);
		    exit (1);
		}
		//get the data from the image
		index_1 = STARTY*160 + STARTX;
		index_2 = ENDY*160 + ENDX;
		index = index_1;
		i = 0; 
		j = 0;
		for(k = 0; k < ((160*120)); k++){
			value = (uint16_t)(videoIn->framebuffer[2*k] + (videoIn->framebuffer[2*k+1]<<8));
			if(k == index && index <= index_2){
				currentValues[i][j] = value;
				i++;
				index++;
				if((index - index_1) == W){
					index_1+=160;
					index = index_1;
					i = 0;
					j++;
				}
			}
	    }
		updateAndCheck(videodevice);
		//printf("AlertCount %i\n", alertCount);
		//printArray();
		fprintf(f, "hey\n");
		if(alertCount > 5 && pixels[0][0].index == D){
			sync_printf("INTRUSION %s %u\n", videodevice, time(NULL));
		}
	    t0 = clock();
		//sync_printf("Count %s %i\n", videodevice, count);
		count++;
	    //run = 0;//printf("Count: %i   %d\n", count, t0);
	}
	printf("t %i\n%s", t0, videodevice);
	
	pthread_exit(NULL);
}


int
main (int argc, char *argv[])
{
	int rc;
	pthread_t thread1, thread2;
	//camera();
	camera("/dev/video1");
	//rc = pthread_create(&thread1, NULL, camera, (char *)"/dev/video0");
	//rc = pthread_create(&thread2, NULL, camera, (char *)"/dev/video1");
    if (rc){
        printf("ERROR; return code from pthread_create() is %d\n", rc);
        while(1){};
    }
	pthread_exit(NULL);
}