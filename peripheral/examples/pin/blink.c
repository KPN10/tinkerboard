// gcc -std=gnu11 -O0 blink.c -o blink -lwiringPi

#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <wiringPi.h>

#define LED 127

int main(void)
{
    printf("Tinker board 2 blink\n");
    wiringPiSetup();
    pinMode(LED, OUTPUT);

    while(true) {
        printf("LED - HIGH\n");
        digitalWrite(LED, HIGH);
        delay(500);
        printf("LED - LOW\n");
        digitalWrite(LED, LOW);
        delay(500);
    }

    return EXIT_SUCCESS;
}