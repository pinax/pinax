from django.test import TestCase
from oembed.core import replace

class OEmbedTests(TestCase):
    noembed = ur"This is text that should not match any regex."
    end = ur"There is this great video at %s"
    start = ur"%s is a video that I like."
    middle = ur"There is a movie here: %s and I really like it."
    trailing_comma = ur"This is great %s, but it might not work."
    trailing_period = ur"I like this video, located at %s."
    
    loc = u"http://www.viddler.com/explore/SYSTM/videos/49/"
    
    embed = u'<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" width="320" height="222" id="viddlerplayer-e5cb3aac"><param name="movie" value="http://www.viddler.com/player/e5cb3aac/" /><param name="allowScriptAccess" value="always" /><param name="allowFullScreen" value="true" /><embed src="http://www.viddler.com/player/e5cb3aac/" width="320" height="222" type="application/x-shockwave-flash" allowScriptAccess="always" allowFullScreen="true" name="viddlerplayer-e5cb3aac" ></embed></object>'

    def testNoEmbed(self):
        self.assertEquals(
            replace(self.noembed),
            self.noembed
        )
    
    def testEnd(self):
        for text in (self.end, self.start, self.middle, self.trailing_comma, self.trailing_period):
            self.assertEquals(
                replace(text % self.loc),
                text % self.embed
            )
    
    def testManySameEmbeds(self):
        text = " ".join([self.middle % self.loc] * 100) 
        resp = " ".join([self.middle % self.embed] * 100)
        self.assertEquals(replace(text), resp)