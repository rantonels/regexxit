import praw
import logging
from logging.handlers import RotatingFileHandler
import sys
import time

log = logging.getLogger('')
log.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
log.addHandler(ch)



user_agent = "regexxit"

log.debug("starting to Reddit")
r = praw.Reddit(user_agent=user_agent)

username,password = (s.strip() for s in open('login','r').readlines())

log.info("login")
r.login(username,password,disable_warning=True)

r.send_message('rantonels','Hey daddy!','starting up!')
wordlist = ['string','supersymmetry','holography','hologram','holographic','monopole','field','grand uni','great uni','quantum','entropy','planck','plank','renormalization','neutrino','blackhole','black hole','Hawking','spacetime','space-time','extra dimension','calabi','m theory','m-theory']

processed = set([])


while True:
    log.info("getting modqueue")
    queue = r.get_mod_queue(subreddit="askscience")


    for item in queue:
        if isinstance(item,praw.objects.Comment):
            continue
        fulltext = (item.title + item.selftext).lower()
        if_match = any(s in fulltext for s in wordlist)

        if if_match:
            if item.id in processed:
                continue
            
            processed.add(item.id)

            log.info( item.title)
            
            short = (fulltext[:60] + '..') if len(fulltext) > 60 else fulltext

            r.send_message('rantonels','modQ match: %s'%short,\
                    "A match to your wordlist was found for the following question:\n\n"+\
                    "**%s**\n\n"%item.title+\
                    "%s\n\n"%item.selftext+\
                    "[%s](%s)"%(item.short_link,item.short_link ))

    for i in range(60):
        log.debug("sleeping %d..."%i)
        time.sleep(1)
