# 2023 SE AI Hackathon
Welcome to the 2023 SE Meetup, featuring an SE AI Hackathon hosted by Rob Masson and Brian Mgrdichian. We will be walking through an application of Large Language Models, discussing the technology, discovering the tools utilized, and further understanding the approaches & opportunities to explore this technology through the hackathon! Teams of SEs will compete for lucrative prizes. More info can be found in your email.

###### A special thanks to Pooja Srinath for her help and input! 😊 

## Introduction

We're going to start our project just like we start any other great hackathon: borrowing some code that isn't throwing a bunch of errors at the present moment.


 The code we're starting with is borrowed heavily from the [**"Build a Question-Answering over Docs SMS Bot with LangChain in Python"**](https://www.twilio.com/blog/qa-over-docs-bot-langchain-python) Twilio blog by [Lizzie Siegle](https://www.twilio.com/blog/author/lsiegle). We are going to alter it **just a bit** to read from the [CTIA Short Code Monitoring Program Handbook](https://www.10dlc.org/ctia_short_code_monitoring_handbook_-_v1.8.pdf) instead of the .txt file in the blog. This will give us a knowledge base of SMS best practices with which we can have a demo up and running as our "square one".
 
 Where you go after square one is completely up to you! You'll be given judging criteria to read through, so please be sure to keep these them in mind as you build.
___
## Installation
###### Note: We'll focus on Mac instructions. See [Lizzie's blog](https://www.twilio.com/blog/qa-over-docs-bot-langchain-python) for Windows instructions.

### 1. Clone and `cd` to the repo
```bash
git clone https://github.com/brianmgr/se-ai-hackathon.git
cd se-ai-hackathon
```

### 2. Activate a new Python virtual environment
Enter the following commands in your terminal, one at a time:
```bash
python3 -m venv venv 
source venv/bin/activate
```
At this point, you should see `(venv)` in front of your terminal input.
###### (If you need to exit the virtual env, you can use the command `deactivate`. You don't need to right now though!)

### 3. Install dependencies
Enter the following commands in your terminal, one at a time:
```bash
!pip install langchain
!pip install requests
pip install flask
pip install faiss-cpu
pip install sentence-transformers
pip install twilio
pip install load_dotenv
```

### 4. Get a HuggingFace token
If you haven't yet signed up for Hugging Face Hub yet, you can do that [here](https://huggingface.co/join?next=%2Fsettings%2Ftokens).
Now, visit https://huggingface.co/settings/tokens and create a token. The name can be anything, but be sure it has the Read role. 


### 5. Store your HuggingFace token in a .env file
This is optional, you can manually set environment variables if you prefer.
```bash
echo "HUGGINGFACEHUB_API_TOKEN=[token copied from last step]" >> .env
```

### 6. Run `app.py`
```bash
python3 app.py 
```
You should see debugger output like this:
```python
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:8001
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 111-111-111
```

### 7. Test it locally
There is a local endpoint you can hit (cleverly located at `/local`) before we start looping in SMS or other channels. Let's try hitting that with `curl` in another terminal tab:
```bash
curl -X POST "http://127.0.0.1:8001/local" --data-urlencode "Body=What are the 6 best practices when sending compliant SMS?"
```
Here's the example response:

>The 6 best practices when sending compliant sms are: 1. Track opt-in information by individual Consumers. 2. Create and vet their own opt-in lists. 3. Send opt-in confirmation messages. 4. Acknowledge and honor opt-out requests. 5. Monitor and confirm successful opt-outs. 6. Use a secure and reliable platform.

This answer is pretty good, but it might leave a little bit to be desired. Make sure to look into [Prompt Engineering](https://en.wikipedia.org/wiki/Prompt_engineering) to get better results.


### 8. Hook it up to the internet with ngrok
We'll use [ngrok](https://ngrok.com/download) to open our service up to the internet so our Twilio phone number webhooks can point to it.
###### Note: When using ngrok to connect Twilio Webhooks to the local running Python app, you may need to include a particular parameter to rewrite the host-header:
```bash
ngrok http 8001 --host-header rewrite
```
This will hand back a `Forwarding` URL that points to your local app. Copy this URL for the next step.
```bash
https://00d00e0d000b.ngrok.app -> http://localhost:8001
```

### 9. Configure Twilio number to hit your app
Purchase and [configure](https://support.twilio.com/hc/en-us/articles/223136047-Configure-a-Twilio-Phone-Number-to-Receive-and-Respond-to-Messages#h_5fd3801f-8241-421f-ad0f-8fb6c25ba68c) a Twilio number. In the `"A MESSAGE COMES IN"` field, choose Webhook and put in your ngrok URL, appending `/sms` to the end of it. This endpoint in the Flask app will format the response in TwiML for an SMS response.
```bash
eg: https://00b00e0d000b.ngrok.app/sms
```

### 10. Test with SMS
Text your Twilio number with a question about CTIA guidelines. Remember- generative AI can be slow, so if you're not seeing an error, give it 10-30 seconds to get a response before hitting `ctrl+c` to debug.
___

## What next?

### Clean it up, change it, ditch it!

There are some parts of the code that could be refined to make the code more efficient, such as:
1. [Not pulling the CTIA PDF every single time.](/app.py?#L43)
2. [Changing the temperature of the LLM to be less deterministic.](/app.py?#L67)
3. [Change the LLM altogether.](/app.py?#L67)

Feel free to build something without using this codebase at all. Make something wild and win that moolah!

---
## Example prompts and their responses
### 1. ✅ I got the information I expected
```bash
curl -X POST "http://127.0.0.1:8001/local" --data-urlencode "Body=When does an opt-in confirmation message need to be sent?"
The opt-in confirmation message must be sent immediately after the Consumer opts into the program.
```

### 2. ✅ Perfect!
```bash
curl -X POST "http://127.0.0.1:8001/local" --data-urlencode "Body=How long should I maintain opt-in and opt-out records?"
The opt-in and opt-out requests should be retained until a minimum of six months after the Consumer has opted out of a program.
```

### 3. ❌ I didn't get a good answer because I didn't ask a good question.
```bash
curl -X POST "http://127.0.0.1:8001/local" --data-urlencode "Body=What is opt-in?"
The answer is opt-in.
```

### 4. ✅ I fixed the above prompt by asking a more specific question.
```bash
curl -X POST "http://127.0.0.1:8001/local" --data-urlencode "Body=What's the CTIA's definition of opt-in?"
The CTIA definition of opt-in is that a consumer agrees to receive messages from a company and agrees to be contacted by a company in order to receive information about the company.
```
