# Fred Factory
Fred Factory is a initiative between Tec de Monterrey and Massachussets Institute of Technology to develop an educative platform for engineering students to learn on advanced factory tools like Computer Vision, Internet of Things, Control Systems, etc.
## Clone the repository
```bash
git clone https://github.com/JuanSanCH/Fred_Factory_Tec.git
```
---------------------------------------------------------------------------
                Requirements: Have Arduino and Terminator 
---------------------------------------------------------------------------



Before running the code to control the FrED from internet, make sure you are connected to a hotspot and be sure ypu have already uploaded the code on arduino...

-----------------------------Thinger terminals----------------------------

To run the thinger terminal follow next steps:

    1.Set the terminator terminal to the same folder [Terminal_code]
        cd Terminal_code

    2.Split the terminal into 3 terminals. (All terminals must be set to Terminal_code/)
    
    3.Start in the first terminal the Serial_manager code:
        python3 lib_iot\serial_manager.py
        (You must be able to see "Esperando conexion...")
    
    4.Start in the second terminal the Diameter sensor code:
        python3 lib_sd\diameter_sensor.py
        (You must be able to see "Esperando conexion...")
    
    5.Start the last terminal which connects all:
        python3 lib_iot\thinger_client\run.sh

--------------------------------- PyQt Control Interphase ------------------------------