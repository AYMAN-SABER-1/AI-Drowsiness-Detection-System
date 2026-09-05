#if __has_include(<Arduino.h>)
#include <Arduino.h>
#else
#include <cstddef>
#include <cstdint>

class HardwareSerial
{
public:
    void begin(unsigned long baud);
    int available();
    int read();
    std::size_t println(const char *text);
    std::size_t println(char value);
    std::size_t print(const char *text);
};

extern HardwareSerial Serial;

void pinMode(std::uint8_t pin, std::uint8_t mode);
void digitalWrite(std::uint8_t pin, std::uint8_t value);
void delay(unsigned long milliseconds);

constexpr std::uint8_t INPUT = 0;
constexpr std::uint8_t OUTPUT = 1;
constexpr std::uint8_t LOW = 0;
constexpr std::uint8_t HIGH = 1;
#endif

constexpr uint8_t LED_PIN = 12;
constexpr uint8_t BUZZER_PIN = 13;

constexpr unsigned long BUZZER_DURATION_MS = 200;

void setLed(bool state)
{
    digitalWrite(LED_PIN, state ? HIGH : LOW);
}

void triggerBuzzer()
{
    digitalWrite(BUZZER_PIN, HIGH);
    delay(BUZZER_DURATION_MS);
    digitalWrite(BUZZER_PIN, LOW);
}

void handleCommand(char command)
{
    switch (command)
    {
        case '1':
            setLed(true);
            Serial.println("LED ON");
            break;

        case '0':
            setLed(false);
            Serial.println("LED OFF");
            break;

        case 'B':
            triggerBuzzer();
            Serial.println("BUZZER TRIGGERED");
            break;

        default:
            Serial.print("UNKNOWN COMMAND: ");
            Serial.println(command);
            break;
    }
}

void setup()
{
    Serial.begin(115200);

    pinMode(LED_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    setLed(false);
    digitalWrite(BUZZER_PIN, LOW);

    Serial.println("EYE ALERT ESP32 READY");
}

void loop()
{
    if (Serial.available() > 0)
    {
        char command = Serial.read();
        handleCommand(command);
    }
}