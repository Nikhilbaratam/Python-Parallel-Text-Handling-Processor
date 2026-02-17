# Python-Parallel-Text-Handling-Processor
Project Title
Python Parallel Text Handling Processor

Project Overview
This project demonstrates parallel text processing using Python.
The system processes multiple text files and stores the results in an SQLite database.

The objective is to show how multiprocessing improves performance when handling text-based workloads.

Features
- Processes multiple text files
- Keyword frequency analysis
- Parallel execution using multiprocessing
- SQLite database integration
- Simple and scalable design

Technologies Used
- Python
- Multiprocessing Module
- SQLite (sqlite3)
- File Handling

How It Works
1. Reads text files from the 'texts' folder
2. Extracts content from each file
3. Counts predefined keywords
4. Executes processing in parallel
5. Stores results in SQLite database

Project Structure

Parallel-Text-Processor/
│
├── texts/
│      ├── tech1.txt
│      ├── tech2.txt
│      ├── logsample.txt
│
├── db_setup.py
├── main.py
├── check_db.py
└── README.md

Execution Steps

1. Setup Database
   py db_setup.py

2. Run Text Processor
   py main.py

3. View Stored Results
   py check_db.py

Expected Outcome
The system processes all text files, calculates keyword frequencies,
and stores the results in the SQLite database.

Purpose of the Project
This project illustrates practical usage of parallel processing for
efficient text data handling in Python.

Author
Nikhil Baratam
