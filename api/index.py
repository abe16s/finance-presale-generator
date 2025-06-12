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
        Write high-converting presale page content for a credit card called "{card_name}", targeting {target_audience}. Highlight the key benefit: "{main_benefit}".

        Return the following JSON structure:
        {{
        "headline": "[Max 10 words, bold, exciting]",
        "subheadline": "[Max 15 words, supporting the headline]",
        "hook": "[1 short, persuasive paragraph introducing the card]",
        "benefits": ["[Exactly 3, high-impact benefits]"],
        "cta": "[Very short button text like 'Apply Now', max 4 words]"
        }}

        Guidelines:
        - Use energetic, persuasive language.
        - Benefits must be direct, specific, and formatted as phrases.
        - Do not exceed 3 benefits.
        - Keep CTA button text to 4 words max.
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
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Finance Presale Page Generator</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 min-h-screen flex items-center justify-center p-6">
            <div class="bg-white rounded-2xl shadow-xl p-10 w-full max-w-lg space-y-6">
                <h1 class="text-3xl font-bold text-center text-gray-800">Finance Presale Page Generator</h1>
                <form method="post" class="space-y-4">
                    <div>
                        <label class="block text-gray-700 mb-1">Credit Card Name</label>
                        <input type="text" name="credit_card_name" required
                            class="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    </div>

                    <div>
                        <label class="block text-gray-700 mb-1">Target Audience</label>
                        <input type="text" name="target_audience" required
                            class="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    </div>

                    <div>
                        <label class="block text-gray-700 mb-1">Main Benefit</label>
                        <input type="text" name="main_benefit" required
                            class="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    </div>

                    <button type="submit" class="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition">
                        Generate Presale Page
                    </button>
                </form>
            </div>
        </body>
        </html>
        '''


if __name__ == "__main__":
    app.run(debug=True)
