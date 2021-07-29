# (2017) reddit-modmapper
Maps moderator/subreddit relationships for making a network graph. This code and the outputs have not been updated since 2017. I'm just archiving this information now. 

modmapper.py is a python script which uses the Reddit API, PRAW, to gather information about subreddits and moderators. This information is then formatted using the [networkx module](https://networkx.org/) into a .gexf file for plotting in [Gephi](https://gephi.org/). 



## Right Wing Mod Network (Jan 2017)
![Right wing moderator networks on reddit (Jan 2017)](graph-images/7sub_1yr_modnetwork.png "Right wing moderator networks on reddit (Jan 2017)")

Seven 1st-degree subreddit moderator relationships were overlaid to make this network graph. 1st degree, here refers to degrees of separation. For each of the subreddit neighborhoods, I started off with the target subreddit (listed below), and searched outward based on the moderators of the target sub. I stopped when I found the set of subreddits associated with all of those moderators. I did this for each of the 7 neighborhoods and joined them together to make this larger plot.

Some caveats: I did not include subreddits that haven't had any activity in the last 365 days, and moderators or users who have been banned were ignored. Additionally, common bots like AutoModerator were excluded because it's not really useful to look at. Essentially, this represents activity in the last year, minus user bans. Line thickness (edge weights) are determined by quantity of moderator relationships between two subreddits. So, thicker lines mean more moderators are shared between those two subreddits. Node size (circle sizes) are based on subreddit subscribers.

Color coding for each network:
- r/sjwhate = Yellow
- r/altright = Light Blue
- r/The_Donald = Green
- r/KotakuInAction = Light Pink (top right)
- r/WhiteRights = Light Red (bottom)
- r/TheRedPill = Orange
- r/MensRights = Purple


## Left Wing Mod Network (Jan 2017, requested selection)
![Left wing moderator networks on reddit (Jan 2017)](graph-images/8leftleaning_subs.png "Left wing moderator networks on reddit (Jan 2017)")

Color coding for each network:
- /r/shitredditsays = Yellow
- /r/me_IRL = Teal 
- /r/socialism = Pink 
- /r/communism = Red 
- /r/EnoughTrumpSpam = Grey 
- /r/TheBluePill = Orange 
- /r/GamerGhazi = Blue 
- /r/againstmensrights = Green

## 1st Degree Mod Network of r/Politics (Jan 2017)
![r/Politics 1 degree mod network (Jan 2017)](graph-images/politics_1Deg_subreddit_rels.png "r/Politics 1 degree mod network (Jan 2017)")

## 1st Degree Mod Network of r/neutralnews (Jan 2017)
![r/Politics 1 degree mod network (Jan 2017)](graph-images/politics_1Deg_subreddit_rels.png "r/Politics 1 degree mod network (Jan 2017)")

## 1st Degree Mod Network of r/uncensorednews (Jan 2017)
![r/Uncensorednews 1 degree mod network (Jan 2017)](graph-images/uncensorednews_60day_1deg.png "r/Uncensorednews 1 degree mod network (Jan 2017)")

## 1st Degree Mod Network of r/NSFW (Jan 2017)
![r/NSFW 1 degree mod network (Jan 2017)](graph-images/NSFW_1Deg_subreddit_modnetwork.png "r/NSFW 1 degree mod network (Jan 2017)")

## 2 Degree Mod Network of r/incels (Jan 2017)
![r/incels 2 degree mod network (Jan 2017)](graph-images/incels_2Deg_modnetwork.PNG.png "r/incels 2 degree mod network (Jan 2017)")
