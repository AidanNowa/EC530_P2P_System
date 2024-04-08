# EC530_P2P_System

## Overview

This project aims to develop a peer-to-peer (P2P) chat application that allows users to communicate directly with each other without the need for a centralized server. The application is designed to run in a terminal and enables users to initiate chat sessions, accept incoming chat requests, and exchange messages in real-time.

## Goals

* Peer-to-Peer Communication: Enable direct communication between users without the need for a centralized server.
* Real-time Messaging: Allow users to exhcange messages in real-time with other users currently logged in.
* User login: Have users login or register with a user/IP address that is accessible by other users.

## Current Features

* User Registration and Discovery: Users can register with thier IP address and discover others through a user registry stored locally.
* Initiating Chat Sessions: USers can start a chat session by sending requests to other users via thier username
* Real-time Messaging: Once a chat session is established, users can send and receive test messages in real-time.
* Flexible Server-Client Roles: The users that initiates the chat acts as the server and accepts connections while the receiving user connects as a client.

## How to Run

1.) Clone the Repo.
2.) Run the application by running the "user.py" python script.
'''
python user.py 
'''
3.) After launching you will be promted to either login or register within the command terminal. Follow prompts to login and begin chatting.

## Current Functionality

Currently the user.py application encounters connection issues when initiating chats. This issue appears to stem from thread synchronization causing the users inputs to be applied to the main menu when they should be used to accept/reject a chat request. 

However, the user_simple.py file showcases a simple case of the first user defaulting to the server after not connecting, and the second connecting automatically. This then allows the two applications to communicate as seen below:

![Simple_messages](https://github.com/AidanNowa/EC530_P2P_System/assets/98485635/1b25aeaf-5148-46dc-be52-0a7af71c0415)
