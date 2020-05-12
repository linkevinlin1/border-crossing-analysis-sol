#For Insight Data Engineering Codeing Challenge: "Border Analysis"
#This Python3 code takes the input data and output with the desired format with some tolerance on the quality of the input data.
#
#Different column positions and custom border and measure names are allowed.
#The date can be on different day of the month.
#Certain delimiters other than semi-colon are allowed.
#Extra spaces and letter case are allowed.
#Typo is not tolerated.
#Slower processing speed is thus expected.
#
#The code reads from the end of the input file, processes and outputs to a temp file in ascending order.
#The temp file is again read from the end and output to the report.csv with correct descending order.
#
#For more info, please refer to readme
##
#Kevin Y. Lin 20200218 linkevinlin1@gmail.com

import os
import collections
import sys
import time
# For Banker's rounding. Python3 uses a different rounding scheme
from decimal import Decimal, ROUND_HALF_UP

def column_init(column_list):

    #identify the indices for relevant columns

    i=0
    for item in column_list:
        if item.lower() == 'border':
            Border_row_num=i
        elif item.lower() == 'date':
            Date_row_num=i
        elif item.lower() == 'measure':
            Measure_row_num=i
        elif item.lower() == 'value':
            Value_row_num=i
        i=i+1
    return [Border_row_num, Date_row_num, Measure_row_num, Value_row_num]

def read_backwards(f,delimiter):
    while f.read(1) != '\n':
        f.seek(f.tell() - 2, os.SEEK_SET)
    current_line_num=f.tell()
    last_line = f.readline()
    last_line=last_line.strip('\n')
    current_list = last_line.split(delimiter)
    current_list=[x.strip() for x in current_list]
    f.seek(current_line_num-4,0)
    return current_list

def reverse_csv():

    #reverse the line order of the temp file and write to report.csv
    f = open(str(sys.argv[2])+'.tmp','r')

    first_line=f.readline()
    firstline_end= f.tell()
    f.seek(0, os.SEEK_END)
    f.seek(f.tell()-4, os.SEEK_SET)

    newf = open(str(sys.argv[2]),'w')
    newf.write('Border,Date,Measure,Value,Average\n')

    #read from the end
    while(f.tell()>firstline_end):
        while f.read(1) != '\n':
            f.seek(f.tell() - 2, os.SEEK_SET)
        current_line_num=f.tell()
        last_line = f.readline()
        newf.write(last_line)
        f.seek(current_line_num-4,0)
    newf.write(first_line)
    newf.close()
    f.close()

    #clean up the temp file
    os.remove(str(sys.argv[2])+'.tmp')

def constuct_end_day(date):

    #calculate the last time stamp of the current month range (12AM of the first day in the next month)

    #find first day of the current month
    first_day=time.strptime(str(date.tm_mon)+' 1 '+str(date.tm_year)+' 0 0 0','%m %d %Y %H %M %S')
    if date>first_day:
        if date.tm_mon+1==13:
            return time.strptime('1 1 '+str(date.tm_year+1)+' 0 0 0','%m %d %Y %H %M %S')
        else:
            return time.strptime(str(date.tm_mon+1)+' 1 '+str(date.tm_year)+' 0 0 0','%m %d %Y %H %M %S')
    else:
        return first_day

def sort_and_output(stats_dic, home_country, month_num, last_end_day, fout):
    #           (dictionary,name of country, month counter, last day of the time period, output file descriptor)
    end_day_str=time.strftime('%m/%d/%Y %I:%M:%S %p', last_end_day)
    #sort the ordered dictionary according to the output specification, key=(Border, Measure) and value of the dictionary=[Value, Running Sum]
    stats_dic=collections.OrderedDict(sorted(stats_dic.items(), key=lambda key_value_pair: (key_value_pair[1][0], key_value_pair[0][1], key_value_pair[0][0])))
    for key in stats_dic:
        #only output when the measure has none-zero value
        if stats_dic[key][0]>0:
            if month_num>1:
                fout.write(home_country+'-'+key[0].title()+' Border,'+end_day_str+','+key[1].title()+','+str(stats_dic[key][0])+','+str(Decimal(stats_dic[key][1]/(month_num-1)).quantize(0, ROUND_HALF_UP))+'\n')
            else:
                fout.write(home_country+'-'+key[0].title()+' Border,'+end_day_str+','+key[1].title()+','+str(stats_dic[key][0])+','+str(0)+'\n')
            #calculate running sum including current month
            stats_dic[key][1]=stats_dic[key][1]+stats_dic[key][0]
            #zero current value
            stats_dic[key][0]=0
    return stats_dic

