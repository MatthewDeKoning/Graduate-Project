
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
#define CAMERAS		4
#define MAGIC 		0.6745

void updatePixelFilling(uint16_t value, uint8_t x, uint8_t y, uint8_t camera);
void updatePixelFull(uint16_t value, uint8_t x, uint8_t y, uint8_t camera);

static uint16_t previousValues[CAMERAS][W][H][D][V];
static uint16_t currentValues[CAMERAS][W][H];

static uint16_t MADArray[CAMERAS][D];
static uint8_t alertCount;

struct pixelTracker{
	uint16_t median; 
	float mean;
	float stdDev;
	uint8_t index;
	uint8_t first;
};

static struct pixelTracker pixels[CAMERAS][W][H];

uint8_t testValue(uint16_t value, uint8_t x, uint8_t y, uint8_t camera){
	float upper, lower, sixStdDev;
	sixStdDev = pixels[camera][x][y].stdDev*6;
	upper = pixels[camera][x][y].mean + sixStdDev;
	lower = pixels[camera][x][y].mean - sixStdDev;
	if(value > upper){
		return 1;
	}
	else if(value < lower){
		return 1;
	}
	return 0;
}

void updatePixel(uint16_t value, uint8_t x, uint8_t y, uint8_t camera){
	if(pixels[camera][x][y].index == D){
		updatePixelFull(value, x, y, camera);
	}
	else{
		updatePixelFilling(value, x, y, camera);
	}
	
}
float calculateMAD(uint8_t x, uint8_t y, uint16_t median, uint8_t index, uint8_t camera){
	uint8_t i, j;
	int16_t diff;
	for(i = 0; i < index; i++){
		diff = previousValues[camera][x][y][i][0] - pixels[camera][x][y].median;
		if(diff < 0){
			diff = ~diff + 1;
		}
		MADArray[camera][i] = diff;
	}
	//now sort the list of differences
	for(i = 0; i < index; i++){
		for(j = 0; j < index; j++){
			if(MADArray[camera][i] < MADArray[camera][j]){
				diff = MADArray[camera][i];
				MADArray[camera][i] = MADArray[camera][j];
				MADArray[camera][j] = diff;
			}
		}
	}
	//return the median
	if (MADArray[camera][(index>>1)] == 0){
		return 0.5;
	}
	return (float)MADArray[camera][index>>1];
}
void updatePixelFilling(uint16_t value, uint8_t x, uint8_t y, uint8_t camera){
	uint8_t low, mid, high, j;
	struct pixelTracker * pixel;
	
	pixel = &pixels[camera][x][y];
	
	high = pixel->index;
	low = 0; 
	mid = (low+high)>>1;
	while((high-low) > 1){
		if(value > previousValues[camera][x][y][mid][0]){
			low = mid;
			mid = (low+high)>>1;
		}
		else{
			high = mid;
			mid = (low+high)>>1;
		}
	}
	if((previousValues[camera][x][y][mid][0] < value) && (mid+1 <= pixel->index))
		mid+=1;
	else if((previousValues[camera][x][y][mid][0] > value) && (mid-1 >= 0)){
		mid-=1;
	}
	
	for(j = pixel->index; j > mid; j--){
		previousValues[camera][x][y][j][0] = previousValues[camera][x][y][j-1][0];
		previousValues[camera][x][y][j][1] = previousValues[camera][x][y][j-1][1];
		if(previousValues[camera][x][y][j][1] == 1){
			pixel->first = j;
		}
	}
	pixel->index++;
	previousValues[camera][x][y][mid][0] = value;
	previousValues[camera][x][y][mid][1] = pixel->index;
	pixel->mean = (pixel->mean*(pixel->index-1) + value)/pixel->index;
	pixel->median = previousValues[camera][x][y][(pixel->index)>>1][0];
	pixel->stdDev = calculateMAD(x, y, pixel->median, pixel->index, camera) / MAGIC;
	
}

void updatePixelFull(uint16_t value, uint8_t x, uint8_t y, uint8_t camera){
	uint8_t low, mid, high, i, j, f;
	uint32_t currentTotal;
	struct pixelTracker * pixel;
	
	pixel = &pixels[camera][x][y];
	
	f = pixel->first;
	previousValues[camera][x][y][f][0] = 0;
	previousValues[camera][x][y][f][1] = -1;
	
	currentTotal = 0;
	
	for(i = 0; i < 31; i++){
		if(i < f){
			currentTotal+=previousValues[camera][x][y][i][0];
			previousValues[camera][x][y][i][1]--;
			if(previousValues[camera][x][y][i][1] == 1){
				pixel->first = i;
			}
		}
		else{
			previousValues[camera][x][y][i][0] = previousValues[camera][x][y][i+1][0];
			previousValues[camera][x][y][i][1] = previousValues[camera][x][y][i+1][1];
			currentTotal+=previousValues[camera][x][y][i][0];
			previousValues[camera][x][y][i][1]--;
			if(previousValues[camera][x][y][i][1] == 1){
				pixel->first = i;
			}
		}
	}
	
	low = 0;
	high = D-1;
	mid = (low+high)>>1;
	while((high-low) > 1){
		if(value > previousValues[camera][x][y][mid][0]){
			low = mid;
			mid = (low+high)>>1;
		}
		else{
			high = mid;
			mid = (low+high)>>1;
		}
	}
	if((previousValues[camera][x][y][mid][0] < value) && (mid+1 <= pixel->index))
		mid+=1;
	
	for(i = 31; i > mid; i--){
		previousValues[camera][x][y][i][0] = previousValues[camera][x][y][i-1][0];
		previousValues[camera][x][y][i][1] = previousValues[camera][x][y][i-1][1];
		if(previousValues[camera][x][y][i][1] == 1){
			pixel->first = i;
		}
	}
	
	previousValues[camera][x][y][mid][0] = value;
	previousValues[camera][x][y][mid][1] = D;
	
	pixel->mean = (currentTotal + value) >> 5;;
	pixel->median = previousValues[camera][x][y][15][0];
	calculateMAD(x, y, pixel->median, 32, camera);
	pixel->stdDev = MADArray[camera][16]/ MAGIC;
}
void updateAndCheck(uint8_t camera){
	uint8_t i, j;
	alertCount = 0;
	for(i = 0; i < W; i++){
		for(j = 0; j < H; j++){
			if(testValue(currentValues[camera][i][j], i, j, camera)){
				alertCount++;
			}
			updatePixel(currentValues[camera][i][j], i, j, camera);
		}
	}
}

