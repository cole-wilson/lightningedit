import os
import re
import time
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_bolt.oauth.callback_options import CallbackOptions
from slack_bolt.response import BoltResponse
from slack_sdk import WebClient
from spellchecker import SpellChecker
from fuzzywuzzy import fuzz
from db import SQL

print('running.')
spell = SpellChecker()
db = SQL()

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
		client_id=os.environ.get("CLIENT_ID"),
		client_secret=os.environ.get("CLIENT_SECRET"),
		scopes=["commands"],
		user_scopes=["chat:write", "channels:history", "groups:history", "im:history", "mpim:history"],
		redirect_uri=None,
		install_path="/",
		redirect_uri_path="/slack/oauth_redirect",
		callback_options=CallbackOptions(success=success, failure=failure),
	),
)

def edit(old, new):
	new = new.strip(' ')
	# print(new)

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

	elif re.match(r"s?(/|!)(.*?)\1(.*?)\1.*?", new):
		_, a, b, f = re.findall(r"s(.)(.*?)\1(.*?)\1(.*?)", new)[0]
		b = re.sub(r"\$(\d*)", r"\\1", b)
		flags = []
		for flag in f:
			if hasattr(re, flag.upper()):
				flags.append(getattr(re, flag.upper()))
		return re.sub(a, b, old, *flags)

	elif new.startswith('+'):
		# append no matter what
		return old + " " + new[1:]
	
	elif new.startswith('!'):
		# completely redo
		return new[1:]
	
	elif re.match('^(<@.*?>\s?)+$', new):
		# add mention
		return new + " " + old
	
	elif len(new.split()) == 1:
		# fuzzy replacement
		ranked = [(word, fuzz.ratio(new, word)) for word in old.split()]
		bestmatch = max(ranked, key=lambda i: i[1])
		if bestmatch[1] > 50:
			return old.replace(bestmatch[0], new)
		else:
			return old + " " + new

	else:
		# just append
		return old + " " + new[1:]


@app.command("/editors")
def editors(command, ack, client):
	ack()
	user = command['user_id']
	text = "*:zap: Lightning Edit Users:*\n"
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

@app.message(r"^\*.*$")
def handle_edit(message, say, ack, client):
	print('>> message <<')
	ack()

	thismessage = message
	# print(message)
	user = thismessage['user']
	channel = thismessage['channel']
	raw_text = thismessage['text']
	text = raw_text.lstrip('*').strip(' ')
	amount = len(raw_text) - len(text)

	if user not in db: return

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
			text = 'Sorry, I couldn\'t find anything to delete! Prefix your text with a comma or something in order to prevent me from deleting it.',
		)
	userclient.chat_delete(channel=channel,ts=thismessage['ts'])

@app.event('message')
def _(ack): ack()

if __name__ == "__main__":
	app.start(port=int(os.environ.get("PORT", 3000)))
