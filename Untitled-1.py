import os
import time
import pandas as pd
from openai import OpenAI
import base64
import json
import neverbounce_sdk
from neverbounce_sdk import NeverBounceSDK
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

def main():
    
    file_path = r"C:\Users\ismai\Documents\Projects\EmailScraper\google.json"

    # Email functionality
    if file_path and os.path.exists(file_path):
        send_emails(file_path)

   
def generate_personalized_email(recipient_name, recipient_title):

    client = OpenAI(    
        api_key="API-KEY"
    )

    # Define your work history and experience
    work_history = f"""EDUCATION
    University of South Florida, 
    Major in Computer Science
    INTERNSHIP EXPERIENCE
    Hewlett Packard 
    Software Developer Intern
    • Led the development of a dynamic battery health manager feature in C for HP's AI PC line, extending battery life by
    up to 10% and saving the company ~$81.7 million by doing a in house software implementation.
    • Designed an algorithm to calculate and precisely measure battery impedance under various load conditions. and
    made dynamic adjustments to the battery's functional capacity, maximizing its longevity.
    • Optimized the algorithm through Real Time Operating System (RTOS) threads and event handlers, achieving a 30%
    improvement in processing efficiency on an ARM Cortex-M4 controller with limited memory and processing power.
    Bank of America 
    Software Developer Intern
    • Strategically led the integration of Oracle DB, employing advanced SQL queries and optimization techniques,
    resulting in a 15% processing time reduction for the Data Quality Control Framework.
    • Engineered visualizations using Tableau and Panda, propelling a 30% growth in operational efficiency, and
    contributing to substantial cost savings of $100,000, garnering high visibility and recognition from senior leadership.
    • Spearheaded the construction of an internal dashboard using React. integrating Oracle DB, yielding a 20% efficiency
    surge, positive user response, and improved cross-functional decisions.
    Time & Tune 
    Software Developer Intern 
    • Developed a responsive e-commerce website using Angular and Node.js, improving page load times by 25% and
    enhancing user experience, which led to increased customer satisfaction and a 10% rise in web traffic.
    • Implemented dynamic features, interactive elements, and integrated secure payment gateways, resulting in a 5%
    decrease in bounce rate, a 30% boost in sales revenue, and a 15% increase in customer trust and repeat purchases.
    • Optimized source code and conducted thorough testing using Jest and Selenium, reducing user-reported errors by
    15%, decreasing post-launch bugs by 40%, and improving overall site reliability; collaborated effectively within an Agile
    team, enhancing productivity by 20%.
    PART TIME EXPERIENCE AND LEADERSHIP
    SCORE Lab @ University of South Florida 
    Research Assistant Tampa, Florida
    • Developed an innovative mosquito trap using Fusion 360, integrating Raspberry Pi, sensors, cameras to automate
    high-quality video capture, which enhanced data collection for a machine learning mosquito classification algorithm.
    • Secured $1.6 million in NIH funding by contributing to the development of an AI classification algorithm and coauthoring a successful grant proposal, advancing research in vector-borne disease prevention.
    PROJECTS
    Academic Counselling Web Application using LLM 
    Angular, Node.js, OpenAI API, Mongo DB, AWS S3 Tampa, Florida
    • Engineered a scalable web application utilizing Angular and Node.js, leveraging Retrieval Augmented Generation
    model with OpenAI’s API to offer personalized class suggestions by training it on forthcoming classes, resulting in
    25% accurate class recommendations compared to traditional advising methods.
    • Developed a feature enabling users to input their academic transcripts and use that as additional training data for
    the model improving relevance and specificity of class recommendations increasing user engagement by 40%
    Payroll Machine Learning Application 
    Python, PyTorch, Fast API Tampa, Florida
    • Spearheaded the development of an ETL application using Python while leveraging PyTorch to construct a robust
    ML model enabling automated extraction of crucial employee data.
    • Leveraged cutting edge technologies e.g., Docker ensuring cross version compatibility, FASTAPI to construct a
    cloud-based web interface for ease of use, saving the university $52,000 in annual payroll labor and significant
    cost efficiency.
    """

    prompt = (f"Write a formal, short personalized email wihtout subject to {recipient_name}, who is a {recipient_title} at Acculynx. Donot right the salutation or the signature"
              f"Introduce yourself as Ismail Mustaali and my education and graduation  "
              f"Ensure that the email highlights my intrest in his field and seeing that the recipient is at a high level in the field i would love to learn from their experiences"
              f"and highlight one key part that is relevant from this {work_history} between his and mine after."
              )

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an AI assistant that generates concise, professional, and engaging emails to recruiters and managers."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-4o",  # Using GPT-4o (optimized version of GPT-4)
        max_tokens=300,
        temperature=0.5,
        top_p=0.8,
        frequency_penalty=0.2,
        presence_penalty=0.1
    )
    
    subject =  "Request for Career Advice from Ismail Mustaali"
    email_body_text = response.choices[0].message.content
    paragraphs = email_body_text.split('\n\n')
   # Format the email body as HTML with proper paragraph separation
    email_body_html = """
    <html>
    <body>

    <p>Dear {recipient_name},</p>
    """.format(recipient_name=recipient_name)

    # Add each paragraph wrapped in <p> tags
    for paragraph in paragraphs:
        email_body_html += f"<p>{paragraph.strip()}</p>"

    # Add the signature
    email_body_html += """
    <p>Warm regards,<br><br>
    <b style="color: green;">Ismail Mustaali</b><br>
    <b style="color: green;">Research Assistant</b><br>
    <i>University of South Florida</i><br>
    (813) 492-1901 | <a href="mailto:Ismailmustaali@usf.edu">Ismailmustaali@usf.edu</a> | 
    <a href="https://www.linkedin.com/in/ismailmustaali/">LinkedIn</a>
    </p>
    </body>
    </html>
    """

    # Return subject and body if needed
    return subject, email_body_html


def send_emails(file_path):
    # Set up Gmail API
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    # Initialize NeverBounce client
    neverbounce = NeverBounceSDK('YOUR_API_KEY')

    # Check if there is a token file with existing credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r"C:\Users\ismai\Documents\Projects\EmailScraper\client_secret_742078879026-phonfj6ct258m855n8ubl1ha6q8k4jg9.apps.googleusercontent.com.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Read the Excel sheet
    with open(file_path, 'r') as f:
        contacts = json.load(f)

    # Loop through each contact and send an email
    for contact in contacts:
        recipient_email = contact['email']
        recipient_name = contact['name']
        recipient_title = contact['position']

        if not recipient_email:
            continue

        # Generate personalized subject and body
        subject, body = generate_personalized_email(recipient_name, recipient_title)

        # Create the MIMEText email
        message = MIMEText(body, 'html')
        message['to'] = recipient_email
        message['from'] = "ismailmustaali@gmail.com"
        message['subject'] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        try:
            # Send the email using the Gmail API
            send_message = {
                'raw': raw_message
            }
            sent = service.users().messages().send(userId="me", body=send_message).execute()
            print(f"Email sent to {recipient_name} ({recipient_email})")
        except HttpError as error:
            print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
