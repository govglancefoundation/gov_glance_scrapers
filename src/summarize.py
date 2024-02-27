import re
import openai
import requests


def ai_summary(content):
    try:
        openai.api_key = os.environ.get('POSTGRES_USERNAME')
        response = openai.Completion.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt= str(content[:9950]) + " Tl;dr",
                    temperature=0.2,
                    max_tokens=100,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=1
                    ) 
        summary = (response['choices'][0]['text']).replace(':', '')
        summary = re.sub(r"^\W+", "", summary)
        period_count = summary.count('.')
        new = summary.replace(summary.split('.',period_count)[period_count],'')
        # new = (re.sub('[^a-zA-Z0-9 \n\.]', '', summary))
        # sum = (re.sub('(^.*[\.\?!]|^\S[^.\?!]*)', '', new))
        return new
    
    except openai.error.Timeout as e:
        #Handle timeout error, e.g. retry or log
        print(f"OpenAI API request timed out: {e}")
        summary = ''
        pass
        return summary
    except openai.error.APIError as e:
        #Handle API error, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        summary = ''
        pass
        return summary
    except openai.error.APIConnectionError as e:
        #Handle connection error, e.g. check network or log
        print(f"OpenAI API request failed to connect: {e}")
        summary = ''
        pass
        return summary
    except openai.error.InvalidRequestError as e:
        #Handle invalid request error, e.g. validate parameters or log
        print(f"OpenAI API request was invalid: {e}")
        summary = ''
        pass
        return summary
    except openai.error.AuthenticationError as e:
        #Handle authentication error, e.g. check credentials or log
        print(f"OpenAI API request was not authorized: {e}")
        summary = ''
        pass
        return summary
    except openai.error.PermissionError as e:
        #Handle permission error, e.g. check scope or log
        print(f"OpenAI API request was not permitted: {e}")
        summary = ''
        pass
        return summary
    except openai.error.RateLimitError as e:
        #Handle rate limit error, e.g. wait or log
        print(f"OpenAI API request exceeded rate limit: {e}")
        summary = ''
        pass
        return summary

def run_ai_sum(list_of_dict):
    data = list_of_dict
    for item in data:
        # this link will be scraped so we run the ai summarizers. 
        url = (item['download']['txtLink']+f'?api_key={KEY}')
        try:
            req = requests.get(url)
            stuff = req.get_content()
            soup = BeautifulSoup(stuff, features='lxml')
            content = []
            for words in soup.find_all():
                content.append(words.get_text())
            prompt = (''.join(content).rstrip().lstrip())
            summary = ai_summary(prompt, AIKEY)
            print(summary)
            item['description'] = summary
        except requests.exceptions.Timeout:
            item['description'] = ''
            pass
    return data