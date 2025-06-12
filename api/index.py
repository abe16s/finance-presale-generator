from flask import Flask, request, render_template
from flask_cors import CORS
import openai
import os
import json

# Explicitly tell Flask where to find the templates
app = Flask(__name__, template_folder='../templates')
CORS(app)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
POSTHOG_API_KEY = os.getenv('POSTHOG_API_KEY')

@app.route('/', methods=['GET', 'POST'])
def generate_presale():
    if request.method == 'POST':
        card_name = request.form['credit_card_name']
        target_audience = request.form['target_audience']
        main_benefit = request.form['main_benefit']

        prompt = f"""
        You are a professional copywriter writing a high-converting blog-style presale page for a credit card offer. This content should look like a sponsored editorial article, designed to look organic and native, not like a direct ad.

        Use the following input variables:
        - Product Name: {card_name}
        - Target Audience: {target_audience}
        - Primary Benefit: {main_benefit}

        Write the output in the following JSON structure:
        {{
        "headline": "Clickbait-style, curiosity-driven headline",
        "subheadline": "Supporting subheadline",
        "publish_date": "Recent publish date, e.g., 'Updated: June 2025'",
        "hook": "Story-based or shocking intro paragraph",
        "body": ["Paragraph 1", "Paragraph 2", "Paragraph 3"],
        "bullets": ["Benefit 1", "Benefit 2", "Benefit 3", "Benefit 4", "Benefit 5"],
        "alert_block": "Urgency or warning block",
        "social_proof": "Optional stat or quote",
        "cta": "Short, strong action text like 'Check Eligibility'",
        "disclaimer": "Light legal note or sponsored disclaimer"
        }}

        Guidelines:
        - Make it persuasive, emotional, and informal — like a BuzzFeed or NerdWallet editorial review.
        - Break the copy into multiple sections with subheadings.
        - Use bold typography and an engaging, human tone.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

            gpt_reply = response.choices[0].message.content.strip()
            content = json.loads(gpt_reply)

            base_url = "https://card-apply-demo.site/offer"
            utm_campaign = card_name.lower().replace(" ", "_")  
            utm_source = "presale"
            utm_medium = "button"

            utm_link = f"{base_url}?utm_campaign={utm_campaign}&utm_source={utm_source}&utm_medium={utm_medium}"

            return render_template('presale.html',
                                   card_name=card_name,
                                   headline=content['headline'],
                                   subheadline=content['subheadline'],
                                   publish_date=content['publish_date'],
                                   hook=content['hook'],
                                   body=content['body'],
                                   bullets=content['bullets'],
                                   alert_block=content['alert_block'],
                                   social_proof=content['social_proof'],
                                   cta=content['cta'],
                                   disclaimer=content['disclaimer'],
                                   utm_link=utm_link,
                                   posthog_api_key=POSTHOG_API_KEY)

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
