# g2_socio_griefbots

Basic Python repo for a Sciences Po academic project in Sociology of the Public Digital Space.
## Overview

The point of the project is to study the evolution of mourning practices at the era of digital technologies, with a focus on the use of griefbots (chatbots designed to simulate conversations with deceased individuals) on social media platforms. 
The project aims to analyze how these technologies impact the grieving process and the social dynamics surrounding death and mourning in online spaces.

As such, Reddit is used as a data source, given its wide range of communities and discussions related to grief and mourning, especially on r/ProjectDecember1982 & r/GriefSupport.
The posts are collected using the PRAW (Python Reddit API Wrapper) library, which allows for easy access to Reddit's API.

## Requirements
- Python 3.x
- PRAW library
- Reddit's API credentials (client_id, client_secret) --> ask Barthélemy for these

## Run the Code
1. Clone the repository to your local machine.
2. Get Reddit API credentials and set them up in a ".env" file. 
3. Run main.py. 