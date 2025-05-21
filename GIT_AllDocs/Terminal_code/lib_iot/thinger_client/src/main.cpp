#include "thinger/thinger.h"    
#include <iostream>
#include <string>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <chrono>
#include <thread>
#define USER_ID             "FredFactory"
#define DEVICE_ID           "Raspberry"
#define DEVICE_CREDENTIAL   "FRED_RASP"

int main() {
    thinger_device thing(USER_ID, DEVICE_ID, DEVICE_CREDENTIAL);
    int sockA = 0; // Socket para recibir datos
    int sockB = 0; // Socket para enviar respuestas
    int sockC = 0;
    struct sockaddr_in serv_addr;
    char buffer[1024] = {0};
    char buffer2[1024] = {0};
    float temperatura = 0; 
    float diametro = 0.4;
    bool mot_value = false, fan_value = false, ext_value = false, hea_value = false; 

    // Configuración del socket A (recepción)
    if ((sockA = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        std::cerr << "Error al crear el socket A" << std::endl;
        return -1;
    }
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(65432);  // Puerto del servidor Python para Socket A

    // Convierte la IP del servidor a binario
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        std::cerr << "Dirección inválida / Dirección no soportada" << std::endl;
        close(sockA);
        return -1;
    }
  
    // Conexión al servidor para Socket A
    if (connect(sockA, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cerr << "Conexión fallida al socket A" << std::endl;
        close(sockA);
        return -1;
    }
    std::cout << "Conectado al servidor (Socket A)" << std::endl;

    // Configuración del socket B (envío de respuestas)
    if ((sockB = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        std::cerr << "Error al crear el socket B" << std::endl;
        close(sockA);
        return -1;
    }
    serv_addr.sin_port = htons(65433);  // Puerto del servidor Python para Socket B

    // Conexión al servidor para Socket B
    if (connect(sockB, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cerr << "Conexión fallida al socket B" << std::endl;
        close(sockB);
        return -1;
    }

    std::cout << "Conectado al servidor (Socket B)" << std::endl;

    // Configuración del socket C (recepción)
    if ((sockC = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        std::cerr << "Error al crear el socket C" << std::endl;
        return -1;
    }
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(65434);  // Puerto del servidor Python para Socket C
    
    // Conexión al servidor para Socket C
    if (connect(sockC, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        std::cerr << "Conexión fallida al socket C" << std::endl;
        close(sockC);
        return -1;
    }
    std::cout << "Conectado al servidor (Socket C)" << std::endl;

    // Definir recursos en Thinger
    thing["temperatura"] >> [&](pson& out) {
            out = temperatura;
        };
    thing["diametro"] >> [&](pson& out) {
            out = diametro;
        };        
    thing["Motor_spool"] << [&](pson& in) {
        if(in.is_empty()){
        in = mot_value;
        }
        else{
        mot_value = in;
    }
        }; 
    thing["Fan"] << [&](pson& in) {
        if(in.is_empty()){
        in = fan_value ;
        }
        else{
        fan_value = in;
    }
        };
    thing["Extruder"] << [&](pson& in) {
        if(in.is_empty()){
        in = ext_value;
        }
        else{
        ext_value = in;
    }
        };
    thing["Heater"] << [&](pson& in) {
        if(in.is_empty()){
        in = hea_value;
        }
        else{
        hea_value= in;
    }
        };
    while (true) {
        int valread = read(sockA, buffer, 1024);   
        if (valread > 0) {
            buffer[valread] = '\0';  // Termina el mensaje recibido
            std::string mensaje(buffer);            // Validar el mensaje antes de convertirlo a número
            temperatura = std::stof(mensaje);
        } else if (valread == 0) {
            std::cerr << "Conexión cerrada por el servidor (Socket A)." << std::endl;
            break;  // Sal del bucle si el servidor cierra la conexión
        } else {
            perror("Error al leer de Socket A");
            std::cerr << "Error en read: código " << errno << std::endl;
            break;  // Sal del bucle si es un error crítico
        }

        int val2read = read(sockC, buffer2, 1024);
        if (val2read > 0) {
            buffer2[val2read] = '\0';
            std::string mensaje2(buffer2);

            // Validar el mensaje antes de convertirlo a número
            try {
                diametro = std::stof(mensaje2);
            } catch (const std::exception& e) {
                std::cerr << "Error al convertir mensaje recibido a número: " << mensaje2 << ". Error: " << e.what() << std::endl;
                continue;  // Ignorar este mensaje y seguir leyendo
            }
        } else if (val2read == 0) {
            std::cerr << "Conexión cerrada por el servidor (Socket C)." << std::endl;
            break;  // Sal del bucle si el servidor cierra la conexión
        } else {
            perror("Error al leer de Socket C");
            std::cerr << "Error en read: código " << errno << std::endl;
            break;  // Sal del bucle si es un error crítico
        }

    // Enviar respuesta por Socket B
        const bool response[] = {mot_value, fan_value, ext_value, hea_value};          
        std::string response_str = "ACTUATE:";
        for (size_t i = 0; i < sizeof(response) / sizeof(response[0]); ++i) {
            response_str += response[i] ? '1' : '0';
        }
        response_str += '#';
        send(sockB, response_str.c_str(), response_str.size(), 0);

        // Manejo de Thinger
    thing.handle();
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    // Cerrar conexiones al finalizar
    }
    close(sockA);
    close(sockB);
    close(sockC);
}


