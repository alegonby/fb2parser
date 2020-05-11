import xml.etree.ElementTree as ET
import os
import shutil
import re
import sqlite3
import sys

# to get path as argument
path = sys.argv[1]
#'./input/'
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

# Establish connection to db:
conn = sqlite3.connect(path+'database/testDB.db')
cur = conn.cursor()


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
else:
    print("Error! cannot create the database connection.")

# Create folder for incorrect_input:
if not os.path.exists(path+'incorrect_input'):
    os.makedirs(path+'incorrect_input')

#check folder for a file
for filename in os.listdir(path):
    if os.path.isfile(path+filename):
        if filename.endswith(".fb2"):
            #open fb2 file and create new table for words
            f = open(os.path.join(path, filename), 'r', encoding='UTF-8')
            tabname = filename[:-4].replace(' ', '')
            drop_table(conn, tabname )
            create_book_table = 'CREATE TABLE '+ tabname +  ' ('\
                                     'word text,'\
                                     'count integer,'\
                                     'count_upper_case integer);'
            create_table(conn,create_book_table)
        # moving other files to incorrect_input folder
        else:
            shutil.move(path+filename,path+ 'incorrect_input/')

#reading xml file
tree = ET.parse(f)
root = tree.getroot()

#this thing sticked to every tag in the file, looks like this is common for fb2 files
xmlns='{http://www.gribuser.ru/xml/fictionbook/2.0}'

#get book_name
for book_name in root.findall('./'+xmlns+'description/'+xmlns+'title-info/'+xmlns+'book-title'):
    book_name = book_name.text

#get number of paragraphs
p_tags = 0
for p in root.iter(xmlns+'p'):
    p_tags = p_tags + 1

#get all text from the book_name
all_text = ''
for element in root.iter():
    all_text = all_text + str(element.text) + ' '
all_text = all_text[:-1] # Remove trailing space

#filter text to get only cyrillic letters and spaces
filtered_text = ''
for char in all_text:
    if (has_cyrillic(char)) or (char == ' '):
        filtered_text += char

#get all words
words = filtered_text.split()

#count number of all words
n_words = len(words)

#count all cyrillic letters (skipping spaces)
n_letters = 0
for letter in filtered_text:
    if (has_cyrillic(letter)):
        n_letters += 1

#sort all words on lower and capitalized
lower_words = []
cap_words = []
sort_low_cap(words, lower_words, cap_words)

#counting lower and cap words
n_lower_words = len(lower_words)
n_cap_words = len(cap_words)

#inserting info about the book to allbooks tab
book = (book_name, p_tags, n_words, n_letters, n_cap_words, n_lower_words)
insert_book(conn,book)
conn.commit()

#get all words and make them lowercase
lowered_words = []
words_to_lower(words, lowered_words )

#get all words with capitals and make them lowercase
lowered_cap_words = []
words_to_lower(cap_words, lowered_cap_words )

#Count frequency of all words
freq = {}
CountFrequency(lowered_words, freq)
for key, value in freq.items():
    word_count = key, value
    insert_words(conn, word_count)

#Count frequency of words with caps
freq = {}
CountFrequency(lowered_cap_words, freq)
for key, value in freq.items():
    word_count = (value, key)
    update_words(conn, word_count)



cur.execute('SELECT * FROM Allbooks')
results = cur.fetchall()
print(results)

cur.execute('SELECT * FROM Example')
results = cur.fetchall()
print(results)


