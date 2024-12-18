Very early pre-alpha version of a Sports Management-style videogame based on FRC that myself and Evan Watson (Oregon State University) are slowly desigining

The codebase itself hasn't been tested for actually loading from the savefile (though the save file appears to work saving everything), but on an event-by-event basis it works
Note that it's only built for a game I designed. Modularity/multiple games will come much later.

Current roadmap (highly subject to change via the whims of my ADHD hyperfocus:)
* Add support for four-team elimination alliances
* Change matches to run one at a time, returning to a more limited menu while an event stage is in progress
* Add support for calling in backup robots during elims (likely using same backend as four-team alliances)
* Fix OPR calculations
* Add support for changing the game to prebuilt FRC games
* Decide which FRC games to use and seek out necessary permissions to use them should this actually be more than a personal for-fun project one day
* Create season-by-season tracking via savefile
* Add support for running multiple seasons in one code session
* Add support for adjusting team metrics (before and during a season)
* Add support for creating one's own FRC game
* GUI support (instead of DOS-like)
* Game elements: Focus on a team and adjust aspects of team (budget/fundraising, strategy, recruitment, awards?, etc.?) 
* (after Game elements) allow for peeking at results of other events the team is not in attendance at

Far future (likely won't happen anytime soon if at all):
* Randomly generate new FRC games, allowing for a theoretically infinite amount of seasons to be run with no repeat games
* Management of multiple teams
* External factor impact analysis (open alliance participation, region-by-region qualitative analysis, etc.)
* Match-by-match viewing of multiple non-participating events