from flask import Flask, request, render_template
from flask import jsonify
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import math

app = Flask(__name__)

def video_id(value):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None

@app.route('/')
def my_form():
    return render_template('index.html')



def YoutubeTranscriptSummary():
  variable = request.form.get('variable')
  videoId = video_id(variable)
  youtubeTranscript = YouTubeTranscriptApi.get_transcript(videoId, languages=['en'])
#   yt = youtubeTranscript[0]['text']
#   return yt
  #extracting words from the list of dictonary
  texts = []
  for i in youtubeTranscript:
    for j in i['text'].split(" "):
      texts.append(j)

  max_length = 700
  summarization = pipeline('summarization')
  combined_summary = " "
  if len(texts) >= 700:
    for part in range(math.ceil(len(texts)/max_length)):
      article = " "
      article = article.join(texts[part*max_length:(part+1)*max_length])
      summary_text = summarization(article, max_length=140, min_length=10)[0]['summary_text']
      combined_summary = combined_summary + ' ' + summary_text
  else:
    combined_summary = combined_summary.join(texts)
  return summarization(combined_summary, max_length=140, min_length=10)[0]['summary_text']
@app.route('/', methods=['POST'])
def result():
    return render_template('result.html', foobar=YoutubeTranscriptSummary())

@app.route('/home')
def home():
    return render_template('home.html', foobar=YoutubeTranscriptSummary())

if __name__ == "__main__":
    app.run()
