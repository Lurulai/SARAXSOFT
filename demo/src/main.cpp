#include <Arduino.h>

const int numPins = 6;

// LED pins
int ledPins[numPins] = {2, 4, 6, 8, 10, 12};

// Corresponding input pins
int inputPins[numPins] = {3, 5, 7, 9, 11, 13};

String inputString = "";     // A String to hold incoming data
bool stringComplete = false; // Whether the string is complete

void serialEvent()
{
    while (Serial.available())
    {
        // Get the new byte:
        char inChar = (char)Serial.read();
        // Add it to the inputString:
        inputString += inChar;
        // If the incoming character is a newline, set a flag so the main loop can
        // do something about it:
        if (inChar == '\n')
        {
            stringComplete = true;
        }
    }
}

void setLED(String params)
{
    // Params format: LED_INDEX STATE
    // Example: 3 ON
    int spaceIndex = params.indexOf(' ');
    if (spaceIndex == -1)
    {
        Serial.println("ERROR: Invalid SET_LED parameters");
        return;
    }

    int ledIndex = params.substring(0, spaceIndex).toInt();
    String state = params.substring(spaceIndex + 1);

    if (ledIndex < 0 || ledIndex >= numPins)
    {
        Serial.println("ERROR: Invalid LED index");
        return;
    }

    if (state == "ON")
    {
        digitalWrite(ledPins[ledIndex], HIGH);
        Serial.println("OK");
    }
    else if (state == "OFF")
    {
        digitalWrite(ledPins[ledIndex], LOW);
        Serial.println("OK");
    }
    else
    {
        Serial.println("ERROR: Invalid LED state");
    }
}

void getInputState(String params)
{
    // Params format: INPUT_INDEX
    // Example: 2
    int inputIndex = params.toInt();

    if (inputIndex < 0 || inputIndex >= numPins)
    {
        Serial.println("ERROR: Invalid input index");
        return;
    }

    int state = digitalRead(inputPins[inputIndex]);
    Serial.print("INPUT_STATE ");
    Serial.print(inputIndex);
    Serial.print(" ");
    Serial.println(state == HIGH ? "HIGH" : "LOW");
}

void parseCommand(String command)
{
    // Command format: ACTION PARAMETER
    // Example: SET_LED 3 ON
    int spaceIndex = command.indexOf(' ');
    if (spaceIndex == -1)
    {
        // Invalid command
        Serial.println("ERROR: Invalid command");
        return;
    }

    String action = command.substring(0, spaceIndex);
    String params = command.substring(spaceIndex + 1);

    if (action == "SET_LED")
    {
        setLED(params);
    }
    else if (action == "GET_INPUT")
    {
        getInputState(params);
    }
    else if (action == "PING")
    {
        Serial.println("PONG");
    }
    else
    {
        Serial.println("ERROR: Unknown action");
    }
}

void setup()
{
    Serial.begin(9600);       // Initialize serial communication
    inputString.reserve(200); // Reserve 200 bytes for the inputString

    // Initialize LED pins as outputs
    for (int i = 0; i < numPins; i++)
    {
        pinMode(ledPins[i], OUTPUT);
        digitalWrite(ledPins[i], LOW);
    }

    // Initialize input pins as inputs with pull-down resistors
    for (int i = 0; i < numPins; i++)
    {
        pinMode(inputPins[i], INPUT);
    }

    Serial.println("Arduino ready"); // Send a ready message
}

void loop()
{
    if (stringComplete)
    {
        inputString.trim();
        if (inputString.length() > 0)
        {
            parseCommand(inputString);
        }
        // Clear the string:
        inputString = "";
        stringComplete = false;
    }
}
