print('running.')

import os
import re
import time
import random
import logging
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_bolt.oauth.callback_options import CallbackOptions
from slack_bolt.response import BoltResponse
from slack_sdk import WebClient
from spellchecker import SpellChecker
from fuzzywuzzy import fuzz
from db import SQL

logging.basicConfig(level=logging.WARNING)
spell = SpellChecker()
db = SQL()

def boot(channel="C0P5NE354"):
	client = WebClient(token=os.environ['TOKEN'])
	message = os.getenv('RAILWAY_GIT_COMMIT_MESSAGE', 'redeploy')
	message = f":party-parrot:I JUST WOKE UP AGAIN! Here's what's new: `{message}`."
	client.chat_postMessage(channel=channel, text=message)

boot()

def success(args):
	user_id = args.installation.user_id
	user_token = args.installation.user_token
	db[user_id] = user_token
	print(db.keys())
	return BoltResponse(status=200,body="success!")

def failure(args):
	return BoltResponse(status=args.suggested_status_code,body="failure :(")

app = App(
	signing_secret=os.environ.get("SIGNING_SECRET"),
	oauth_settings=OAuthSettings(
		token=os.environ.get("TOKEN"),
		client_id=os.environ.get("CLIENT_ID"),
		client_secret=os.environ.get("CLIENT_SECRET"),
		scopes=["commands", "chat:write.public", "chat:write"],
		user_scopes=["chat:write", "channels:history", "groups:history", "im:history", "mpim:history", "reactions:write"],
		redirect_uri=None,
		install_path="/",
		redirect_uri_path="/slack/oauth_redirect",
		callback_options=CallbackOptions(success=success, failure=failure),
	),
)

def edit(old, new):
	new = new.strip(' ')
	sedstyle = r"s?(/|!)(.*?)\1(.*?)\1.*?"
	
	# correct everything
	if new == "":
		# spellcheck
		out = ""
		words = old.split()
		for word in words:
			if word.startswith(':'):
				out += word + " "
			else:
				out += spell.correction(word) + " "
		return out

	# sed style replace
	elif re.match(sedstyle, new):
		_, a, b, f = re.findall(sedstyle, new)[0]
		b = re.sub(r"\$(\d*)", r"\\1", b)
		flags = []
		for flag in f:
			if hasattr(re, flag.upper()):
				flags.append(getattr(re, flag.upper()))
		return re.sub(a, b, old, *flags)

	# append
	elif new.startswith('+'):
		# append no matter what
		return old + " " + new[1:]

	# overwrite
	elif new.startswith('!'):
		# completely redo
		return new[1:]

	# add punctuation
	elif re.match(r"^(\?|!)*$", new):
		return old + new

	# strikethrough
	elif re.match('^-*?$', new):
		return "~" + old + "~"

	# add mentions
	elif re.match('^(<@.*?>\s?)*$', new):
		return new + " " + old

	# fuzzy replacement
	else:
		threshold = 55
		def _fuzzypos(word, string, precedence=0):
			string = string.split()
			enum = enumerate(map(lambda i:fuzz.ratio(word,i),string))
			maxi = sorted(filter(lambda i:i[1]<100,enum),key=lambda i:i[1])
			if len(maxi) == 0:
				return False
			top = maxi[-1][1] # the top ratio
			maxi = list(filter(lambda i:i[1]==top and i[1], maxi))[precedence]
			if maxi[1] < threshold:
				return None
			return maxi[0]

		s_index = _fuzzypos(new.split()[0], old)
		e_index = _fuzzypos(new.split()[-1], old, precedence=-1)
		if s_index is None or e_index is None:
			print(old + " " + new)
		if s_index is False or e_index is False:
			print(old)
		section = " ".join(old.split()[s_index:e_index+1])
		ratio = fuzz.partial_token_sort_ratio(section, new)
		if ratio >= threshold:
			print(old.replace(section, new, 1))
		else:
			print(old + " " + new)

