import sqlite3
import openai
from datetime import datetime
from flask import Flask, request, jsonify


app = Flask(__name__)


openai.api_key = 'your-openai-api-key'


def init_db():
    conn = sqlite3.connect('faq_system.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def log_query(question, response):
    conn = sqlite3.connect('faq_system.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''
        INSERT INTO logs (question, response, timestamp)
        VALUES (?, ?, ?)
    ''', (question, response, timestamp))
    conn.commit()
    conn.close()


def get_response_from_chatgpt(question):
    prompt = f"You are a support assistant. Answer the following question in one paragraph: {question}"
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",  # Or the engine you have access to
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()


@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json.get('question')
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400

    response = get_response_from_chatgpt(question)
    
    
    log_query(question, response)
    
    return jsonify({
        'question': question,
        'response': response
    })


@app.route('/logs', methods=['GET'])
def view_logs():
    conn = sqlite3.connect('faq_system.db')
    c = conn.cursor()
    c.execute('SELECT * FROM logs ORDER BY timestamp DESC')
    logs = c.fetchall()
    conn.close()
    
    logs_data = [{'id': log[0], 'question': log[1], 'response': log[2], 'timestamp': log[3]} for log in logs]
    
    return jsonify(logs_data)

if __name__ == '__main__':
    
    init_db()
    
     
   app.run(debug=True)



* Serving Flask app '__main__'
 * Debug mode: on
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
INFO:werkzeug:Press CTRL+C to quit
INFO:werkzeug: * Restarting with stat