def check_key(stats_dic, current_list, column_index):

    #[Border_row_num, Date_row_num, Measure_row_num, Value_row_num]=column_index

    border_name=current_list[column_index[0]].split()
    country_name=border_name[0].split('-')

    #handle extra spaces in Measure name
    measure_list=current_list[column_index[2]].split()
    measure_name=' '.join(measure_list)

    #key=(Border, Measure)
    dic_key=(country_name[-1].lower(), measure_name.lower())

    #check if the key already exists in the dictionary
    if dic_key in stats_dic:
        #combine the values of same measure and border
        stats_dic[dic_key][0]=stats_dic[dic_key][0]+int(current_list[column_index[3]])
    else:
        #create new key
        #value of the dictionary=[Value, Running Sum]
        stats_dic[dic_key]=[int(current_list[column_index[3]]),0]
    return stats_dic

def check_delimiter(line):
    if line.find(',')>0:
        delimiter=','
    elif line.find(';')>0:
        delimiter=';'
    elif line.find('|')>0:
        delimiter='|'
    elif line.find('^')>0:
        delimiter='^'
    elif line.find('\t')>0:
        delimiter='\t'
    return delimiter

def main():

    #use ordered dictionary to handle the data
    stats_dic=collections.OrderedDict()
    #month counter
    month_num=1
    first_entry_flag=1
    last_end_day=time.gmtime(0)
    #name of the country of interest
    home_country='US'

    #open the input data
    f=open(str(sys.argv[1]), 'r')

    #write to a temp file
    fout=open(str(sys.argv[2])+'.tmp', 'w')

    #read and check the label row
    first_line=f.readline()
    first_line=first_line.strip('\n')
    delimiter=check_delimiter(first_line)
    first_list=first_line.split(delimiter)

    #remove extra spaces
    first_list=[x.strip() for x in first_list]

    #identify the relevant column indices
    column_index=column_init(first_list)
    [Border_row_num, Date_row_num, Measure_row_num, Value_row_num]=column_index


    #read from the end, one line by one line
    firstline_end= f.tell()
    f.seek(0, os.SEEK_END)
    f.seek(f.tell()-4, os.SEEK_SET)
    while(f.tell()>firstline_end):
        current_list=read_backwards(f,delimiter)

        #remove extra spaces in the time string and get current date
        time_list=current_list[Date_row_num].split()
        time_str=' '.join(time_list)
        Current_date=time.strptime(current_list[Date_row_num], '%m/%d/%Y %I:%M:%S %p')

        #initialize the month range record
        if first_entry_flag==1:
            last_end_day=constuct_end_day(Current_date)
            first_entry_flag=0

        #check if the date of the current entry is in the same month range as the last one
        if constuct_end_day(Current_date)!=last_end_day:

            #sort, calculate the running average, and output
            stats_dic=sort_and_output(stats_dic, home_country, month_num, last_end_day, fout)
            month_num=month_num+1
            last_end_day=constuct_end_day(Current_date)

        #check if the current entry matches the exisitng dictionary key and combine them. If not, create a new key fot it.
        stats_dic=check_key(stats_dic, current_list, column_index)

    #exiting the loop, output the remaining entries in the last month range
    stats_dic=sort_and_output(stats_dic, home_country, month_num, last_end_day,fout)

    f.close()
    fout.close()

    #reverse the entry order in the temp file and write to report.csv
    reverse_csv()
    print('Done.')

main()
