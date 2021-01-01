import re
import sqlite3
from collections import Counter
from string import punctuation
from math import sqrt
import requests
from tkinter import *
import tkinter as tk
from tkinter import filedialog
import pandas as pd


root =Tk()
root.title("Mr. Bot")
root.geometry("800x500")
main_menu=Menu(root)

chatwindow = Text(root, bd=1, bg="#f5f5f5", width=50, height=8)
chatwindow.place(x=6, y=6, height=385, width= 788)

messagewindow=Entry(root, bd=1, bg="#f5f5f5")
messagewindow.place(x=6,y=400,height=80,width=650)


connection = sqlite3.connect('chatbot.db')
cursor = connection.cursor()
create_table_request_list = [
    'CREATE TABLE words(word TEXT UNIQUE)',
    'CREATE TABLE sentences(sentence TEXT UNIQUE, used INT NOT NULL DEFAULT 0)',
    'CREATE TABLE associations (word_id INT NOT NULL, sentence_id INT NOT NULL, weight REAL NOT NULL)',
]
for create_table_request in create_table_request_list:
    try:
        cursor.execute(create_table_request)
    except:
        pass
    
def get_id(entityName, text):
    tableName = entityName + 's'
    columnName = entityName
    cursor.execute('SELECT rowid FROM ' + tableName + ' WHERE ' + columnName + ' = ?', (text,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute('INSERT INTO ' + tableName + ' (' + columnName + ') VALUES (?)', (text,))
        return cursor.lastrowid
 
def get_words(text):
    wordsRegexpString = '(?:\w+|[' + re.escape(punctuation) + ']+)'
    wordsRegexp = re.compile(wordsRegexpString)
    wordsList = wordsRegexp.findall(text.lower())
    return Counter(wordsList).items()
def get_word(H):
    global B
    words = get_words(B)
    words_length = sum([n * len(word) for word, n in words])
    sentence_id = get_id('sentence', H)
    for word, n in words:
        word_id = get_id('word', word)
        weight = sqrt(n / float(words_length))
        cursor.execute('INSERT INTO associations VALUES (?, ?, ?)', (word_id, sentence_id, weight))
    connection.commit()
    cursor.execute('CREATE TEMPORARY TABLE results(sentence_id INT, sentence TEXT, weight REAL)')
    words = get_words(H)
    words_length = sum([n * len(word) for word, n in words])
    for word, n in words:
        weight = sqrt(n / float(words_length))
        cursor.execute('INSERT INTO results SELECT associations.sentence_id, sentences.sentence, ?*associations.weight/(4+sentences.used) FROM words INNER JOIN associations ON associations.word_id=words.rowid INNER JOIN sentences ON sentences.rowid=associations.sentence_id WHERE words.word=?', (weight, word,))

    cursor.execute('SELECT sentence_id, sentence, SUM(weight) AS sum_weight FROM results GROUP BY sentence_id ORDER BY sum_weight DESC LIMIT 1')
    row = cursor.fetchone()
    cursor.execute('DROP TABLE results')
    if row is None:
        cursor.execute('SELECT rowid, sentence FROM sentences WHERE used = (SELECT MIN(used) FROM sentences) ORDER BY RANDOM() LIMIT 1')
        row = cursor.fetchone()
    B = row[1]
    cursor.execute('UPDATE sentences SET used=used+1 WHERE rowid=?', (row[0],))
B='Hello'
chatwindow.insert(END,'Mr.Bot: ' + B+'\n\n')
def chatBot():
    global B;
    temp = 0
    #print('B: ' + B)
    H = messagewindow.get().strip()
    chatwindow.insert(END, 'Rishabh: '+H+'\n\n')
    if H == '':
        pass
    elif ((H == "what is the top 10 news?")or(H == "tell me the news")or(H == "any latest news?")):
        main_url = " https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=3753389e319e4171b1ccf7c12ff22087"
        open_bbc_page = requests.get(main_url).json() 
        article = open_bbc_page["articles"] 
        results = [] 
        temp = 1
        for ar in article: 
            results.append(ar["title"]) 
                
        for i in range(len(results)): 
            chatwindow.insert(END,str(i + 1) +'. ' + results[i]+'\n')
        print("\n\n") 
    elif(H == "update db"):
        messagewindow.delete(0,END)
        import_file_path = filedialog.askopenfilename()
        df = pd.read_csv (import_file_path)
        msg = df.Message #use this line to perticularly select a coloumn , change the word Message from df.Message if your coloumn name is something else. ex:- df.text if your coloumn name is text
        add = df['Message'].astype(str)
        file1 = open("y.txt","w") 
        file1.writelines(add)
        file1.close()
        file1 = open("y.txt","r+")  
        z= file1.read()
        nval=z
        H=z
        get_word(H)



        #print(add)     

        #messagewindow.insert(END,nval)

    else:
        get_word(H)
        if B=='':
            B=H;
        chatwindow.insert(END,'Mr.Bot: ' + B+'\n\n')
    messagewindow.delete(0,END)

Button = Button(root, text="send", command = chatBot, bg="#f5f5f5", activebackground="#f5f5f5",width=12, height=9, font=("Arial", 13))
Button.place(x=682, y=420, height=50, width=90)
root.mainloop()
