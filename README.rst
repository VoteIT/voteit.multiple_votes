Introduction
============

Multiple votes for users. This is an opt-in addon for meetings that will
allow voters to hold multiple votes.

Note that this plugin will change the behaviour in some ways, most notably that you must never asign vore permissions through the participants list or invitations.

Step by step guide:

* Activate this from the control panel. Pick a name for the entities that causes users to have several votes. (Like "Organisations")
* Add organisations.
* Add users to them. One user may be responsibe for several organisations.
* Lock the voting registry through the workflow menu. An electoral register will be created for you automatically, if needed.
* Simply start any votes!
* If you need to change the voting permissions, close the votes first and then change the workflow from locked to open within the multivote-context.

Some caveats:

* Again: Don't assign voting permissions to a user when using this. Not through invitation tickets or the participants screen.
* A lot of votes may cause errors when voting a a lot of people at the same time. This is due to a limitation in how this version of VoteIT is built - it's not possible to store votes at exactly the same time. Users will receive an error when trying to save their vote if that happens, simply press vote again in that case.
* The projector-views vote count isn't compatible with this. It will count users with voter role rather than the number of votes, so having 100 votes with 20 voters might look weird since each voter has several votes. There's no harm in using it though, but it requires some explaining.

Current bugs:

* When opening or closing a vote, the moderators will see the wrong vote-count. Reload the page and it will be displayed correctly.

Web: http://www.voteit.se
