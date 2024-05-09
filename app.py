from flask import Flask, render_template, session, request, redirect, url_for, make_response, send_file
import os
from werkzeug.utils import secure_filename
from datetime import timedelta
from convert import convert
from summarize import summarize, format_output, clear_folder
import smtplib
from pytube import YouTube
import config

app = Flask(__name__)
app.secret_key = config.app_secretkey
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=2)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST", "GET"])
def upload(filename=None):
    if request.method == "POST":
        session.permanent = True
        file = request.files["file"]
        fname = secure_filename(file.filename)
        session['uploaded_filename'] = fname  # Store the filename in the session
        fname = session['uploaded_filename'] 
        # if not os.path.exists('/uploads'):
        #     os.makedirs('/uploads')
        save_location = os.path.join('uploads', fname)
        file.save(save_location)
        return redirect(url_for("notes", fn=fname))   
    else:
        return render_template("upload.html", filename="")

@app.route("/notes")  # Handle both with and without 'fn' parameter
@app.route("/notes/<string:fn>")
def notes(fn=None):  # Provide a default value for 'fn'
    stt_apikey = config.watson_apikey
    watson_url = config.watson_url
    ai_apikey = config.ai_apikey
    if fn:
        print(os.path.abspath(fn))
        try:
            output = convert(stt_apikey, watson_url, f'uploads/{fn}')
        except FileNotFoundError:
            output = convert(stt_apikey, watson_url, f'{fn}')


        clear_folder('uploads')
        summary = summarize(ai_apikey, output)
        formatted_summary, formatted_notes = format_output(summary)
        
        session['file_data'] = {
        'summary': formatted_summary,
        'notes': formatted_notes,
        'transcript': output
        }

        return render_template("notes.html", summary=formatted_summary, notes=formatted_notes, transcript=output)
    else:
        return render_template("notes.html", summary="No file selected.", notes="", transcript="")

@app.route("/download")
def download():

    
    pdf_data = session.get('file_data')

    if pdf_data:

        notes_formatted = "\n".join([f"• {note}" for note in pdf_data['notes']])

        text_content = f"Summary:\n{pdf_data['summary']}\n\nNotes:\n{notes_formatted}\n\nTranscript:\n{pdf_data['transcript']}"

        # Create a response with the text content
        response = make_response(text_content)
        response.headers["Content-Disposition"] = f"attachment; filename=notes.txt"
        response.headers["Content-Type"] = "text/plain"
        
        return response

    return "No file selected."

        # rendered = render_template(
        #     "notes.html",
        #     summary=pdf_data['summary'],
        #     notes=pdf_data['notes'],
        #     transcript=pdf_data['transcript']
        # )

        # pdf = pdfkit.from_string(rendered, False, options={"enable-local-file-access": ""})

        # response = make_response(pdf)
        # response.headers['Content-Type'] = 'application/pdf'
        # response.headers['Content-Disposition'] = 'attachment; filename=notes.pdf'
        # return response

@app.route("/send-email", methods=['GET', 'POST'])   
def sendemail():
    notewizard_email = "notewizard15@gmail.com"
    password = "pviawnlgierbjlou"

    
    if request.method == 'POST':
        
        pdf_data = session.get('file_data')

        if pdf_data:

            # character = '•'
            # ascii_code = ord(character)

            notes_formatted = "\n".join([f"- {note}" for note in pdf_data['notes']])

            text_content = f"Summary:\n{pdf_data['summary']}\n\nNotes:\n{notes_formatted}\n\nTranscript:\n{pdf_data['transcript']}"
       
        #get email
            email = request.form.get('email')

            connection = smtplib.SMTP("smtp.gmail.com")
            connection.starttls()
            connection.login(user=notewizard_email, password=password)
            connection.sendmail(from_addr=notewizard_email, to_addrs=email, msg="Subject:Your Notes\n\n" + text_content)
            connection.close()
            
            return redirect(url_for("email_confirmation", message="Email sent!"))  


        
        return redirect(url_for("email_confirmation", message="No file uploaded."))  


@app.route("/email-confirmation")
@app.route("/email-confirmation/<message>")
def email_confirmation(message=None):
    
    return render_template("email-confirmation.html", msg=message)

@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy-policy.html")

@app.route("/terms-and-conditions")
def terms():
    return render_template("terms-and-conditions.html")

@app.route("/process", methods=['POST'])
def process():
    youtube_url = request.form['youtube_url']
    
    # Download YouTube video
    yt = YouTube(youtube_url)
    video = yt.streams.get_highest_resolution()
    
    video.download(output_path='uploads', filename='yt')

    return redirect(url_for("notes", fn='yt'))




if __name__ == "__main__":
    app.run(debug=True)
