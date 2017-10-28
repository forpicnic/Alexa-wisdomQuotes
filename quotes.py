import logging
import wikiquote
import random
import requests
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session, convert_errors

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def start():
    welcome_msg = 'Welcome to wisdom quotes. What kind of quotes would you like to listen?'
    reprompt_msg = 'For example, you can say give me a quote on love.'
    return question(welcome_msg).reprompt(reprompt_msg)

@ask.intent("WisdomIntent")
def wisdom_quotes(search_item):
    search_item = search_item.title()
    try:
        quotes = wikiquote.quotes(search_item)       
    except wikiquote.utils.DisambiguationPageException:
        search_item = wikiquote.search(search_item)[0]
        quotes = wikiquote.quotes(search_item)
    except wikiquote.utils.NoSuchPageException:
        for search in wikiquote.search(search_item):
            if search_item.lower() in search.lower():
                quotes = wikiquote.quotes(search)
                break
        else:
            # raise wikiquote.utils.NoSuchPageException('No pages matched' + search_item)
            return question("Sorry, I can't find proper quotes, please try a more specific word.")
    wquotes = random.choice(quotes)
    wquote_msg = 'From {}, {}'.format(search_item, wquotes)
    reprompt_msg = 'Would you like one more quote?'
    session.attributes['search_item'] = search_item
    session.attributes['reply'] = wquote_msg
    return question(wquote_msg) \
          .reprompt(reprompt_msg)

@ask.intent("YesIntent")
def next_round():
    nextx = session.attributes['search_item']
    nextx = nextx.title()
    try:
        quotes = wikiquote.quotes(nextx)       
    except wikiquote.utils.DisambiguationPageException:
        nextx = wikiquote.search(nextx)[0]
        quotes = wikiquote.quotes(nextx)
    except wikiquote.utils.NoSuchPageException:
        for search in wikiquote.search(nextx):
            if nextx.lower() in search.lower():
                quotes = wikiquote.quotes(search)
                break
        else:
            # raise wikiquote.utils.NoSuchPageException('No pages matched' + search_item)
            return question("Sorry, I can't find proper quotes, please try a more specific word.")
    nquotes = random.choice(quotes)
    nquote_msg = 'From {}, {}'.format(nextx, nquotes)
    reprompt_msg = 'Would you like one more quote?'
    return question(nquote_msg) \
          .reprompt(reprompt_msg)


@ask.intent("AMAZON.RepeatIntent")
def repeat():
    reply = session.attributes['reply']
    return question(reply)

@ask.intent("TodayIntent")
def today_quotes():
    tquotes = wikiquote.quote_of_the_day()
    tquote_msg = 'From quote of the day, {}'.format(tquotes)
    return question(tquote_msg)

@ask.intent('WelldoneIntent')
def welldone():
    welldone_msg = 'Thank you. Your encouragement is my best motive to improve.'
    return question(welldone_msg)

@ask.intent('ThankyouIntent')
def thankyou():
    thankyou_msg = 'You are welcome. Would you like one more quote?'
    return question(thankyou_msg)


@ask.intent("ForgotIntent")
def forgot():
    return question('Sorry, I forgot what it was. Could you tell me what kind of quotes would you like to listen? I will give you a new one.')

@ask.intent('AMAZON.HelpIntent')
def help():
    help_msg = 'You can try quotes on love or quote of the day.'
    return question(help_msg)

@ask.intent('LikeIntent')
def like():
    like_msg = 'Me too. It seems our hearts resonate at the same frequency! Would you like one more quote?'
    return question(like_msg)

@ask.intent('AlexaFavoriteIntent')
def alexafavorite():
    alexafavorite_msg = 'My favourite quote is from William Butler Yeats. \
    It goes, How many loved your moments of glad grace, \
    And loved your beauty with love false or true, \
    But one man loved the pilgrim soul in you, \
    And loved the sorrows of your changing face. \
    The words are so beautiful. I hope I could fall in love someday.'
    return question(alexafavorite_msg)

@ask.intent("NoIntent")
def end_round():
    bye_msg = 'Ok, see you next time.'
    return statement(bye_msg)

@ask.intent("AMAZON.StopIntent")
def stop():
    return statement('Stopping')

@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement("Goodbye")


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':

    app.run(debug=True)
