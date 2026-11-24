# Handoff from the cloud session: sombr MSG pitch (Tue Nov 24, 2026)

This is written for Mel's local Claude session. It covers everything from the cloud session that isn't already in PITCH.md, CONTACTS_APOLLO.md or OUTREACH_20.md. The footage itself never reached the cloud session.

## 1. Mel's instructions and preferences

### Goal
Get hired to shoot behind-the-scenes content for sombr at the MSG finale tonight. "I want him and his brand to choose me."

### The story to capture
- What it feels like to perform at MSG in the city where he grew up.
- The whole crowd loving and singing every one of his songs.

### Timeline
- Mel saw night 1 (Nov 23).
- Tonight is night 2. It is the final show of the "You Are The Reason" tour, his first North American arena tour.
- Captions used so far: "night one at the Garden / a kid from New York / every word, back at him / one more night / home."
- Press calls it his hometown show, and Stanford Daily wrote that his set "transforms the Bay into the Lower East Side".
- Otherwise, the Lower East Side detail is unconfirmed. Don't state it as fact.

### Screenshots
- One video has screenshots of Mel's favorite moments. Find those exact moments and make clips from them.
- `find_moments.py <clips> <screenshots> <out>` does this. It decodes every frame, trims phone UI bars and letterboxing, and writes the best-matching frame per screenshot to `moments.json`, plus stills.

### Go through everything
- Look at every frame of every clip and listen to the full audio, not just the start.
- For the rest of the footage, use your own judgment on which moments to turn into content.

### Audio
- One edit uses "My Body Isn't Ready" as the background vocals.
- Another uses "Back to Friends".
- Experiment with the rest.
- I recommended using Mel's own crowd recordings of those songs (the whole room singing them), not studio tracks.

### Montage styles
Mel said "experiment and try different ones" (grainy and film-y versus clean and high-contrast). `make_montages.py <clips> <out>` produces:
- a 30s hype reel
- a 60s hometown vlog
- a 15s teaser
- a contact sheet

It renders 9:16 by default. Set `WIDE=1` for 16:9 versions and `SHOOTER=@handle` for the end cards.

### Photos
Pull stills that capture the vibe and edit them in Lightroom.

### Working style
Mel strongly wants **no questions and no permission requests**. In her words: "stop asking me, just build it" and "you have full access to everything." Make sensible calls and keep going.

### Footage location
The Somber folder in iCloud Drive (it was still uploading). Mel also mentioned a Seagate drive.

## 2. Contacts

The full table is in CONTACTS_APOLLO.md. Extras that aren't in it:

**Instagram**
- @sombr is the verified main account. @sombrsucks is his second account.
- @kevinmazur: the Getty photographer who shot this tour for AEG.
- @thegarden: MSG.
- Possible @annperkinss for Ann Perkins (unconfirmed).
- @sombrontour and @sombrteam are **fan accounts. Don't pitch them.**

**More people**
- Gus Black: directs his music videos. Handle @MrGusBlack, platform unconfirmed.
- Bryce Glenn: photographer and creative director on the "Undressed" shoot. itsnova.com/bryceglenn
- Chris Steiger: shot the Atlanta show.
- Juliette Carter: manages opener Hannah Jadagu (Lads Lads Lads).
- Jess Braunstein: on UTA's sombr team. Email format is first.last@unitedtalent.com.

**Caveats**
- The other opener tonight is Dove Cameron.
- Sacks & Co may be his *former* publicist. BookingAgentInfo lists the current press team only as "Ceri R., Laura S., Lily G."
- Warner laid off about a dozen staff in early November, including Dalia Ganz (EVP digital), Torie Mason and Fount Lynch.

**Top priority:** Ann Perkins, aperkins@thesystemgroup.com. She is in his core decision group, with Shane and his dad Andy Boose.

## 3. Gmail drafts

All drafts are in Mel's Gmail and none have been sent. Each has the placeholders `[LINK TO MSG EDITS]`, `[PORTFOLIO LINK]`, `[PHONE]` and `[@INSTAGRAM]`, and is signed "Mel".

| # | To | Subject |
|---|---|---|
| 1 | Kate Rakvic, cc Carla Sacks | sombr MSG: night one footage + offer to shoot the finale tonight |
| 2 | Ann Perkins | Filmed sombr at the Garden last night: can I shoot tonight? |
| 3 | Theresa Abou-Daoud + Noah Almekinder | sombr MSG: BTS shooter for tonight, zero lift for you |
| 4 | Devin Sarno | sombr at MSG: footage from night one + offer to shoot the finale |
| 5 | Sam Riddle + Will Morrow, cc TJ Landig | Same-night sombr MSG edits for socials: free, tonight |
| 6 | Cori Gadbury + Matt Meyer, cc JT Taylor | sombr MSG finale: free BTS content for tour recap |
| 7 | Kelly Sarno + Lukas Lennon | BTS / second camera for sombr shoots |

The offer in every draft: pre-show city footage, backstage, or second camera for the tour photographer. Free, they own all the footage, and edits by tomorrow morning.

## 4. Ideas not in PITCH.md
- **Lead with DMs** on the same day: @sombr, the tour photographer, and @kevinmazur. Attach the 15s teaser directly.
- **Find the current tour photographer or videographer** from the photo credits on @sombr's last 10 posts. DM them offering to second-shoot or run B-roll. A peer referral is the easiest yes.
- **Keep the ask small.** Pre-show NYC street and hometown footage needs no credential. Shoot outside MSG before doors and send it tonight either way.
- **Same-night vertical edits** are the hook for Warner digital (Riddle and Morrow).
- **Opener teams** (Juliette Carter for Hannah Jadagu, and Dove Cameron's team) may want BTS too. That's a backdoor onto the site.
- **Follow up 2–3 hours later.** A LinkedIn note of 300 characters or less is in CONTACTS_APOLLO.md.
- **Post the edits tagging @sombr and @thegarden tonight**, even if nobody replies.
- **Never claim any affiliation.** Credit the music to him and his team.

## Portfolio

There are three unpublished Lovable versions. Each is built from Mel's Quinn XCII SXSW films plus her Vérité Visuals work.

| Version | Look | Preview |
|---|---|---|
| A (recommended) | '70s gig poster: black, film grain, orange like his stage pipes | https://id-preview--a455fdef-2c71-4260-9ce8-dccc5358a85e.lovable.app |
| B | "Late Night": stark, wall of TV monitors | https://id-preview--280ab8d4-a885-4bc8-8905-c364a8451858.lovable.app |
| C | "Zine": grunge scrapbook | https://id-preview--bfbe7444-160e-4f92-b0d1-4d8f1ad3d2ff.lovable.app |

- Each version has a hidden "Madison Square Garden" section. It appears once you add films to the `nycFilms` array.
- Some inner pages still say "we/Vérité" and need rewording in Mel's voice.
- Version C's contact email is still hi@veriteandco.com.
- The original site is the "Vérité Visuals" Lovable project. Its /concerts page has the Quinn films.

## Visual research on sombr (for grading and design)
- Retro '70s alt-rock and New York new wave.
- "2014 Tumblr grunge" (Rolling Stone, on "Back to Friends").
- The "12 to 12" video has a late-night talk show concept. It was directed by Gus Black and stars Addison Rae.
- The tour set recreates a Lower East Side street: awnings, fire escapes, large orange pipes spewing smoke, a black curtain drop, and live camera feeds on big screens.
