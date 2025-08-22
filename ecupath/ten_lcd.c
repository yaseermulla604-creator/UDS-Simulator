#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/i2c.h"
 
#define I2C i2c1
#define ADDRESS 0x27
#define SDA 2
#define SCL 3
 
void lcdCommand(uint8_t cmd) {
    uint8_t data[2] = {cmd & 0xF0, (cmd << 4) & 0xF0};
    for (int i = 0; i < 2; i++) {
        data[i] |= 0x0C;
        i2c_write_blocking(I2C, ADDRESS, &data[i], 1, false);
        data[i] &= 0xF8;
        i2c_write_blocking(I2C, ADDRESS, &data[i], 1, false);
    }
}
 
void lcdData(uint8_t data) {
    uint8_t highNibble = (data & 0xF0) | 0x0D;
    uint8_t lowNibble = ((data << 4) & 0xF0) | 0x0D;
    uint8_t bytes[] = {highNibble, highNibble & 0xFB, lowNibble, lowNibble & 0xFB};
    i2c_write_blocking(I2C, ADDRESS, bytes, 4, false);
}
 
void init() {
    sleep_ms(50);
    lcdCommand(0x03);
    sleep_ms(5);
    lcdCommand(0x03);
    sleep_us(150);
    lcdCommand(0x03);
    lcdCommand(0x02);
    lcdCommand(0x28);
    lcdCommand(0x0C);
    lcdCommand(0x06);
    lcdCommand(0x01);
    sleep_ms(5);
}
 
void lcdCursor(uint8_t row, uint8_t col) {
    uint8_t addr = (row == 0) ? (0x80 + col) : (0xC0 + col);
    lcdCommand(addr);
}
 
void lcdPrint(const char *str) {
    while (*str) {
        lcdData(*str++);
    }
}
 
int main() {
    stdio_init_all();
    i2c_init(I2C, 100000);
    gpio_set_function(SDA, GPIO_FUNC_I2C);
    gpio_set_function(SCL, GPIO_FUNC_I2C);
    gpio_pull_up(SDA);
    gpio_pull_up(SCL);
 
    init();
    lcdCursor(0, 0);
    lcdPrint("Mulla");
    lcdCursor(1, 0);
    lcdPrint("Yaseer");
   
    while (1) {
        sleep_ms(500);
    }
}