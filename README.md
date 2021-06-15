# Lightning Edit

Quickly edit your Slack posts. Heavily inspired by @KhushrajRathod's [LightningDelete](https://github.com/KhushrajRathod/LightningDelete).

## Usage:
> **Note:** Before anything, be sure to head over to [lightningedit.cwi.repl.co](https://lightningedit.cwi.repl.co) first, in order to let Lightning Edit access you account.

The sytax of Lightning Edit is extremely simple, just post the edited word with `*` added to it!

For example, if I had sent `their` instead of `they're`, all I would have to do is send another message with `*they're` and Lightning Edit will edit your original message with the change.

You can do more that just edit single words! Here are some other features:
 - `sed` style replacement! Like so: `*/regex_to_replace/what_with/flags`
 - To correct a single word, just type it after the asterisk: `*there`.
 - Want to edit a message that isn't your most recent? Just add more asterisks. `**there` will edit your second most recvent message.
 - Forgot to mention someone? Just type their names like `*@goat` or `*@goat @cow`, and the mention will be prepended to your original message.
 - If you need to *completely* rewrite your original message, just type `*!your new message here`, and the exclamation mark will force a complete overwrite.
 - Did you mess up a *lot* of spelling? Just type `*` by itself to fix all spelling mistakes. "I am reelly badd aat sppeelling" will turn to "I am really bad at spelling" in less than a second!
 - To append text to your original message, just type `*+text`, or just use more than one word, like `*text to be appended`.
 - I want to add more features! Just submit an issue or PR and I'll add it!

You can type `/editors` to get a list of all users using the app, as well as your authentication status.