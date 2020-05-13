import xml.etree.ElementTree as ET
import os
import shutil
import re
import sqlite3
import sys

# to get path as argument
path = sys.argv[1]
# path = './input/'
#to define whether char is cyrillic
def has_cyrillic(text):
    return bool(re.search('[\u0400-\u04FF]', text))

#to sort words on lower and with capital letters
def sort_low_cap(words, low, cap):
    for word in words:
        if word.islower():
            low.append(word)
        else:
            cap.append(word)

#to count word frequency
def CountFrequency(my_list, freq):
    for items in my_list:
        freq[items] = my_list.count(items)

def words_to_lower(words, lowered):
    for word in words:
        lowered.append(word.lower())



# Create folder for database:
if not os.path.exists(path+'database'):
    os.makedirs(path+'database')
    print('DB folder created')

# Establish connection to db:
conn = sqlite3.connect(path+'database/testDB.db')
cur = conn.cursor()
print('DB connection established')

# Create table:
def create_table(conn, create_table_sql):
    cur.execute(create_table_sql)

# drop table
def drop_table(conn, tabname):
    cur.execute('DROP TABLE IF EXISTS ' + tabname)

#Insert into Allbooks table
def insert_book(conn, book):
    sql = ''' INSERT INTO allbooks(book_name,number_of_paragraph,number_of_words,number_of_letters,words_with_capital_letters,words_in_lowercase)
              VALUES(?,?,?,?,?,?) '''
    cur.execute(sql, book)
    return cur.lastrowid

#Insert into book table
def insert_words(conn, words):
    sql = 'INSERT INTO '+ tabname + ' (word,count,count_upper_case)'\
              'VALUES(?,?,0)'
    cur.execute(sql, words)
    return cur.lastrowid

#Update book table
def update_words(conn, words):
    sql = 'UPDATE '+ tabname +\
              ' set count_upper_case = ? '\
              'where word = ?'
    cur.execute(sql, words)
    return cur.lastrowid


#SQL to create allbooks table
create_allbooks_table = """ CREATE TABLE IF NOT EXISTS allbooks (
                              book_name text,
                              number_of_paragraph integer,
                              number_of_words integer,
                              number_of_letters integer,
                              words_with_capital_letters integer,
                              words_in_lowercase integer); """

#checking that connection is established and creating allbooks table
if conn is not None:
    create_table(conn, create_allbooks_table)
    print('allbooks table created')
else:
    print("Error! cannot create the database connection.")

# Create folder for incorrect_input:
if not os.path.exists(path+'incorrect_input'):
    os.makedirs(path+'incorrect_input')
    print('incorrect_input folder created')

#check folder for a file
for filename in os.listdir(path):
    if os.path.isfile(path+filename):
        if filename.endswith(".fb2"):
            #open fb2 file and create new table for words
            f = open(os.path.join(path, filename), 'r', encoding='UTF-8')
            print('fb2 file opened')
            tabname = filename[:-4].replace(' ', '')
            drop_table(conn, tabname )
            create_book_table = 'CREATE TABLE '+ tabname +  ' ('\
                                     'word text,'\
                                     'count integer,'\
                                     'count_upper_case integer);'
            create_table(conn,create_book_table)
            print('table for words in a file created')
            
            # reading xml file
            tree = ET.parse(f)
            root = tree.getroot()
    
            # this thing sticked to every tag in the file, looks like this is common for fb2 files
            xmlns = '{http://www.gribuser.ru/xml/fictionbook/2.0}'
    
            # get book_name
            for book_name in root.findall('./' + xmlns + 'description/' + xmlns + 'title-info/' + xmlns + 'book-title'):
                book_name = book_name.text
                print('book_name received')
    
            # get number of paragraphs
            p_tags = 0
            for p in root.iter(xmlns + 'p'):
                p_tags = p_tags + 1
            print('num of paragraphs received')
    
            # get all text from the book_name
            all_text = ''
            for element in root.iter():
                all_text = all_text + str(element.text) + ' '
            all_text = all_text[:-1]  # Remove trailing space
            print('all text from file received')
    
            # filter text to get only cyrillic letters and spaces
            filtered_text = ''
            for char in all_text:
                if (has_cyrillic(char)) or (char == ' '):
                    filtered_text += char
            print('text filtered')
    
            # get all words
            words = filtered_text.split()
            print('all words from text received')
    
            # count number of all words
            n_words = len(words)
            print('num of words received')
    
            # count all cyrillic letters (skipping spaces)
            n_letters = 0
            for letter in filtered_text:
                if (has_cyrillic(letter)):
                    n_letters += 1
            print('num of letters received')
    
            # sort all words on lower and capitalized
            lower_words = []
            cap_words = []
            sort_low_cap(words, lower_words, cap_words)
            print('sort on lowercase words and words with caps')
    
            # counting lower and cap words
            n_lower_words = len(lower_words)
            print('num of lower_words received')
            n_cap_words = len(cap_words)
            print('num of cap_words received')
    
            # inserting info about the book to allbooks tab
            book = (book_name, p_tags, n_words, n_letters, n_cap_words, n_lower_words)
            insert_book(conn, book)
            conn.commit()
            print('book info inserted into allbooks table')
    
            # get all words and make them lowercase
            lowered_words = []
            words_to_lower(words, lowered_words)
            print('all words converted to lower case received')
    
            # get all words with capitals and make them lowercase
            lowered_cap_words = []
            words_to_lower(cap_words, lowered_cap_words)
            print('Cap words converted to lower case received')
    
            # Count frequency of all words and insert into books table
            freq = {}
            CountFrequency(lowered_words, freq)
            for key, value in freq.items():
                word_count = key, value
                insert_words(conn, word_count)
            conn.commit()
            print('all words with count inserted into book table')
    
            # Count frequency of words with caps and update books table
            freq = {}
            CountFrequency(lowered_cap_words, freq)
            for key, value in freq.items():
                word_count = (value, key)
                update_words(conn, word_count)
            conn.commit()
            print('Cap words count updated in book table')
            
            
        # moving other files to incorrect_input folder
        else:
            shutil.move(path+filename, path + 'incorrect_input/')
            print('incorrect files moved to incorrect_input')


# cur.execute('SELECT * FROM Allbooks')
# results = cur.fetchall()
# print(results)
#
# cur.execute('SELECT * FROM Example')
# results = cur.fetchall()
# print(results)

# Close opened file, cursor, connection to DB
f.close()
cur.close()
conn.close()
print('file closed')
print('cursor closed')
print('connection to DB closed')