/*
#include <iostream>
#include <fstream>
#include <cmath>
#include "MCP2210-Library/mcp2210.h"

int binary_to_decimal(unsigned int b3, unsigned int b2, int unsigned b1, unsigned int b0) {
    return b3 * pow(2, 3) + b2 * pow(2, 2) + b1 * pow(2, 1) + b0 * pow(2, 0);
}

int main(int argc, char** argv) {
    // Open the serial port
//    std::ofstream serial_port("/dev/ttyS0");  // Replace /dev/ttyS0 with your serial port
//    if (!serial_port.is_open()) {
//        std::cerr << "Failed to open serial port!" << std::endl;
//        return 1;
//    }

    int r = 0;

    hid_device *handle;

    */
/**
     * initializing the MCP2210 device.
     *//*

    handle = InitMCP2210();
    if (handle == NULL) {
        std::cerr << "Failed to initialize MCP2210!!!!" << std::endl;
        return 1;  // exit the program if initialization fails
    }
    printf("Hello world\n");

    */
/**
     * Configure GPIO0 direction to output
     *//*

    GPPinDef def = GetGPIOPinDirection(handle);
    printf("Hello world 2\n");
    def.GP[0].GPIODirection = GPIO_DIRECTION_OUTPUT;
    */
/*def.GP[1].GPIODirection = GPIO_DIRECTION_OUTPUT;
    def.GP[2].GPIODirection = GPIO_DIRECTION_OUTPUT;
    def.GP[3].GPIODirection = GPIO_DIRECTION_OUTPUT;*//*

    printf("Hello world 3\n");


    r = SetGPIOPinDirection(handle, def);
//    def.GP[0].GPIOOutput = 0; // Explicit initialization to 0
    //printf("GPIO0 Direction: %u\n", def.GP[0].GPIODirection);
    int direction = 1; // 1 for increasing, -1 for decreasing
    unsigned int counter = 1;  // Starting from 0001 (1 in decimal)
    ///< Generate a rectangular wave by toggling GP0.
    while (1)  {
        def.GP[0].GPIOOutput = 1-def.GP[0].GPIOOutput;
//        def.GP[0].GPIOOutput = (def.GP[0].GPIOOutput == 1) ? 0 : 1;
        */
/*def.GP[0].GPIOOutput = 1;
        def.GP[1].GPIOOutput = 0;
        def.GP[2].GPIOOutput = 0;
        def.GP[3].GPIOOutput = 0;
        // Set the GPIO values based on the 4-bit counter
//        def.GP[0].GPIOOutput = (counter & 0x01) ? 1 : 0;  // LSB (GPIO0)
//        def.GP[1].GPIOOutput = (counter & 0x02) ? 1 : 0;  // GPIO1
//        def.GP[2].GPIOOutput = (counter & 0x04) ? 1 : 0;  // GPIO2
//        def.GP[3].GPIOOutput = (counter & 0x08) ? 1 : 0;  // MSB (GPIO3)
        printf("-------------------new--------------------------\n");
        printf("Toggling GP[0] Output to: %u\n", def.GP[0].GPIOOutput);
        printf("Toggling GP[1] Output to: %u\n", def.GP[1].GPIOOutput);
        printf("Toggling GP[2] Output to: %u\n", def.GP[2].GPIOOutput);
        printf("Toggling GP[3] Output to: %u\n", def.GP[3].GPIOOutput);
        printf("Message to send: %u%u%u%u\n", def.GP[3].GPIOOutput, def.GP[2].GPIOOutput, def.GP[1].GPIOOutput, def.GP[0].GPIOOutput);

        printf("In decimal: %d\n", binary_to_decimal(def.GP[3].GPIOOutput, def.GP[2].GPIOOutput, def.GP[1].GPIOOutput, def.GP[0].GPIOOutput));*//*


        r = SetGPIOPinVal(handle, def);
        */
/*if (r != 0) {
            printf("Failed to set GPIO Pin Value! Error: %d\n", r);
        } else {
            //printf("Successfully set GPIO Pin Value.\n");
        }
        //printf("Hello world 4\n");
//        counter = (counter == 12) ? 1 : counter + 1;
        if (counter == 12) {
            direction = -1; // Start decreasing
        } else if (counter == 1) {
            direction = 1; // Start increasing
        }
        counter += direction;
        usleep(500000); // 500ms*//*

    }



    */
/**
     * release the handle
     *//*

    ReleaseMCP2210(handle);

    return 0;
}
*/
#include "MCP2210-Library/mcp2210.h"

int main(int argc, char** argv) {
    int r = 0;

    hid_device *handle;

    /**
     * initializing the MCP2210 device.
     */
    handle = InitMCP2210();

    /**
     * Configure GPIO0 direction to output
     */
    GPPinDef def = GetGPIOPinDirection(handle);
    def.GP[0].PinDesignation = 0x00;
    def.GP[1].PinDesignation = 0x00;
    def.GP[2].PinDesignation = 0x00;
    def.GP[3].PinDesignation = 0x00;
    def.GP[4].PinDesignation = 0x00;
    def.GP[5].PinDesignation = 0x00;
    def.GP[6].PinDesignation = 0x00;
    def.GP[7].PinDesignation = 0x00;
    def.GP[8].PinDesignation = 0x00;

    def.GP[0].GPIODirection = GPIO_DIRECTION_OUTPUT;
    def.GP[1].GPIODirection = GPIO_DIRECTION_OUTPUT;
    def.GP[2].GPIODirection = GPIO_DIRECTION_OUTPUT;
    def.GP[3].GPIODirection = GPIO_DIRECTION_OUTPUT;
    def.GP[5].GPIODirection = GPIO_DIRECTION_OUTPUT;
    def.GP[6].GPIODirection = GPIO_DIRECTION_OUTPUT;
    def.GP[7].GPIODirection = GPIO_DIRECTION_OUTPUT;
    def.GP[8].GPIODirection = GPIO_DIRECTION_OUTPUT;
    def.GP[4].GPIODirection = GPIO_DIRECTION_OUTPUT;

    r = SetGPIOPinDirection(handle, def);

    ///< Generate a rectangular wave by toggling GP0.
    while (1)  {
//        def.GP[0].GPIOOutput = 0;
        def.GP[0].GPIOOutput = 1-def.GP[0].GPIOOutput;
        def.GP[1].GPIOOutput = 1-def.GP[1].GPIOOutput;
        def.GP[2].GPIOOutput = 1-def.GP[2].GPIOOutput;
        def.GP[3].GPIOOutput = 1-def.GP[3].GPIOOutput;
        def.GP[5].GPIOOutput = 1-def.GP[5].GPIOOutput;
        def.GP[6].GPIOOutput = 1-def.GP[6].GPIOOutput;
        def.GP[7].GPIOOutput = 1-def.GP[7].GPIOOutput;
        def.GP[8].GPIOOutput = 1-def.GP[8].GPIOOutput;
        def.GP[4].GPIOOutput = 1-def.GP[4].GPIOOutput;
        //        def.GP[2].GPIOOutput = 0;
//        def.GP[3].GPIOOutput = 0;
        r = SetGPIOPinVal(handle, def);
    }

    /**
     * release the handle
     */
    ReleaseMCP2210(handle);

    return 0;
}
