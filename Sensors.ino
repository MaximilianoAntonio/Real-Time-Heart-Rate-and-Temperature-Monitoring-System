// Pines analógicos para los sensores
const int pinPulso = A0;
const int pinNTC = A1;

// Constantes para el cálculo de temperatura
const float c1 = 2.108508173e-03;
const float c2 = 0.7979204727e-04;
const float c3 = 6.535076315e-07;
const float R1 = 10000;  // Resistencia fija del divisor de tensión

unsigned long tiempoAnterior = 0;
const unsigned long intervaloMuestreo = 5; // Intervalo de muestreo en milisegundos (5 ms = 200 Hz)

void setup() {
  Serial.begin(9600); // Iniciar el monitor serie a 115200 baudios
}

void loop() {
  // Obtener el tiempo actual
  unsigned long tiempoActual = millis();

  // Verificar si ha pasado el intervalo de muestreo
  if (tiempoActual - tiempoAnterior >= intervaloMuestreo) {
    // Actualizar el tiempo anterior al tiempo actual
    tiempoAnterior = tiempoActual;

    // Leer el valor del sensor de pulso
    int valorPulso = analogRead(pinPulso);

    // Leer el valor del NTC
    int valorNTC = analogRead(pinNTC);

    // Calcular la resistencia del NTC
    float resistenciaNTC = R1 * (1023.0 / valorNTC - 1);

    // Calcular la temperatura usando la ecuación del termistor
    float logR = log(resistenciaNTC);
    float temperaturaKelvin = 1.0 / (c1 + c2 * logR + c3 * logR * logR * logR);
    float temperaturaCelsius = temperaturaKelvin - 273.15;

    // Mostrar los valores en el monitor serie
    Serial.print("Pulso: ");
    Serial.print(valorPulso);
    Serial.print(" - Temperatura: ");
    Serial.print(temperaturaCelsius);
    Serial.println(" ºC");
  }
}
