# The Key Ring

Some Build Room tools work much faster with a key to one of the member's own accounts: GoHighLevel for the push and the funnel numbers, an image or video provider for the Ad Studio and the Video Director. The Key Ring is how a member adds a key without ever typing it into the chat. Any session that needs a key uses it; the script lives here, in `buildroom-os`, at `scripts/key_ring.py`.

It needs a session that can run commands on the member's computer (Claude Code or Codex). In a chat that cannot run commands, say so and give the hand route at the bottom.

## The rules, every time

1. **A key never goes in the chat.** Never ask for one, never repeat one, never put one on a command line. If the member pastes one anyway, do not use it from the chat: tell them it is now in the conversation history, that they should make a new one in their account, and open the Key Ring for the new one.
2. **Never open, print or read aloud** `.env` or `~/.buildroom/keys.json`. `key_ring.py list` tells you everything you are allowed to know: names, dates, the last four characters, working or not.
3. **One key ring per computer.** A key is added once. Every other folder gets it with `add` or `link`, with nothing asked.
4. **Say what is true about safety.** The keys sit as ordinary text in two private files on the member's computer (the ring in their home folder, and the `.env` in each working folder). They are as safe as the computer's login. They are not sent to Build Room. A key goes online only to the provider it belongs to.
5. **Affiliate links carry the disclosure.** `key_ring.py catalog` gives each provider's sign-up links. When you offer an affiliate link, put this sentence right next to it, word for word, and offer the plain route too: *This is my affiliate link. If you sign up through it, I earn a commission, at no extra cost to you.* The page does this by itself. Never quote a price or a discount: the member reads the current price on the provider's site.

## Adding a key

When a session reaches a step that needs a key, or the member says "add my GoHighLevel key":

1. Run `python3 <buildroom-os>/scripts/key_ring.py add gohighlevel` from the member's working folder. It prints one line of JSON.
2. `{"event": "linked"}`: the key was already on this computer. The folder's `.env` is filled. Say so in one sentence and carry on.
3. Otherwise a page opens in the member's browser. Tell them: "A page just opened in your browser. It shows where to get the key and has a box to paste it into. Come back here when it says Saved." If the first line of output says the browser did not open, give them the address it printed: it works only on their computer.
4. `{"event": "none"}` means they are still getting the key. Run `key_ring.py wait` again, as many times as it takes. Do not hurry them. The page stays open for 30 minutes.
5. `{"event": "saved", "works": true}`: done. Carry on with the step that needed it.
   `"works": null`: saved but not checked (the provider could not be reached, or it has no safe check). Say so, and let the first real use show it.
   `"works": false`: the member chose to save a key the provider refused. Say that the tool will not work until the key is right.
   `{"event": "closed"}`: the page went away with nothing saved. Ask whether they want to try again.
6. If the event carries `env_problem`, read it out and run the `link` command it names.

The page checks the key with the provider before it saves. A refused key is not saved unless the member presses "Save it anyway".

## The other commands

| The member says | Run |
|---|---|
| "Show my keys" | `key_ring.py list`, then a short table: provider, added on, ending, working or not, in this folder or not |
| "Are my keys still working?" | `key_ring.py check` |
| "Use my keys in this folder" | `key_ring.py link gohighlevel kie` (the ones this folder's work needs, not every key) |
| "Change my GoHighLevel key" | `key_ring.py add gohighlevel --replace` |
| "Remove my Kie key" | Ask first. Then `key_ring.py remove kie --yes`. Tell them this takes it off the computer's ring and this folder only; to make the key useless everywhere they delete it in their account with the provider. |
| "What keys can I add?" | `key_ring.py catalog` |

Providers it knows: `gohighlevel` (also `ghl`), `kie`, `higgsfield`, `heygen`, `submagic`. GoHighLevel, Kie.ai and HeyGen keys are checked on save; GoHighLevel's check was run against a real account. The Kie.ai and HeyGen checks have not been confirmed against the live services, so they count only a clear yes or a clear no, and a member whose good key is refused can press "Save it anyway". Higgsfield and SubMagic keys are saved without a check.

## GoHighLevel, specifically

The page walks the member through making a private integration in their own sub-account, with read permissions plus Edit Custom Values, and tells them to leave everything under Conversations off: Build Room never sends messages as the member. It saves the token as `GHL_TOKEN` (and as `GHL_API_KEY`, the name the Funnel Map and Decision Machine pushes read) and the location as `GHL_LOCATION_ID`. If a tool later reports that the token is not allowed to do something, the member adds that one permission to the same integration; the token does not change and nothing needs adding again.

## Any other key, by hand

For a key the Key Ring does not know (for example a website builder's), or where no commands can run: "Open the file named `.env` in your working folder in a text editor, add one line like `NAME=your-key`, and save. Do not paste the key here." Then make sure `.env` is listed in `.gitignore` if the folder is a git project.
