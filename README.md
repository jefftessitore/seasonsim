Very early pre-alpha version of a Sports Management-style videogame based on FRC that myself and Evan Watson (Oregon State University) are slowly desigining

The codebase itself is only built for a game I designed. Modularity/multiple games will come much later.

The math calculations behind match simulation are getting an overhaul at some point

Current roadmap (highly subject to change via the whims of my ADHD hyperfocus:)
* Add support for four-team elimination alliances (IN PROGRESS)
* Change matches to run one at a time during elims (IN PROGRESS)
* Add ability to save/load ongoing event during elims (IN PROGRESS)
* Add support for calling in backup robots during elims (likely using same backend as four-team alliances) (ON DECK)
* Fix OPR calculations (ON DECK)
* Add offseason functionality
* Add support for changing the game to prebuilt FRC games
* Decide which FRC games to use and seek out necessary permissions to use them should this actually be more than a personal for-fun project one day
* Create season-by-season tracking via savefile
* Add support for running multiple seasons in one code session
* Add support for adjusting team metrics (before and during a season)
* Add support for creating one's own FRC game
* GUI support (instead of DOS-like)
* Randomly-generated event registration schedules per season
* Automated alliance selection
* Game elements: Focus on a team and adjust aspects of team (budget/fundraising, strategy, recruitment, awards?, etc.?)
* Add offseason team elements
* (after Game elements) allow for peeking at results of other events the team is not in attendance at
* Allow player to register for events
* Move everything to be more Object-Oriented (will happen naturally throughout the project but wanted to explicitly notate that this is a goal)

Far future (likely won't happen anytime soon if at all):
* Randomly generate new FRC games, allowing for a theoretically infinite amount of seasons to be run with no repeat games
* Management of multiple teams
* External factor impact analysis (open alliance participation, region-by-region qualitative analysis, etc.)
* Match-by-match viewing of multiple non-participating events
* Randomly generate new rookie teams when running new seasons (i.e. after donotchange.csv is set to '1')
* Allow for creation of junior/sister team(s) when team member number reaches a certain threshold
* Allow for a visual point-and-click selection of where to base team out of (think Airport CEO)
* Expansion of point-and-click selection: Preload list of existing FRC teams (at compile time) and associated communities/schools, warn player when community/school already has a team (prevent from selecting?)

COMPLETE:
* Qualification matches run one at a time
* Events can be saved/loaded during qualification rounds
