# Border Crossing Analysis Solution
By Kevin Y. Lin (linkevinlin1@gmail.com)

## Features
* Organize the data in the desired format
* Allow custom Border name (The origin country name can also be changed in the code.)
* Allow custom Measure name
* Several implementations for input data tolerance

## Input Data Tolerance
* Allow input columns to have a different order
* Auto-detect delimiters: comma, semi-colon, tab, Pipes (|) and Carets (^)
* Tolerant on newline symbol in both Windows (\r\n) and Unix (\n)
* Auto remove trailing and leading spaces and those in between words in one label
* Case-insensitive. The output will be capitalized for the first letter in each word
* Time stamp can be anytime within the month. The output will still be the at 12AM of first day of the next month
* Border format can be either the following one: US-Mexico Border, US-Mexico, Mexico. The output will be US-Mexico Border

## What the Code Does Not Do
* Typos are not tolerated
* Not accept different time stamp format.
* Can be slow due to all the data tolerance features

## General Work Flow
The code reads the input data backwards from the end of file one line at a time. The relevant data are stored in an order dictionary for easy access. Once the entries within the same month are collected, the dictionary is then sorted by the labels in ascending order. The processed data are written in a temp file. After all the input data are processed, the temp file will be read from the end again and write to the report.csv. Therefore, the date and the labels will be in a descending order as required. 


