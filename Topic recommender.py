import os
import openai
import json
import topics_custom_search
from time import time,sleep
import datetime
from nltk.corpus import stopwords
from tkinter import *
from tkinter import scrolledtext,ttk
import elastic2




# tkinter dialogue box initialization and settings
root = Tk()
root.resizable(False, False)
root.geometry("850x500")
root.title("ChatBot Using OpenAI")
root.configure(bg='brown')

###############################################################################
###############################################################################
'''
https://github.com/daveshap/ChatGPT_API_Salience
'''
###############################################################################
###############################################################################


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def save_json(filepath, payload):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, ensure_ascii=False, sort_keys=True, indent=2)


def timestamp_to_datetime(unix_time):
    return datetime.datetime.fromtimestamp(unix_time).strftime("%A, %B %d, %Y at %I:%M%p %Z")



# Function that sends a conversation to the OpenAI API and returns the response text
def chatgpt_completion(messages, model="gpt-3.5-turbo"):
    # Sends messages to OpenAI API
    response = openai.ChatCompletion.create(model=model, messages=messages)
    # Extracts response text from API response
    text = response['choices'][0]['message']['content']
    # Generates a filename for the response text
    filename = 'chat_%s_Resrarchy.txt' % time()
    # Generates a filename for the response text
    if not os.path.exists('chat_logs'):
        os.makedirs('chat_logs')
    # Saves response text to a file
    save_file('chat_logs/%s' % filename, text)
    return text

