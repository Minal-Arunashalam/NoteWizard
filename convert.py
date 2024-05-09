import subprocess
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os

def convert(apikey, url, video_file_path):
    if os.path.exists('audio.wav'):
        os.remove('audio.wav')

    command = f'ffmpeg -i {video_file_path} -ab 160k -ar 44100 -vn audio.wav'
    subprocess.call(command, shell=True)



    # Setup service
    authenticator = IAMAuthenticator(apikey)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(url)

    # # Create the target directory if it does not exist
    # if not os.path.exists('/audio'):
    #     os.makedirs('/audio')

    with open('audio.wav', 'rb') as f:
        res = stt.recognize(audio=f, content_type='audio/wav', model='en-AU_NarrowbandModel').get_result()

    # print(res)
    text = [result['alternatives'][0]['transcript'].rstrip() + '.\n' for result in res['results']]
    text = [para[0].title() + para[1:] for para in text]
    transcript = ''.join(text)
    
    return transcript