@app.command("/editors")
def editors(command, ack, client):
	ack()
	user = command['user_id']
	text = f"*:zap: Lightning Edit Users:* _({len(db.keys()) - 1})_\n"
	for u in db.keys():
		text += f":large_green_circle: <@{u}>\n"
	text += f"\nYou, (<@{user}>), have "

	if user in db.keys():
		text += "successfully installed Lightning Edit!"
	else:
		text += "have NOT successfully installed Lightning Edit.\n"
		text += "Head over to https://lightningedit.colewilson.xyz to get started."

	client.chat_postEphemeral(
		attachments = [],
		channel = command['channel_id'],
		user = user,
		text = text,
	)

@app.message(r"^\^*?$")
def upvote(message, say, ack, client):
	ack()

	thismessage = message
	user = thismessage['user']
	channel = thismessage['channel']

	if channel == "C0255PRDR44": return
	if user not in db:
# 		client.chat_postEphemeral(
# 			attachments = [],
# 			channel = channel,
# 			user = user,
# 			text = 'Hello. Are you trying to use Lightning Edit? Head over to https://lightningedit.colewilson.xyz to get started!',
# 		)
		return

	userclient = WebClient(token=db[user])

	if 'thread_ts' in thismessage:
		messages = reversed(userclient.conversations_replies(channel=channel,ts=thismessage['thread_ts'])['messages'])
	else:
		messages = userclient.conversations_history(channel=channel)['messages']
	message = list(messages)[1]
	try:
		userclient.reactions_add(channel=channel,name="upvote",timestamp=message['ts'])
	except:
		pass
	userclient.chat_delete(channel=channel,ts=thismessage['ts'])

@app.event("app_mention")
def random_response(client, body):
	db['test'] = time.time() # set SQL so it doesn't disconnect

	text = body["event"]["text"]
	user = body["event"]["user"]
	client.chat_postMessage(text=random.choice([
		f"Hi <@{user}>, I'm still here!",
		f"<@{user}> spels reely wel: i should no.",
		f"Hey <@{user}>: grammer you do very bad, lol.",
		f"Sorry <@{user}>, I'm correcting @...'s spelling. I'll get back to you in just a second.",
		f'<@{user}>:'+" ".join(map(lambda i: hex(ord(i))[2:], text)),
		f'<@{user}>:'+" ".join(map(lambda i: bin(ord(i))[2:], text)),
		f'<@{user}>:'+" ".join(map(lambda i: oct(ord(i))[2:], text)),
		f'<@{user}>:" '+"".join(map(lambda i:random.choice((i.upper,i.lower))(),text))+'"'
	]), thread_ts=body['event']['ts'], channel=body['event']['channel'])

@app.message(r"^-*?$")
@app.message(r"^(\?|!)*$")
@app.message(r"^\*.*$")
def handle_edit(message, say, ack, client):
	ack()


	thismessage = message
	user = thismessage['user']
	channel = thismessage['channel']
	raw_text = thismessage['text']
	text = raw_text.lstrip('*').strip(' ')
	amount = max(len(raw_text) - len(text), 1)

	if channel == "C0255PRDR44": return
	if user not in db:
# 		client.chat_postEphemeral(
# 			attachments = [],
# 			channel = channel,
# 			user = user,
# 			text = 'Hello. Are you trying to use Lightning Edit? Head over to https://lightningedit.colewilson.xyz to get started!',
# 		)
		return

	userclient = WebClient(token=db[user])

	if 'thread_ts' in thismessage:
		messages = reversed(userclient.conversations_replies(channel=channel,ts=thismessage['thread_ts'])['messages'])
	else:
		messages = userclient.conversations_history(channel=channel)['messages']

	messages = filter(lambda i: 'user' in i and i['user']==user, messages)
	messages = list(messages)

	try:
		old_message = messages[amount]
		if old_message['text'] == text: return
		newtext = edit(old_message['text'], text)
		userclient.chat_update(
			channel = channel,
			ts = old_message['ts'],
			text = newtext,
		)
	except Exception as err:
		print(err)
		client.chat_postEphemeral(
			attachments = [],
			channel = channel,
			user = user,
			text = 'Sorry, I couldn\'t find anything to edit! Prefix your text with a comma or something in order to prevent me from editing it.',
		)
	userclient.chat_delete(channel=channel,ts=thismessage['ts'])
	print('>> message handled <<')

@app.event('message')
def _(ack): ack()

if __name__ == "__main__":
	app.start(port=int(os.environ.get("PORT", 3000)))
