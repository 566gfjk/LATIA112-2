import sys
import configparser

# Azure Speech
import os
import azure.cognitiveservices.speech as speechsdk
import librosa

#Azure Translation
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError

from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    AudioMessage
)

#Config Parser
config = configparser.ConfigParser()
config.read('config.ini')

# Azure Speech Settings
speech_config = speechsdk.SpeechConfig(subscription=config['AzureSpeech']['SPEECH_KEY'], 
                                       region=config['AzureSpeech']['SPEECH_REGION'])
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
UPLOAD_FOLDER = 'static'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



app = Flask(__name__)

channel_access_token = config['Line']['CHANNEL_ACCESS_TOKEN']
channel_secret = config['Line']['CHANNEL_SECRET']
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)

configuration = Configuration(
    access_token=channel_access_token
)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    korean_text, latin_transcription = azure_translate(event.message.text)
    audio_duration = azure_speech(korean_text)
    print(korean_text)
    print(latin_transcription)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=korean_text),
                    TextMessage(text=latin_transcription),
                    AudioMessage(
                        originalContentUrl=config["Deploy"]["URL"] + "/static/outputaudio.wav",
                        duration=audio_duration
                    )
                ]
            )
        )

from hangul_romanize import Transliter
from hangul_romanize.rule import academic

def azure_translate(user_input):
    credential = TranslatorCredential(config['AzureTranslator']["Key"], config['AzureTranslator']["Region"])
    text_translator = TextTranslationClient(endpoint=config['AzureTranslator']["EndPoint"], credential=credential)

    try:
        target_languages = ["ko"]
        input_text_elements = [InputTextItem(text=user_input)]

        response = text_translator.translate(content=input_text_elements, to=target_languages)
        print(response)
        translation = response[0] if response else None

        if translation:
            korean_text = translation.translations[0].text
            latin_transcription = korean_to_latin_transcription(korean_text)
            return korean_text, latin_transcription

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error}")
        print(f"Message: {exception.error.message}")

def korean_to_latin_transcription(korean_text):
    transliter = Transliter(rule=academic)
    latin_transcription = transliter.translit(korean_text)
    return latin_transcription

def azure_speech(user_input):
    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = "ko-KR-SunHiNeural"
    file_name = "outputaudio.wav"
    file_config = speechsdk.audio.AudioOutputConfig(filename="static/" + file_name)
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=file_config
    )

    # Receives a text from console input and synthesizes it to wave file.
    result = speech_synthesizer.speak_text_async(user_input).get()
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(
            "Speech synthesized for text [{}], and the audio was saved to [{}]".format(
                user_input, file_name
            )
        )
        audio_duration = round(
            librosa.get_duration(path="static/outputaudio.wav") * 1000
        )
        print(audio_duration)
        return audio_duration
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

if __name__ == "__main__":
    app.run()