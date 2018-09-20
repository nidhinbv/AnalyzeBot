import requests
import json
import praw
import os
import config
import time
import io
import operator

#from string_builder import StringBuilder

def login():
    print(os.listdir('.')) # DELETE
    print("Attempting to log in")
    r = praw.Reddit(username = config.username,
                    password = config.password,
                    client_id = config.client_id,
                    client_secret = config.client_secret,
                    user_agent = "LYKABAU5's first bot")
    print("Logged in!") 
    return r


def run(r, replied_comments):
    print("Fetching comments")
    for comment in r.subreddit('test').comments(limit=100): #/r/all 
        if "watsonbot" in comment.body and comment.id not in replied_comments: #and comment.author != r.user.me()

            #watsonbot LYKABAU5 50 verbose

            print("Bot summoned by: " + str(comment.author))
            summon_commands = comment.body.split()
            #print (summon_commands[0] + " " + summon_commands[1] + " " + str(summon_commands[2]))
            try:
                target = r.redditor(summon_commands[1])
            except:
                print("Invalid user.")
                continue
                
            size = None
            verbose = False

            try:
                size = int(summon_commands[2])
                print("Examining " + str(size) + " comments")
            except:
                print("Size not specified or invalid. Examining all comments")
                pass
            
            try:
                if (summon_commands[2] == "verbose" or summon_commands[3] == "verbose"):
                    print("Verbose mode requested")
                    verbose = True
            except:
                print("Verbose mode not requested")
                pass

            print("Writing target_history.txt ...")
            target_file = open("target_history.txt", "wb")
            for target_comment in target.comments.new(limit = size): 
                target_file.write(target_comment.body.encode('utf-8'))
                target_file.write("\n".encode('utf-8'))
            target_file.close()

            print("Calling Watson method")
            call_Watson(verbose)

            try: 
                output = open("target_results.txt", "r")
                #comment.reply(output.read())
                print("SUCCESS!!!\n")
            except:
                print("Something went wrong with Watson method\n")
                pass
            
            replied_comments.append(comment.id)
            with open("replied_comments.txt", "a") as file:
                file.write(comment.id + "\n")

    print("Sleeping for 15 secs")
    time.sleep(15)


def get_replied_comments():
    if not os.path.isfile("replied_comments.txt"):
        replied_comments = []
    else:
        with open("replied_comments.txt", "r") as f:
            replied_comments = f.read()
            replied_comments = replied_comments.split("\n")
            replied_comments = list(filter(None, replied_comments))

    return replied_comments

def call_Watson(verbose):
    file = io.open("C:/Users/nidhi/Downloads/bot/.vscode/target_history.txt", mode = "r", encoding = "utf-8") #Need to make dynamic
    d = file.read()
    
    response = requests.post("https://gateway.watsonplatform.net/personality-insights/api/v3/profile?version=2017-10-13",
                             auth = ("38cfd745-f5dd-4350-9dfe-050499e152db", "KTomyKzvmG8m"), 
                             headers = {"content-type": "text/plain;charset=utf-8" , "Accept": "application/json"}, 
                             data = d.encode("utf-8")) #charset wasn't set previously!!!
    
    #actual json is just response.text
    try: 
        personality = json.loads(response.text) #This creates a dictionary
        print("Post is successful")
    except: 
        raise Exception("Post failed. Error code " + str(response.status_code))

    target_results = open("target_results.txt", "w")
    #"Verbose mode"
    if verbose: 
        target_results.write("Greetings! These are all of the requested user's characteristics according to the Watson Personality Insights API: \n\n&nbsp;\n\n")
        for value in personality['values']:
            target_results.write(value['name'] + " : " + str(value['percentile'])+ "\n\n")
            #print(value['name'] + " : " + str(value['percentile']))
        #print()
        for need in personality['needs']:
            target_results.write(need['name'] + " : " + str(need['percentile']) + "\n\n")
            #print(need['name'] + " : " + str(need['percentile']))
        #print()
        for big5 in personality['personality']:
            target_results.write(big5['name'] + " : " + str(big5['percentile']) + "\n\n")
            #print(big5['name'] + " : " + str(big5['percentile']))
            for children in big5['children']:
                target_results.write(children['name'] + " : " + str(children['percentile']) + "\n\n")
                #print(children['name'] + " : " + str(children['percentile']))
        #print()
    else:
        print("NOT VERBOSE")
        target_results.write("Greetings! These are the top 3 and bottom 3 characteristics according to the Watson Personality Insights API: \n\n&nbsp;\n\n")
        results_dictionary = {}
        for value in personality['values']:
            results_dictionary[str(value['name'])] = float(value['percentile'])
        for need in personality['needs']:
            results_dictionary[str(need['name'])] = float(need['percentile'])
        for big5 in personality['personality']:
            results_dictionary[str(big5['name'])] = float(big5['percentile'])
            for children in big5['children']:
                results_dictionary[str(children['name'])] = float(children['percentile'])
        
        for key in results_dictionary:
            print(str(key) + " : " + str(results_dictionary.get(key)))
        
        print()
        print()
        sorted_dict = sorted(results_dictionary.items(), key = operator.itemgetter(1), reverse = True)
        count = 0
        last_three = len(sorted_dict) - 3
        for key in sorted_dict:
            if (count < 3 or count >= last_three):
                print("key: " + str(key[0]) + " value: " + str(key[1]))
            count+=1
        #Don't print, write!
    target_results.close()

def main():

    r = login()
    replied_comments = get_replied_comments()
    while True:
        run(r, replied_comments)

main()