# Function that sends a prompt to the OpenAI API using a specified engine and returns the response text
def gpt3_completion(prompt, engine='text-davinci-003', temp=0.0, top_p=1.0, tokens=400, freq_pen=0.0, pres_pen=0.0, stop=None):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            filename = '%s_gpt3.txt' % time()
            if not os.path.exists('gpt3_logs'):
                os.makedirs('gpt3_logs')
            save_file('gpt3_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

# Function that converts a conversation into a flattened string
def flatten_convo(conversation):
    convo = ''
    for i in conversation:
        convo += '%s: %s\n' % (i['role'].upper(), i['content'])
    return convo.strip()

# Function that performs a Google search and returns a list of results
def custom_search(topic_name, result=[]):
    # For single word or sentence search
    # perform a new Google search using the text input
    links, titles, snippets = topics_custom_search.get_data(topic_name)
    # loop through all the found results
    for i in range(len(links)):
        # display all the results
        # print('>> Webpage Title: ' + titles[i] + '\n>> Website Link: ' + links[i]
        # + '\n>> Snippets: ' + snippets[i] + '\n')
        result.append('>> Webpage Title: ' + titles[i] + '\n>> Website Link: ' + links[i] + '\n>> Snippets: '
                      + snippets[i])
    return result

combo_list= ['please select topic']

# function to get user input
def take_input():
    global conversation, counter, combo_list
    convo_length = 30
    openai.api_key = open_file('openaiapikey.txt')
    default_system = 'I am an AI named Researchy. My primary goal is suggest topics for research students based on their background'
    conversation = list()
    conversation.append({'role': 'system', 'content': default_system})
    counter = 0



    # get the input text string
    a = str(inputtxt.get()).capitalize()

    # output the user input to the chat screen
    Output.insert(END, 'User: ' + a + '\n', "left")

    # detect when no user input
    if len(a) <= 0:
        return
    # add user input to the conversation
    conversation.append({'role': 'user', 'content': a})
    # save the user input to a file
    filename = 'chat_%s_user.txt' % time()
    if not os.path.exists('chat_logs'):
        os.makedirs('chat_logs')
    save_file('chat_logs/%s' % filename, a)

    # flatten the conversation into a single string
    flat = flatten_convo(conversation)
    # print(flat)
    # Use GPT3 to infer user intent, disposition, valence and  needs
    prompt = open_file('user_trail.txt').replace('<<INPUT>>', flat)
    anticipation = gpt3_completion(prompt)
    print('\n\nANTICIPATION: %s' % anticipation)

    # Use Gpt3 to summarize the conversation to the most salient points
    prompt = open_file('user_salient.txt').replace('<<INPUT>>', flat)
    salience = gpt3_completion(prompt)
    print('\n\nSALIENCE: %s' % salience)

    # update SYSTEM based upon user needs and salience
    conversation[0][
        'content'] = default_system + ''' Here's a brief summary of the conversation: %s - And here's what I expect the user's needs are: %s''' % (
    salience, anticipation)

    # generate a response
    response = chatgpt_completion(conversation)

    #add response to conversation
    conversation.append({'role': 'assistant', 'content': response})
    print('\n\nRESEARCHY: %s' % response)
    # output the user input to the chat screen
    Output.insert(END, '\nRESEARCHY: %s' % response + '\n\n', "left")

    if '1.' in str(response):
        new_list = str(response).split('\n')
        combo_list = []
        for item in new_list:

            if len(item) > 0 and item.split('.')[0].isdecimal():

                word_list = str(item.split('.')[1]).strip().split()
                combo_list.append(word_list)

    # Clear the items in the list
    combo.configure(values=())
    combo['values'] = combo_list
    combo.current(0)

    # clear the last user input
    inputtxt.delete(0, 'end')

    # increment counter and consolidate memories
    counter += 2
    if counter >= 100:
        # reset conversation
        conversation = list()
        conversation.append({'role': 'system', 'content': default_system})


def callback(event):
    # Extract selected item from combo box
    selected_item = str(combo.get()).strip().split()
    # print(combo.get())

    # Remove stopwords from selected item
    filtered_words = [word for word in selected_item if word not in stopwords.words('english')]

    # Convert filtered list of words to string
    new_lis = ' '.join(str(e) for e in filtered_words)
    print('Filtered Selected Item: ', new_lis)
    # Search for supervisors using elastic2 module
    if len(new_lis) > 0:
        supervisors = elastic2.get_supervisors(selected_item)
        print('Supervisor List')

        # Extract the first part of the topic (before the explanation) for google search
        if '.' in new_lis.strip():
            new_lis = str(new_lis.strip()).split('.')[0]
        elif ':' in new_lis.strip():
            new_lis = str(new_lis.strip()).split(':')[0]

        # Perform custom google search
        print('Searching google for: ', new_lis.strip())
        google_results = custom_search(new_lis.strip())
        # supervisor search
        if len(supervisors) > 0:
            # Iterate through the list of supervisors
            for i, item in enumerate(supervisors):
                # Display the supervisor's name and email address
                print('\n')
                print(item)
                # display result based on number of available links retrived
                if i <= (len(google_results) - 1):
                    print(google_results[i])
                    # output the user input to the chat screen
                    Output.insert(END, '\nResult: ' + str(i + 1) + '\nName of Supervisor: ' + str(
                        item['Name']) + '\nSupervisor Email: ' + str(item['Email address']) + '\n' + google_results[
                                      i] + '\n', "left")
        # If no supervisors are found, display the default supervisor
        else:
            # output the user input to the chat screen
            Output.insert(END, '\nSupervisor Name: ' + '\nSupervisor Email: ',
                          "left")
        # create a dropdown list of all topics
        # create the dropdown menu for all_topics

######################################
# Tkinter interface window settings
######################################


# assign the first label
l1 = Label(text="OpenAI chatBot message screen:", fg="white", bg="grey", font=('Times', 14))
# create the output text box
Output = scrolledtext.ScrolledText(root, height=10,
                width=80,
                bg="light yellow", font=('Times', 12))
# assign the second label
l2 = Label(text="Enter your request here:", fg="white", bg="grey", font=('Times', 14))
# create the user text input box
inputtxt = Entry(root,
              width=50,
              bg="white", justify=CENTER, font=('Times', 12))
# create the button to send user entered text
Display = Button(root, height=1,
                 width=15,
                 text="Send Request",
                 command=lambda: take_input(), fg="white", bg="black", font=('Times', 14))



# configure the text justification
Output.tag_configure("right", justify="right")
Output.tag_configure("left", justify="left")

# Tkinter drop list settings
# creating drop down
combo = ttk.Combobox(root, state="readonly", width=70, justify=CENTER, font=('Times', 12), values=combo_list)
combo.current(0)
combo.bind("<<ComboboxSelected>>", callback)


# organise widgets in blocks before placing them in the parent widget
l1.pack()
combo.pack()

Output.pack(fill="both", expand=True)
l2.pack()
inputtxt.pack()
Display.pack()
# Bind the Enter Key to the window
root.bind('<Return>', lambda event=None: Display.invoke())

# output the user input to the chat screen
Output.insert(END, 'RESEARCHY: I am a Research chatbot. Depending on your background, I can recommend research topics and supervisors, '
                   'as well as have a conversation with you to learn about your needs in terms of research..' + '\n\n', "left")



# start dialogue app
mainloop()
