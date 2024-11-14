from flask import Flask, render_template, redirect, request, url_for
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values
import json
from time import time
load_dotenv()
prompt = {}
answer = ""
output = {}
conn = OpenAI()

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"]=True

@app.route("/",methods=["GET","POST"])
def index():
    if request.method == "POST":
        un = request.form.get("userName")
        if not un:
            print("no prompt")
            return redirect("/")
        global prompt
        global output
        global answer
        details = {}
        details["userName"] = request.form['userName']
        details["email"] = request.form['email']
        details["yoe"] = request.form['yoe']
        details["workex"] = request.form['workex']
        details["skills"] = request.form['skills']
        details["pos"] = request.form['pos']
        details["comp"] = request.form['comp']
        submission = """Whats your name: {}
        How many Years of experience: {} 
        What are your Prior work experience: {} 
        What are your Relevant Skills: {}
        What is your dream role?: {}
        What is your dream company?: {}
        """.format(
                details["userName"],
                details["yoe"],
                details["workex"],
                details["skills"],
                details["pos"],
                details["comp"])
        prompt = """You are a product manager at a tech firm that knows all the relevant skills a product manager needs. You are advising a person who is currently in a marketing and growth role. The person you are advising currently is in a program  that runs for 1 year and helps students gain skills required to get a job at startups. The current user is in their 3rd month of training and are currently preparing for their next role. Your role is to brainstorm unique ideas with the candidate on bridging the gap between where they are now vs where they want to be. This would be unique for every student.
The student has submitted a form which is provided in double quotes: 
"{}"
Your current task is to provide advice to the student. Do this by first summarizing their current situation, what skills they are missing and how difficult it may be to transition. Then provide 4 different options for future opportunities that can overcome these shortcomings and build on their current skills, years of industry experience and work experience in the next 6 months to prepare. These future steps maybe able to be done simultaneously. Then, wait for the student to respond to these options.

The output format should in a dictionary with the following format:
"summary" : "<summary of the person in second person>",
"options":[
"<option 1 of their future opportunities>",
 "<option 2 of their future opportunities>",
 "<option 3 of their future opportunities>",
 "<option 4 of their future opportunities>"
]
where the text inside the demiliters <> is replaced by their custom advice""".format(submission)
        usermessages = [{
            "role":"user",
            "content":prompt}
        ] 
        answer = askAI(prompt,usermessages)
        output = json.loads(answer)

        #print(output)
        return redirect(url_for("options",summary=output["summary"],
                               option1 = output["options"][0],
                               option2 = output["options"][1],
                               option3 = output["options"][2],
                               option4 = output["options"][3],))
    else:
        return render_template("index.html")
@app.route('/options')
def options():
    global prompt
    global output
    global answer
    summary = request.args.get('summary', None)
    option1 = request.args.get('option1', None)
    option2 = request.args.get('option2', None)
    option3 = request.args.get('option3', None)
    option4 = request.args.get('option4', None)
    return render_template('options.html', summary=summary,
                               option1 = option1,
                               option2 = option2,
                               option3 = option3,
                               option4 = option4)
@app.route('/finaloutput', methods=['POST'])
def finaloutput():
    global prompt
    global answer
    global output
    options = []
    options.append(request.form.getlist('option1'))
    options.append(request.form.getlist('option2'))
    options.append(request.form.getlist('option3'))
    options.append(request.form.getlist('option4'))
    options.append(request.form.getlist('option5'))
    feedback = request.form.get('feedback', '').strip()
    selected_options = []
    for i in range(0,5):
        #print(options[i])
        if options[i]:    
            selected_options.append("".join(options[i]))
    #print("selected_options")
    #print(selected_options)
    
    #print(prompt)
    # Check if "I do not like these options" is selected
    if "Option 5" in selected_options and feedback:
        # Generate new options based on feedback, here we just simulate changes
        summary = "Thank you for your feedback! Based on your suggestions, here is an updated list of options."
        options = ["New Option 1", "New Option 2", "New Option 3", "New Option 4"]
        return render_template('options.html', summary=summary, options=options)
    else:
        # If one of the regular options was selected, redirect to the final page
        choicesmade = f"You selected: {', '.join(selected_options)}"
        prompt2 = "The user has chosen {}. Based on this summarise the users choices and create a month by month roadmap of their next 6 months. The plan should consider their \
          past experience, their current skills and the skills they want to achieve, their years of experience, their dream career and their \
            dream company. No need to answer in json or dictionary format, please answer normally.".format(', '.join(selected_options))
        usermessages = [{
                "role":"user",
                "content":prompt},
                {
                "role":"assistant",
                "content":answer},
                {"role":"user",
                "content":prompt2}
            ] 
        answer = askAI(prompt,usermessages)
        
        return render_template('finaloutput.html', output=choicesmade,output2=answer)

def askAI(prompt,usermessages):
    print(usermessages)
    completion = conn.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = usermessages
    )
    #print(completion)
    answer = completion.choices[0].message.content
    print("thinking")
    #print(answer)

# Convert the string to JSON

# Display the resulting dictionary
    #print(data_json)
    return answer