void printMAD(uint8_t camera){
	int i;
	printf("MAD %d %i\n", MADArray[camera][16], (32>>1));
	for(i = 0; i < pixels[camera][0][0].index; i++){
		printf("%i ", MADArray[camera][i]);
	}
	printf("\n");
}
void printArray(uint8_t camera){
	int j, k, l;
	//for(i = 0; i < W; i++){
		//for(j = 0; j < H; j++){
			for(k = 0; k < D; k++){
				for(l = 0; l < V; l++){
					printf("%d ", previousValues[camera][0][0][k][l]);
				}
				printf("\n");
			}
		//}
	//}
	printf("MEAN: %f\nMEDIAN: %d\nSTDDEV %f\n", pixels[camera][0][0].mean, pixels[camera][0][0].median, pixels[camera][0][0].stdDev);
	printf("alert %i\n", testValue(currentValues[camera][0][0], 0, 0, camera));
	printf("\n\n");
}

void initValues(){
	int i, j, k, l, m;
	for(m = 0; m < CAMERAS; m++){
		for(i = 0; i < W; i++){
			for(j = 0; j < H; j++){
				for(k = 0; k < D; k++){
					for(l = 0; l < V; l++){
						previousValues[m][i][j][k][l] = 0;
					}
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

const char *devices[4] = {"/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3"};

void
*cameras ( uint8_t cameras)
{
	int format = 1;
	int grabmethod = 1;
	int width = WIDTH;
	int height = HEIGHT;
	struct vdIn *videoIn[CAMERAS];
	int i, j, k, c;
	uint16_t value;
	int count = 0;
	clock_t times[CAMERAS];
	int index_1, index_2, index;
	int run = 1;
	/*
	FILE *f1 = fopen('output0.txt', 'w');
	FILE *f2 = fopen('output2.txt', 'w');
	FILE *f3 = fopen('output3.txt', 'w');
	FILE *f4 = fopen('output4.txt', 'w');*/
	//initialize the array to 0
	initValues();
    printf("CLOCKS PER SECOND %u\n", CLOCKS_PER_SEC);
	//set up the video structure
	for(c = 0; c < cameras; c++){
		printf("%s started\n", devices[c]);
		videoIn[c] = (struct vdIn *) calloc (1, sizeof (struct vdIn));
		if (init_videoIn(videoIn[c], (char *) devices[c], width, height, format, grabmethod) < 0){
			exit (1);
		}

	}
	/*
	//begin grabbing data
	if(videodevice[10] == '0'){
		f = fopen("output0.txt", "a");
	}
	else{
		f = fopen("output1.txt", "a");
	}*/
	while(run){
		for(c = 0; c < cameras; c++){
			//printf("%i\n", c);
			if (uvcGrab (videoIn[c]) < 0) {
				printf ( "Error grabbing %i\n", c);
				close_v4l2 (videoIn[c]);
				free (videoIn[c]);
				exit (1);
			}
			//get the data from the image
			index_1 = STARTY*160 + STARTX;
			index_2 = ENDY*160 + ENDX;
			index = index_1;
			i = 0; 
			j = 0;
			k = index_1;
			while(k <= index_2){
				value = (uint16_t)(videoIn[c]->framebuffer[2*k] + (videoIn[c]->framebuffer[2*k+1]<<8));
				k++;
				//printf("%i\n", value);
				currentValues[c][i][j] = value;
				i++;
				index++;
				
				if((k - index_1) == W){
					index_1+=160;
					k = index_1;
					i = 0;
					j++;
				}
			}
			times[c] = clock();
			if(c == 0){
				printf("TIME %i\n", times[c]);
			}
		}
		for(c = 0; c < cameras; c++){
			updateAndCheck(c);
			if(alertCount > 20 && pixels[c][0][0].index == D){
				//printf("INTRUSION %s %u %i\n", devices[c], times[c], alertCount);
				//printArray(c);
				//printMAD(c);
				//printf("\n\n");
			}
		}
		count++;
		//run = 0;
	}	
}
int
main (int argc, char *argv[])
{
	//doesn't return
	cameras(2);
}