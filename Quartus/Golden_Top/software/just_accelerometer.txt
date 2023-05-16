#include <sys/alt_stdio.h>
#include "system.h"
#include <stdio.h>
#include "altera_up_avalon_accelerometer_spi.h"
#include "altera_avalon_timer_regs.h"
#include "altera_avalon_timer.h"
#include "altera_avalon_pio_regs.h"
#include "sys/alt_irq.h"
#include <stdlib.h>

#define OFFSET -32
#define PWM_PERIOD 16

alt_8 pwm = 0;
alt_u8 led;
int level = 0;

void led_write(alt_u8 led_pattern) {
    IOWR(LED_BASE, 0, led_pattern);
}

void convert_read(alt_32 acc_read, int * level, alt_u8 * led) {
    acc_read += OFFSET;
    alt_u8 val = (acc_read >> 6) & 0x07;
    * led = (8 >> val) | (8 << (8 - val));
    * level = (acc_read >> 1) & 0x1f;
}

void sys_timer_isr() {
    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_BASE, 0);

    if (pwm < abs(level)) {

        if (level < 0) {
            led_write(led << 1);
        } else {
            led_write(led >> 1);
        }

    } else {
        led_write(led);
    }

    if (pwm > PWM_PERIOD) {
        pwm = 0;
    } else {
        pwm++;
    }

}

void timer_init(void * isr) {

    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_BASE, 0x0003);
    IOWR_ALTERA_AVALON_TIMER_STATUS(TIMER_BASE, 0);
    IOWR_ALTERA_AVALON_TIMER_PERIODL(TIMER_BASE, 0x0900);
    IOWR_ALTERA_AVALON_TIMER_PERIODH(TIMER_BASE, 0x0000);
    alt_irq_register(TIMER_IRQ, 0, isr);
    IOWR_ALTERA_AVALON_TIMER_CONTROL(TIMER_BASE, 0x0007);

}

int main() {
	int button_datain;
	double x[10] = {0};
	double x_average=0;
	double y[10] = {0};
	double y_average=0;
	int x_int, y_int;
    alt_32 x_read, y_read;
    alt_up_accelerometer_spi_dev * acc_dev;
    acc_dev = alt_up_accelerometer_spi_open_dev("/dev/accelerometer_spi");
    if (acc_dev == NULL) { // if return 1, check if the spi ip name is "accelerometer_spi"
    	alt_printf("Can't connect to Accelerometer!\n\r");
        return 1;
    }
    else{alt_printf("connected to accelerometer");}

    timer_init(sys_timer_isr);

    while (1) {
    	button_datain = IORD_ALTERA_AVALON_PIO_DATA(BUTTON_BASE);
        alt_up_accelerometer_spi_read_x_axis(acc_dev, & x_read);
        alt_up_accelerometer_spi_read_y_axis(acc_dev, & y_read);
        x_average = 0;
        y_average = 0;
        for (int i=9; i>0; i--){
        	x[i]=x[i-1];
        }
        for (int i=9; i>0; i--){
                	y[i]=y[i-1];
                }
        x[0]= x_read;
        y[0]= y_read;
        for (int i=0; i<10; i++){
        	x_average += x[i]*0.1;
        }
        for (int i=0; i<10; i++){
			y_average += y[i]*0.1;
		}
        x_int = x_average;
        y_int = y_average;
        alt_printf("<-->x: %x<-->y: %x<-->buttons: %x<-->\n", x_int, y_int, button_datain);
        convert_read(x_int, & level, & led);

    }

    return 0;
}

