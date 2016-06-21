import praw
import logging
from logging.handlers import RotatingFileHandler
import sys
import time
import cPickle


# user class def

class User:
    wordlist = []


# database

class Database:
    ulist = {}
    processed = set([])

    def getUser(self,uname):
        if uname in self.ulist:
            return self.ulist[name]
        else:
            return None

    def getTotalWordlist(self):
        out = []
        for uname in self.ulist:
            u = self.ulist[uname]
            out += [ (w,uname) for w in u.wordlist]
        return out


try:
    donelist = cPickle.load(open("donelist",'r'))
except:
    logging.warning("donelist file not found, creating from scratch")
    donelist = set([])

try:
    donemessagelist = cPickle.load(open("donemsg",'r'))
except:
    logging.warning("donemsg file not found, creating from scratch")
    donemessagelist = []

try:
    db = cPickle.load(open('database','r'))
except:
    logging.warning("database file not found, creating empty")
    db = Database()

    rantonels = User()
    rantonels.wordlist = ['string','supersymmetry','holography','hologram','holographic','monopole','field','grand uni','great uni','quantum','entropy','planck','plank','renormalization','neutrino','blackhole','black hole','Hawking','spacetime','space-time','extra dimension','calabi','m theory','m-theory']

    sol = User()
    sol.wordlist = ["crocodile", "alligator", "dinosaur", "fossil", "paleontology", "paleontologist"]

    vl = User()
    vl.wordlist = [ "galax", "orbit", "neutron", "nuclear", "fart"]

    db.ulist["rantonels"] = rantonels
    #db.ulist["StringOfLights"] = sol
    #db.ulist["VeryLittle"] = vl





log = logging.getLogger('')
log.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
log.handlers[:] = [ch]



user_agent = "regexxit"

log.debug("starting to Reddit")
r = praw.Reddit(user_agent=user_agent)

username,password = (s.strip() for s in open('login','r').readlines())

log.info("login")
r.login(username,password,disable_warning=True)

r.send_message('rantonels','Hey daddy!','starting up!')



while True:

    log.info("getting PMs")
    pms = r.get_unread(limit=20)

    for m in pms:
        if m.subject == "MQ":
            log.info("got command...")
            m.mark_as_read()
            log.info("from %s"%m.author.name)
            words = m.body.lower().strip().split(' ')
            boddy_instr ="sending me a PM with subject \"MQ\" and body \"set word1 word2 word3 ... lastword\" (without the quotes!)"
            if (len(words) == 0) or (words[0] != "set"):
                indb = (m.author.name in db.ulist)

                if indb:
                    boddy = "your current wordlist is as follows:\n\n"+\
                            ",".join(db.ulist[m.author.name].wordlist)+"\n\n"\
                            "Cool, right? You can change it by "      + boddy_instr + \
                            "\n\nIf you want to disable it completely, just send me a PM with subject \"MQ\" and body \"set\"."
                else:
                    boddy = "You're not in the database :(.\n\n"+\
                            "If you want to start receiving notifications from the modqueue, register your wordlist by" + boddy_instr
                            
            else:
                words_list = words[1:]
                if not (m.author.name in db.ulist):
                    db.ulist[m.author.name] = User()

                db.ulist[m.author.name].wordlist = words_list

                boddy = "I have set your wordlist to the following:\n\n"+\
                        ", ".join(db.ulist[m.author.name].wordlist) + "\n\n" +\
                        "If this is not what you wanted, you can change it by "+boddy_instr

            r.send_message(m.author,"MQ","Hi %s!\n\n"%m.author.name+boddy)

    log.info("getting modqueue")
    queue = r.get_mod_queue(subreddit="askscience")

    log.debug("recomputing wordlist")

    wordlist = db.getTotalWordlist()


    for item in queue:

        if item.id in donelist:
                continue


        if isinstance(item,praw.objects.Comment):
            continue
        fulltext = (item.title + item.selftext).lower()
        #if_match = any(s[0] in fulltext for s in wordlist)

        if_match = set([])
        for w,u in wordlist:
            if w in fulltext:
                if_match.add(u)

        if len(if_match)>0:
            log.info("matched %d users"%len(if_match))

        for matched_user in if_match:
                        
            log.info( item.title)
            
            short = (fulltext[:60] + '..') if len(fulltext) > 60 else fulltext

            author = item.author.name

            r.send_message(matched_user,'modQ match: %s'%short,\
                    "A match to your wordlist was found for the following question:\n\n"+\
                    "**%s**\n\n"%item.title+\
                    "%s\n\n"%item.selftext+\
                    "*by* u/%s\n\n"%author+\
                    "[%s](%s)\n\n\n\n"%(item.short_link,item.short_link )+\
                    "(Please do not reply to me)"\
                    )

        if len(if_match)>0:
            donelist.add(item.id)

    log.info("dumping...")
    cPickle.dump(donelist, open("donelist",'w'))
    cPickle.dump(db, open('database','w'))


    for i in range(15):
        log.debug("sleeping %d..."%i)
        time.sleep(1)
