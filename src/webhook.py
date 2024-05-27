from groqqer import client, vector_search, gen_query_vector, logger
from datetime import datetime
import requests
import os
from dotenv import load_dotenv


def send_nfn():
    keywords = [
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "Natural Language Processing",
        "Robotics",
        "Automation",
        "Neural Networks",
        "AI Startups",
        "IIT (Indian Institutes of Technology)",
        "AI in Healthcare",
        "Sam Altman",
        "AI",
        "OpenAI",
        "LLMs",
    ]
    query_vector = gen_query_vector(", ".join(keywords))
    retrieved_docs = vector_search(query_vector)

    system_prompt = f"""
    Your role is to provide the user the best summary possible
    based on the following news.
    """ + "\n".join(
        [i for i in retrieved_docs]
    )

    prompt = "I need the best and detailed summary possible with headings and subheadings. Use markdown and emojis to make it look presentable in Discord. Should be less than 2000 characters."
    curdate = str(datetime.now().date())
    category = "AI"

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{prompt}"},
            ],
        )

        data = {
            "embeds": [
                {
                    "title": f"{curdate} | {category}",
                    "description": response.choices[0].message.content,
                }
            ]
        }

        response = requests.post(
            url=os.environ["DISCORD_WEBHOOK_URL"], json=data
        )

        logger.info(msg="Notification sent!")
    except Exception as e:
        logger.error(msg=f"Could not sent notification! {e}")
