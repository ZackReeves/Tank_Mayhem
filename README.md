Tank Mayhem
========

This repository contains the project files for Tank Mayhem, a multiplayer tank battle royale game developed as part of the 2nd year Information Processing module completed in spring 2022. The project involves an IoT system where up to 6 PCs, which act as nodes, communicate with a TCP server hosted on an AWS client. Each node uses an FPGA as a controller. The server then handles communication between the player nodes and sends and receives the required information between these nodes to run the game. Please find a brief guide to the repository below!

[**AWS**](AWS)
--------------

This directory contains the scripts and assets required on the AWS instance.

[**Local_Node**](Local_Node)
----------------------------

This directory contains all Python scripts and assets that are responsible for running the game and managing the connection between the player nodes and the TCP server.

[**Quartus**](Quartus)
----------------------

This directory contains the Quartus project files and platform designer files required for the FPGA controllers.
