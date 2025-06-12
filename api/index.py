from flask import Flask, request, render_template
from flask_cors import CORS
import openai
import os
import json

# Explicitly tell Flask where to find the templates
app = Flask(__name__, template_folder='../templates')
CORS(app)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/', methods=['GET', 'POST'])
def generate_presale():
    if request.method == 'POST':
        card_name = request.form['credit_card_name']
        target_audience = request.form['target_audience']
        main_benefit = request.form['main_benefit']

        prompt = f"""
        Write a high-converting presale page for a credit card called "{card_name}", targeting {target_audience}.
        Highlight the benefit: "{main_benefit}".

        Return the following as JSON:
        {{
            "headline": "...",
            "subheadline": "...",
            "hook": "...",
            "benefits": ["...", "...", "..."],
            "cta": "..."
        }}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

            gpt_reply = response.choices[0].message.content.strip()
            content = json.loads(gpt_reply)

            return render_template('presale.html',
                                   card_name=card_name,
                                   headline=content['headline'],
                                   subheadline=content['subheadline'],
                                   hook=content['hook'],
                                   benefits=content['benefits'],
                                   cta=content['cta'])
        except Exception as e:
            return f"<h1>Error:</h1><p>{e}</p><a href='/'>Go Back</a>"

    return '''
    <h1>Finance Presale Page Generator</h1>
    <form method="post">
        <label>Credit Card Name:</label><br>
        <input type="text" name="credit_card_name" required><br><br>

        <label>Target Audience:</label><br>
        <input type="text" name="target_audience" required><br><br>

        <label>Main Benefit:</label><br>
        <input type="text" name="main_benefit" required><br><br>

        <input type="submit" value="Generate Page">
    </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
