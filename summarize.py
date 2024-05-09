import openai
import textwrap
import os

def summarize(ai_apikey, transcript):
    openai.api_key = ai_apikey


    messages = [{"role": "system", "content": "You are an academic assistant for lecture summaries and notes"}]


    message = "This is a transcript of a lecture. Give me a summary, and then give me notes on it. Also format it for easy readibility. DO NOT start the summary with 'Summary:', but start the notes with 'Notes:'. Each bullet point in the Notes should be denoted with a '-', but do not add '-' to the Summary. Transcript:" + transcript
    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages)
    reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": reply})
    return "\n" + reply + "\n"

def format_output(output_text):
    # Split the output into summary and notes parts
    output = output_text.split("Notes:")
    #clean output list from \n characters
    cleaned_list = [note.replace("\n", " ") for note in output]
    #make summary equal first element of cleaned list
    summary = cleaned_list[0]
    #remove the starting 'summary:' part of the summary
    formatted_summary = summary.replace("Summary: ", "")
    #make notes equal second element of cleaned list
    notes = cleaned_list[1]

    #split by hyphen
    bullet_points = notes.split(" - ")

    # Remove the empty string caused by the initial delimiter
    if bullet_points[0] == '':
        bullet_points.pop(0)

    
    return formatted_summary, bullet_points


def clear_folder(folder_path):
    # Iterate through the items in the folder
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        # Check if the item is a file
        if os.path.isfile(item_path):
            os.remove(item_path)  # Remove the file