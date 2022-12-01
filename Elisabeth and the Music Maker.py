## Elisabeth and the Music Maker

## MUS 381 - Music History until 1800
## Capstone project - multimedia

## By Daniel Bergman and Robert Rattray

## This file contains both Python code, comments relevant to the understanding of
## the Python code, and comments relevant to the function of the game as it relates
## to the Baroque harpsichord practice of Elisabeth Jean-Claude Jacquet de la Guerre.
## For ease of reading, comments relating exclusively to the code are presented with
## a single # symbol, while comments relating to the function are marked with two ##
## symbols.  The # symbol flags everything after it in a line of text as a comment
## such that a Python interpreter does not read it; when using a text editor intended
## for coding (such as Visual Studio Code, Atom, or Notepad++), this usually causes
## the commented code to appear in green so it can be read independently from the 
## code by humans.

# This Python project makes use of the built-in math and os modules for file access
# and graphics, pygame (including the Sprite library) for its interface, and the
# midiutil library for the output of MIDI files.
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import math
import pygame
from pygame import sprite
pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(1.0)
import os
import random
from midiutil import MIDIFile

# The following lines determine the dimensions of various on-screen objects in pixels.
WINDOW_DIM = (1200,750) # Entire game window (width, height)
BUTTON_DIM = (60,80) # Buttons along the bottom of the screen
BUFFER = 10 # Buffer between buttons and the edges of the screen
BUTTON_RECT = pygame.Rect(0,WINDOW_DIM[1]-BUTTON_DIM[1]-2*BUFFER,WINDOW_DIM[0],BUTTON_DIM[1]+BUFFER*2)
CHAT_WIDTH = 300 # Area at right where Elisabeth speaks
CHAT_RECT = pygame.Rect(WINDOW_DIM[0]-CHAT_WIDTH,0,CHAT_WIDTH,BUTTON_RECT.top)
PAPER_RECT = pygame.Rect(0,0,CHAT_RECT.left,BUTTON_RECT.top)
SYSTEMS = 3 # The number of systems, or grand staves, of music in the window
STAVES_PER = 2 # The number of staves in each grand staff
MEASURES_PER = 4 # The number of measures each staff is across.
STAFF_HEIGHT = int(PAPER_RECT.height/(3*SYSTEMS*STAVES_PER+1))
# STAFF_HEIGHT is the distance between the highest and lowest non-ledger line in a staff
STAFF_LENGTH = PAPER_RECT.width - 4*STAFF_HEIGHT # The length of the paper of the staff with notes
SIGN_STAFF_LENGTH = 2*STAFF_HEIGHT # The part of the staff reserved for clef and time signature
PAGEDIM = (STAFF_LENGTH+SIGN_STAFF_LENGTH+STAFF_HEIGHT,WINDOW_DIM[1]-BUTTON_DIM[1]-2*BUFFER-STAFF_HEIGHT)
NOTE_LINE = 2 # Thickness of note features in pixels

# Colors and font
WINDOW_BACKGROUND = (240,240,240)
UNCLICKED_BUTTON = (200,200,200)
CLICKED_BUTTON = (180,180,180)
PAPER_COLOR = (230,230,200)
INK_COLOR = (40,20,20)
DEFAULT_FONT = pygame.font.SysFont('constantia',18)

# The following functions, linebreak and bliterate, were written by Robert Rattray for a 
# previous project, Wolf Adventure.

# The linebreak function yields a list of image-type objects rendering a line
# of the given text of the appropriate width.
def linebreak(text,width,maxheight=0,font=DEFAULT_FONT,color=INK_COLOR):
    # Begin by converting the text - likely read from a file with line breaks of its own -
    # into a simple long string with single line breaks for paragraphs, less whitespace.
    pars = text.split('\n\n')
    for i in range(len(pars)):
        par = pars[i]
        par = par.replace('\n',' ')
        while '  ' in par:
            par = par.replace('  ',' ')
        pars[i] = par
    text = ' \n '.join(pars)
    # Then look as the text as a series of words, with paragraph breaks considered words.
    words = text.split(' ') # This is NOT equivalent to text.split()
    lines = [] # Lines is a series of images with text rendered in a font.
    line = words[0] # Line is the next words to be rendered.
    if font.render(words[0],True,color).get_width() > width:
        return False         # Linebreak yields false if a word is too long for
    for word in words[1:]:   # the width or the whole exceeds a maximum height.
        if font.render(word,True,color).get_width() > width:
            return False
        linextend = ' '.join([line,word])
        if word == '\n': # At paragraph breaks, end the line without adding the 'word'.
            lines.append(font.render(line,True,color))
            line = ''
        elif font.render(linextend,True,color).get_width() > width:
            lines.append(font.render(line,True,color))
            line = word # When adding a word would go beyond the width, end the line and start anew.
        else:
            line = linextend
    lines.append(font.render(line,True,color))
    lineheight = lines[0].get_height()
    if maxheight > 0 and lineheight*len(lines) > maxheight:
        return False
    else:
        return lines

# Bliterate takes a text string, line-breaks it, and blits it.
# It yields the y-position ideal for blitting text beneath it,
# as well as the width of the text block.
def bliterate(screen,text,x,y,width,height=0,justify=False,outerbuffer=0,buffer=0,font=DEFAULT_FONT,color=INK_COLOR):
    lines = linebreak(text,width-2*outerbuffer,height-2*outerbuffer,font,color)
    widths = []
    if lines == False: # Display error for lines if word too wide or text too tall.
        screen.blit(font.render('Error',True,(255,0,0)),(x,y))
    else:
        runningheight = y + outerbuffer
        change = int(lines[0].get_height() + buffer / 2)
        for line in lines:
            if justify:
                screen.blit(line,(int(x+(width-line.get_width())/2),runningheight))
            else:
                screen.blit(line,(x+outerbuffer,runningheight))
            widths.append(line.get_width())
            runningheight += change
    return runningheight, max(widths)

# Code to retrieve image files easily.  May need to be changed if run on other device.
MAIN_DIR = os.path.dirname(os.getcwd())
def get_asset(assetname):
    return pygame.image.load(os.path.join(MAIN_DIR,'Elisabeth','Elisabeth_Assets',assetname))

# Graphics dictionaries are made by loading all of the files.
CLEF_DICT = {"treble":get_asset("treble.png"),"cclef":get_asset("cclef.png"),"bass":get_asset("bass.png")}
UPPER_CLEF_DICT = {"treble":get_asset("treble.png"),"cclef":get_asset("cclef.png")}
CLEF_NOTE_DICT = {'treble':38,'cclef':36,'bass':26}
TIME_DICT = {"common":get_asset("c.png"),"three":get_asset("three.png"),"six-four":get_asset("six_four.png"),
    "three-two":get_asset("three_two.png")}
TIME_TUPLE_DICT = {"common":(4,4),"three":(3,4),"six-four":(6,4),"three-two":(3,2)}
ACCI_DICT = {"sharp":get_asset("sharp.png"),"flat":get_asset("flat.png")}
NOTE_TIME_DICT = {"whole":1.0,"half":0.5,"quarter":0.25,"eighth":0.125,"sixteenth":0.0625}
NOTE_PICT_DICT = {"whole":get_asset("whole.png"),"half":get_asset("half.png"),"quarter":get_asset("quarter.png"),
    "eighth":get_asset("eighth.png"),"sixteenth":get_asset("sixteenth.png")}
ERASER_DICT = {"eraser":get_asset("Knife.png")}
INVERTER_DICT = {"inverse":get_asset("inverse.png")}
DOT_DICT = {"dot":get_asset("1,5.png")}
AGREMENT_DICT = {"pince":get_asset("pince.png"),"tremblement":get_asset("tremblement.png"),
    "appuye":get_asset("tremblement_appuye.png"),
    "portdevoix":get_asset("portdevoix.png"),"double":get_asset("double.png"),
    "cadence":get_asset("cadence.png"),"mordent":get_asset("mordent.png")}
AGREMENT_DONE_DICT = {}
for K in AGREMENT_DICT:
    AGREMENT_DONE_DICT[K] = False
PLAY_DICT = {"play":pygame.transform.scale(get_asset("play.png"),(CHAT_WIDTH,BUTTON_DIM[1]))}
lispic = get_asset("Elisabeth.jpg")
LIS_HEIGHT = int(CHAT_WIDTH*lispic.get_height()/lispic.get_width())
lispic = pygame.transform.scale(lispic,(CHAT_WIDTH,LIS_HEIGHT))
CHAT_RECT.top = LIS_HEIGHT
CHAT_RECT.height -= LIS_HEIGHT

# Classes
#
################################################################
#
# A class for the button objects, seen at the bottom of the screen.
class pybutton(pygame.sprite.Sprite): # Inherits from Sprite b/c has appearance
    def __init__(self,statusdict,position,explanation='',*groups):
        super().__init__(*groups)
        for eachkey in statusdict:
            statusdict[eachkey] = pygame.transform.scale(statusdict[eachkey],BUTTON_DIM)
        self.statusdict = statusdict
        self.statuslist = list(statusdict)
        self.status = 0
        self.selected = False
        self.selectable = False
        self.position = position
        self.rect = pygame.Rect(position[0],position[1],BUTTON_DIM[0],BUTTON_DIM[1])
        self.image = pygame.Surface(BUTTON_DIM)
        self.image.fill(UNCLICKED_BUTTON)
        self.image.blit(self.statusdict[self.statuslist[self.status]],(0,0))
        self.explanation = explanation
    
    def feel_click(self):
        if self.selectable and not self.selected:
            self.selected = True
            self.image.fill(CLICKED_BUTTON)
            self.image.blit(self.statusdict[self.statuslist[self.status]],(0,0))
        elif self.selectable:
            if self.status == len(self.statuslist) - 1:
                self.status = 0
            else:
                self.status += 1
            self.image.fill(CLICKED_BUTTON)
            self.image.blit(self.statusdict[self.statuslist[self.status]],(0,0))
    
    def unselect(self):
        self.selected = False
        self.image.fill(UNCLICKED_BUTTON)
        self.image.blit(self.statusdict[self.statuslist[self.status]],(0,0))
    
    def grey(self):
        self.selectable = False 
        self.unselect()
        for y in range(0,self.image.get_height()-2,2):
            pygame.draw.line(self.image,UNCLICKED_BUTTON,(0,y),(self.image.get_width(),y))

################################################################################
## This research project was started because of unfamiliarity with the notation
## used by Elisabeth Jean-Claude Jacquet de la Guerre in her Suite in A Minor,
## so the appearance of notes in the game is based on her manuscript, specifically:
##
## Jacquet de la Guerre, Elisabeth.  Pièces de clavecín, livre 1 (Paris:  de Baussen, 1687).
##
## accessed through the Petrucci Music Library.  Another main topic of discussion in this 
## project is the difference in technological methods of composition between now and when 
## the piece was composed.  The creation of a modern computer program to compose this piece 
## is contrasted with the simple, yet nuanced method of manually writing a piece on 
## parchment, which de la Guerre used in her time. Expectedly, the human element of a 
## composition can not be perfectly represented through recreation with a computer 
## program, so ambiguously interpretable aspects of the piece are lost in translation.
##
## The Prelude presents the most challenging notation to imitate, with its own unique 
## expectations for improvisation.  Such style is considered too complicated for this 
## program, however, and the appearance of normal-ish notes and familiar bar lines makes 
## up this game.  Details for note appearance atypical of today's music are 
## marked with ## comments throughout the Note class.
#################################################################################

class Note():
    def __init__(self,staff,time,duration,pitch,accidental='',agrement='',orientation=True):
        self.staff = staff # The staff in which the note appears (a Staff object)
        self.time = time # The position in time in which this note is played, as a tuple of measure and beat.
        self.duration = duration # The duration for which this note is played; e.g., 0.75 for dotted half note.
        self.pitch = pitch # The pitch of this note without accidental, e.g., 'c4' for C-sharp above middle C
        self.accidental = accidental # Either 'sharp,' '' or 'flat.'
        ###########################################################################################
        ## As seen in the third measure of the first "Allemande," and throughout the suite,
        ## accidentals do not carry from note to note, even within the same octave and measure
        ## (or else de la Guerre is including unusually many courtesy accidentals).
        ###########################################################################################
        # As such, the variable self.accidental determines whether an accidental appears and is used to
        # find the pitch for the MIDI output all the same.
        self.agrement = agrement # Any agrement the note carries.
        self.orientation = orientation # True if, for a quarter note, shaped like a d, False if like a p.
        ##################################################################################################
        ## Also seen throughout the piece are inverted notes with their stems proceeding from their middle,
        ## not the left side.  This change of appearance is reflect in the game.  And though today it is
        ## conventional for notes' orientations to be determined by where they appear in relation to the
        ## central line of a staff, in Jacquet de la Guerre's pieces it is more often a function of its
        ## voicing (still typical of choral music today), so this orientation is determined by the player.
        ##################################################################################################
    
    def __str__(self): # This method isn't working but it isn't ever called either.
        return f"Note {self.pitch} at {self.time} in Staff #{self.staff.id}."
    
    def set_position(self):
        ##################################################################################################
        ## In de la Guerre's Prelude, the evidence for what appear to be whole notes not being played as
        ## such is that they are not spaced as far apart as quarter notes would be; they are intended to
        ## be played as arpeggiated chords, according to:
        ##
        ## Burkholder, J. Peter and Claude V. Palisca.  “85:  Elisabeth Jean-Claude Jacquet de la Guerre, 
        ## Suite No. 3 in A Minor.”  In Norton Anthology of Western music, Sixth Edition, Volume One: 
        ## Ancient to Baroque, 584-98.  New York:  W. W. Norton & Company, 2010.
        ##
        ## Though of course not every whole note need be as far from its neighbor as sixteen sixteenth notes
        ## put together would be, de la Guerre was at least familiar with the intuitive idea that longer
        ## notes should have more space after them.  As such, it is not unreasonable that this game assume
        ## note be placed in time based on where the player clicks relative to the measure bars, as opposed
        ## to, say, having notes be placed in the order the player clicks them.
        #################################################################################################
        # For the sake of simplicity, notes appear in precise locations based on beat.
        distalong = int((self.time[0]-1+(self.time[1]-1)*self.staff.timesig[1]/(4*self.staff.timesig[0]))*STAFF_LENGTH/MEASURES_PER)
        toprung = CLEF_NOTE_DICT[self.staff.clef]
        self.rung = {'c':0,'d':1,'e':2,'f':3,'g':4,'a':5,'b':6}[self.pitch[0]] + 7*int(self.pitch[1])
        self.stepsdown = toprung - self.rung
        headdown = int(self.stepsdown*STAFF_HEIGHT/8)
        distdown = headdown - int(3*STAFF_HEIGHT/8)
        if self.orientation:
            distdown = headdown - int(9*STAFF_HEIGHT/8)
        self.position = ( int(self.staff.position[0]+STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+distalong), int(self.staff.position[1]+STAFF_HEIGHT+distdown) )
        centerx = int(STAFF_LENGTH/(32*MEASURES_PER)) + self.position[0]
        if self.orientation:
            self.tip_position = (int(centerx+STAFF_HEIGHT/8-NOTE_LINE),int(STAFF_HEIGHT/4+self.position[1]))
        else:
            self.tip_position = (int(centerx-STAFF_HEIGHT/8+NOTE_LINE),self.position[1]+self.rect.height)
        self.rect = pygame.Rect(self.position[0],self.position[1],int(self.duration*STAFF_LENGTH*self.staff.timesig[1]/(MEASURES_PER*self.staff.timesig[0])),int(1.25*STAFF_HEIGHT))
    
    # This method convert the printed pitch (like 'b4' with a sharp or 'c5') to a MIDI pitch (like '72').
    def midi_pitch(self):
        midi_pitch = {'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11}[self.pitch[0]] + 12*int(self.pitch[1]) + 12
        if self.accidental == 'sharp':
            midi_pitch += 1
        elif self.accidental == 'flat':
            midi_pitch -= 1
        return midi_pitch

    # This method returns the duration of the note in MIDI, which is in beats.
    def midi_duration(self):
        return self.duration*self.staff.timesig[1]

    # This method draws the note onto the screen.
    def generate_image(self):
        # Draw notehead to surface
        centerx = int(STAFF_LENGTH/(32*MEASURES_PER)) + self.position[0]
        headpos = (centerx,int(3*STAFF_HEIGHT/8) + self.position[1])
        if self.orientation:
            headpos = (centerx,int(9*STAFF_HEIGHT/8) + self.position[1])
        if self.duration >= 0.5:
            pygame.draw.circle(self.staff.screen,INK_COLOR,headpos,int(STAFF_HEIGHT/8),NOTE_LINE)
        else:
            pygame.draw.circle(self.staff.screen,INK_COLOR,headpos,int(STAFF_HEIGHT/8))
        # Draw note stem to surface
        if self.duration < 1:
            if self.orientation:
                pygame.draw.line(self.staff.screen,INK_COLOR,(int(centerx+STAFF_HEIGHT/8-NOTE_LINE),headpos[1]),self.tip_position,NOTE_LINE)
            else:
                pygame.draw.line(self.staff.screen,INK_COLOR,(int(centerx-STAFF_HEIGHT/8+NOTE_LINE),headpos[1]),self.tip_position,NOTE_LINE)
        # Draw dot (if it exists)
        if self.duration * 32 % 3 == 0:
            pygame.draw.circle(self.staff.screen,INK_COLOR,(headpos[0]+int(STAFF_HEIGHT/4),headpos[1]),NOTE_LINE)
        # Draw accidental (if it is marked)
        if self.accidental != '':
            mark = pygame.transform.scale(ACCI_DICT[self.accidental],(int(STAFF_HEIGHT/4),int(STAFF_HEIGHT/3)))
            self.staff.screen.blit(mark,(int(headpos[0]-STAFF_HEIGHT/4),int(headpos[1]-STAFF_HEIGHT/3)))
        # Draw agrement (if it exists)
        if self.agrement != '':
            mark = pygame.transform.scale(AGREMENT_DICT[self.agrement],(int(STAFF_HEIGHT/3),int(STAFF_HEIGHT/3)))
            self.staff.screen.blit(mark,(int(centerx-STAFF_HEIGHT/6),int(self.position[1]-STAFF_HEIGHT/3)))
        # Draw ledger lines (if necessary)
        if self.rung > CLEF_NOTE_DICT[self.staff.clef]:
            for l in range((self.rung - CLEF_NOTE_DICT[self.staff.clef]) // 2):
                y = int(self.staff.position[1]+STAFF_HEIGHT-(l+1)*STAFF_HEIGHT/4)
                pygame.draw.line(self.staff.screen,INK_COLOR,(int(centerx-STAFF_HEIGHT/6),y),(int(centerx+STAFF_HEIGHT/6),y))
        elif self.rung < CLEF_NOTE_DICT[self.staff.clef] - 8:
            for l in range((CLEF_NOTE_DICT[self.staff.clef] - 8 - self.rung) // 2):
                y = int(self.staff.position[1]+2*STAFF_HEIGHT+(l+1)*STAFF_HEIGHT/4)
                pygame.draw.line(self.staff.screen,INK_COLOR,(int(centerx-STAFF_HEIGHT/6),y),(int(centerx+STAFF_HEIGHT/6),y))

    # This method draws an eighth note or sixteenth note's flag/tail.
    def flag(self):
        if self.duration < 0.25:
            if self.orientation:
                pygame.draw.line(self.staff.screen,INK_COLOR,self.tip_position,(self.tip_position[0]+2*NOTE_LINE,self.tip_position[1]+4*NOTE_LINE),NOTE_LINE)
                pygame.draw.arc(self.staff.screen,INK_COLOR,[self.tip_position[0]-int(NOTE_LINE*6.4),self.tip_position[1]+2*NOTE_LINE,int(NOTE_LINE*9.2),int(8*NOTE_LINE)],-math.atan(1/2),math.atan(1/2)+0.1,NOTE_LINE)
            else:
                pygame.draw.line(self.staff.screen,INK_COLOR,self.tip_position,(self.tip_position[0]+2*NOTE_LINE,self.tip_position[1]-4*NOTE_LINE),NOTE_LINE)
                pygame.draw.arc(self.staff.screen,INK_COLOR,[self.tip_position[0]-int(NOTE_LINE*6),self.tip_position[1]-10*NOTE_LINE,int(NOTE_LINE*9.2),int(8*NOTE_LINE)],-math.atan(1/2)-0.1,math.atan(1/2),NOTE_LINE)
            if self.duration < 0.125:
                if self.orientation:
                    pygame.draw.line(self.staff.screen,INK_COLOR,(self.tip_position[0],self.tip_position[1]+4*NOTE_LINE),(self.tip_position[0]+2*NOTE_LINE,self.tip_position[1]+8*NOTE_LINE),NOTE_LINE)
                    pygame.draw.arc(self.staff.screen,INK_COLOR,[self.tip_position[0]-int(NOTE_LINE*6.4),self.tip_position[1]+6*NOTE_LINE,int(NOTE_LINE*9.2),int(8*NOTE_LINE)],-math.atan(1/2),math.atan(1/2)+0.1,NOTE_LINE)
                else:
                    pygame.draw.line(self.staff.screen,INK_COLOR,(self.tip_position[0],self.tip_position[1]-4*NOTE_LINE),(self.tip_position[0]+2*NOTE_LINE,self.tip_position[1]-8*NOTE_LINE),NOTE_LINE)
                    pygame.draw.arc(self.staff.screen,INK_COLOR,[self.tip_position[0]-int(NOTE_LINE*6),self.tip_position[1]-14*NOTE_LINE,int(NOTE_LINE*9.2),int(8*NOTE_LINE)],-math.atan(1/2)-0.1,math.atan(1/2),NOTE_LINE)
    
    # This method runs when a note (or the invisible box around it) is clicked on.
    # Note that the box pertains more to the portion of the measure in which the note is played and where the stem is;
    # agrements, accidentals, and dots can all be printed outside this box.
    def feel_click(self,selected_function):
        # Clicking with the accidental function will cause that accidental to appear.
        if selected_function in ACCI_DICT:
            self.accidental = selected_function
            self.generate_image()
        # Clicking with the inverse function will invert the note (d to q and vice versa).
        elif selected_function == "inverse":
            if self.orientation:
                self.orientation = False 
            else:
                self.orientation = True 
            self.set_position()
        # Clicking on the note with the eraser will get rid of an agrement, then a dot, then an accidental, then the note itself.
        elif selected_function == "eraser":
            if self.agrement != '':
                self.agrement = ''
            elif self.duration * 32 % 3 == 0:
                self.duration *= 2/3
                self.rect.width = int(self.rect.width*2/3)
                self.generate_image()
            elif self.accidental != '':
                self.accidental = ''
            else:
                self.staff.notes.remove(self)
        # The dot function will add or remove a dot.
        elif selected_function == "dot":
            if self.duration * 32 % 3 != 0:
                self.duration *= 1.5
                self.rect.width = int(self.rect.width*1.5)
                self.generate_image()
            else:
                self.duration *= 2/3
                self.rect.width = int(self.rect.width*2/3)
                self.generate_image()
        # Agrement function causes agrement marks to appear.
        elif selected_function in AGREMENT_DICT:
            AGREMENT_DONE_DICT[selected_function] = True
            self.agrement = selected_function
            if selected_function in ['cadence','appuye'] and self.duration * 32 % 3 != 0:
                self.duration *= 1.5
                self.rect.width = int(self.rect.width*1.5)
            elif selected_function == 'tremblement' and self.duration * 32 % 3 == 0:
                self.duration *= 2/3
                self.rect.width = int(self.rect.width*2/3)
            self.generate_image()

# This class - staff - includes a list of the Note objects that are the notes appearing on it,
# as well as the clef, time signature, and other features.  All notes can refer to their Staff
# object via the self.staff attribute.  This sort of circular reference is discouraged by
# theoretical programmers because of the inherent dangers, but they aren't here.
# Neither the programmers, nor the dangers.
class Staff():
    def __init__(self,screen,position,id,clef='cclef',timename="common"):
        self.screen = screen
        self.position = position # Absolute position on the screen.  Tuple.
        self.clef = clef # Clef at the front, as a string.
        self.timename = timename # Time signature, as a string, e.g. "common"
        self.timesig = TIME_TUPLE_DICT[timename] # Time signature, as a tuple, e.g. (4,4)
        self.notes = []
        self.id = id
        self.rect = pygame.Rect(self.position[0],self.position[1],STAFF_LENGTH+SIGN_STAFF_LENGTH+STAFF_HEIGHT,3*STAFF_HEIGHT)

    # The process by which a staff renders itself, based on the notation in Elisabeth Jean-Claude Jacquet de la Guerre's
    # own score for her Suite in A Minor, is described below.
    def generate_image(self):
        # Erase the rest of what's in the staff's area
        pygame.draw.rect(self.screen,PAPER_COLOR,self.rect)
        # Draw five horizontal lines and vertical lines in between measures.
        for l in range(5):
            y = int(l*STAFF_HEIGHT/4+self.position[1]+STAFF_HEIGHT)
            pygame.draw.line(self.screen,INK_COLOR,(int(STAFF_HEIGHT/2+self.position[0]),y),(int(STAFF_LENGTH+SIGN_STAFF_LENGTH+STAFF_HEIGHT/2)+self.position[0],y))
        for m in range(MEASURES_PER):
            pygame.draw.line(self.screen,INK_COLOR,(int(STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+m*STAFF_LENGTH/MEASURES_PER+self.position[0]),STAFF_HEIGHT+self.position[1]),(int(STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+m*STAFF_LENGTH/MEASURES_PER+self.position[0]),2*STAFF_HEIGHT+self.position[1]))
        # Draw the clef at the front of each staff.  The C-clef can reach half the staff height below the staff.
        self.screen.blit(pygame.transform.scale(CLEF_DICT[self.clef],(STAFF_HEIGHT,int(1.5*STAFF_HEIGHT))),(int(STAFF_HEIGHT/2+self.position[0]),STAFF_HEIGHT+self.position[1]))
        # Draw the time signature immediately following the clef.
        self.screen.blit(pygame.transform.scale(TIME_DICT[self.timename],(STAFF_HEIGHT,STAFF_HEIGHT)),(int(3*STAFF_HEIGHT/2+self.position[0]),STAFF_HEIGHT+self.position[1]))
        # Draw the notes, or at least, their heads, stems, and special marks, as these can be done independently.
        for eachnote in self.notes:
            eachnote.generate_image()
        # Connect stems of eighth notes, sixteeth notes in same beat
        ######################################################################################################
        ## One thing of interest in de la Guerre's original manuscript, not present in the newer copies, is the
        ## way she beams notes.  If a sixteenth note follows a dotted eighth note, sharing a beat, as occurs
        ## in the second measure of the Allemande and throughout, they are beamed together, but while today one
        ## would usually indicate the latter note being a mere sixteeth by a tick towards the eighth, (as in
        ##
        ## Jacquet de la Guerre, Elisabeth.  “Troisème suite” in Pièces de clavecin, livre 1, ed. Pierre Gouin
        ## (Montréal:  Les Éditions Outremontaises, 2022), 26-39.
        ##
        ## a more recent edition of the same), in her original manuscript the sixteenth note points its tails
        ## rightward.  Also of note is that her beams are not always straight as modern ones, especially when
        ## notes on a beat are not purely in ascent or descent; they may curve and stems stick across the beam.
        ## There is no clear pattern to these curves, however; they are not always a translation of the curved
        ## line that would pass through the noteheads, for example, so for this program beams remain straight.
        ########################################################################################################
        # This sub-method beams the set of notes on one beat in one staff.
        def beam(noteset):
            # Look at the d-notes and p-notes separately.  If there is only one, it should flag itself.
            if len(noteset) == 1:
                noteset[0].flag()
               # Otherwise, assume any pattern of eighths and sixteenths.
            elif len(noteset) > 1 and noteset[-1].tip_position[0] != noteset[0].tip_position[0]:
                # Apply one line across all the tops of all the notes.
                # Find the slope of this line and adjust tip positions to fit.
                pygame.draw.line(self.screen,INK_COLOR,noteset[0].tip_position,noteset[-1].tip_position,2*NOTE_LINE)
                slope = (noteset[-1].tip_position[1]-noteset[0].tip_position[1]) / (noteset[-1].tip_position[0]-noteset[0].tip_position[0])
                for everypair in range(len(noteset)-1):
                    left_note, right_note = noteset[everypair], noteset[everypair+1]
                    right_note.tip_position = (right_note.tip_position[0],int(noteset[0].tip_position[1]+slope*(right_note.tip_position[0]-noteset[0].tip_position[0])))
                    if left_note.duration < 0.125:
                        if right_note.duration < 0.125:
                            if left_note.orientation:
                                pygame.draw.line(self.screen,INK_COLOR,(left_note.tip_position[0],left_note.tip_position[1]+4*NOTE_LINE),(right_note.tip_position[0],right_note.tip_position[1]+4*NOTE_LINE),2*NOTE_LINE)
                            else:
                                pygame.draw.line(self.screen,INK_COLOR,(left_note.tip_position[0],left_note.tip_position[1]-4*NOTE_LINE),(right_note.tip_position[0],right_note.tip_position[1]-4*NOTE_LINE),2*NOTE_LINE)
                        else:
                            xchange = (right_note.tip_position[0] - left_note.tip_position[0]) // 2
                            if left_note.orientation:
                                pygame.draw.line(self.screen,INK_COLOR,(left_note.tip_position[0],left_note.tip_position[1]+4*NOTE_LINE),(left_note.tip_position[0]+xchange,int(left_note.tip_position[1]+slope*xchange+4*NOTE_LINE)),2*NOTE_LINE)
                            else:
                                pygame.draw.line(self.screen,INK_COLOR,(left_note.tip_position[0],left_note.tip_position[1]-4*NOTE_LINE),(left_note.tip_position[0]+xchange,int(left_note.tip_position[1]+slope*xchange-4*NOTE_LINE)),2*NOTE_LINE)
                    elif right_note.duration < 0.125 and everypair == len(noteset) - 2:
                        xchange = (right_note.tip_position[0] - left_note.tip_position[0]) // 3
                        if right_note.orientation:
                            pygame.draw.line(self.screen,INK_COLOR,(right_note.tip_position[0],right_note.tip_position[1]+4*NOTE_LINE),(right_note.tip_position[0]+xchange//2,int(right_note.tip_position[1]+slope*xchange/2+4*NOTE_LINE)),2*NOTE_LINE)
                            pygame.draw.line(self.screen,INK_COLOR,(right_note.tip_position[0],right_note.tip_position[1]),(right_note.tip_position[0]+xchange//2,int(right_note.tip_position[1]+slope*xchange/2)),2*NOTE_LINE)
                        else:
                            pygame.draw.line(self.screen,INK_COLOR,(right_note.tip_position[0],right_note.tip_position[1]-4*NOTE_LINE),(right_note.tip_position[0]+xchange//2,int(right_note.tip_position[1]+slope*xchange/2-4*NOTE_LINE)),2*NOTE_LINE)
                            pygame.draw.line(self.screen,INK_COLOR,(right_note.tip_position[0],right_note.tip_position[1]),(right_note.tip_position[0]+xchange//2,int(right_note.tip_position[1]+slope*xchange/2)),2*NOTE_LINE)
                        
        # Iterate through notes.
        beat = 0
        shared_upper_notes = []
        shared_lower_notes = []
        itsbeat = 0
        for eachnote in range(len(self.notes)):
            # Go through notes, beat by beat, ignoring all quarter notes and above.
            if self.notes[eachnote].duration < 0.25:
                itsbeat = self.time_a_note(self.notes[eachnote]) // 1
                if itsbeat > beat:
                    # This means we have reached a new beat.  First stem the old:
                    for noteset in [shared_lower_notes,shared_upper_notes]:
                        beam(noteset)
                    # Then start the new.
                    beat = itsbeat
                    shared_upper_notes = []
                    shared_lower_notes = []
                if self.notes[eachnote].orientation:
                    shared_upper_notes.append(self.notes[eachnote])
                else:
                    shared_lower_notes.append(self.notes[eachnote])
        for noteset in [shared_lower_notes,shared_upper_notes]:
            beam(noteset)

    # This method is called to set the clef on a staff.
    def change_clef(self,clef):
        self.clef = clef
        self.generate_image()
    
    # This method is called to set the time signature on a staff.
    def change_time(self,time):
        self.timename = time 
        self.timesig = TIME_TUPLE_DICT[time]
        self.generate_image()
    
    # This note determines on what beat in a staff a note appears,
    # e.g., an eighth note at the end of the second measure of 3/4 time
    # is at beat 6.5
    def time_a_note(self,note):
        return note.time[0]*self.timesig[0] + note.time[1]

    # This method is how a staff responds to being clicked, in the loop
    # after clef and time signature have been set.
    def feel_click(self,mousepos,selected_function):
        # Where in the staff's rectangle it was clicked.
        relpos = (mousepos[0]-self.position[0],mousepos[1]-self.position[1])
        if relpos[0] > 2.5*STAFF_HEIGHT: # Only matters if clicked in music part.
            # If a note is clicked on, it gets priority.
            for eachnote in self.notes:
                if eachnote.rect.collidepoint(mousepos):
                    eachnote.feel_click(selected_function)
                    self.generate_image()
                    return False # Only one note responds to click.
            if selected_function in NOTE_TIME_DICT:
                # Algorithm for when a staff is clicked on with the note placement tool.
                # First, find the time of the note.
                duration = NOTE_TIME_DICT[selected_function]
                distalong = relpos[0] - 2.5*STAFF_HEIGHT
                measure = 1 + distalong // (STAFF_LENGTH/MEASURES_PER)
                beatinown = 1 + (distalong - (measure-1)*STAFF_LENGTH/MEASURES_PER) // (duration*STAFF_LENGTH*self.timesig[1]/(MEASURES_PER*self.timesig[0]))
                # For example, the fifth consecutive eighth note in a measure has a 'beatinown' of 5.
                # Notes can only appear in such a portion in their measure, for example, a half
                # note does not start right after a dotted quarter note.
                while duration*beatinown > self.timesig[0]/self.timesig[1]:
                    duration *= 0.5 # Note size adjusted to fit certain notes.
                    beatinown = 1 + 2*(beatinown-1)
                time = (measure,(beatinown-1)*4*duration+1)
                # Second, the pitch of the note.
                stepsdown = (relpos[1] - 15*STAFF_HEIGHT/16) // (STAFF_HEIGHT/8)
                toprung = CLEF_NOTE_DICT[self.clef]
                notename = {0:'c',1:'d',2:'e',3:'f',4:'g',5:'a',6:'b'}[(toprung-stepsdown) % 7]
                noteoctave = (toprung-stepsdown) // 7
                newnote = Note(self,time,duration,notename+str(noteoctave))
                newnote.set_position()
                self.notes.append(newnote)
                self.notes.sort(key=self.time_a_note)
                self.generate_image()

# The 'main' function, the part of the program that runs.
def main():
    # Initialize display window
    screen = pygame.display.set_mode(pygame.Rect((0,0,WINDOW_DIM[0],WINDOW_DIM[1])).size)
    screen.fill(WINDOW_BACKGROUND)
    pygame.display.set_caption("Elisabeth and the Music Maker")

    # Set up buttons
    buttons = pygame.sprite.Group()
    clefbutton = pybutton(UPPER_CLEF_DICT,(BUFFER,BUTTON_RECT.top+BUFFER))
    timebutton = pybutton(TIME_DICT,(2*BUFFER+BUTTON_DIM[0],BUTTON_RECT.top+BUFFER))
    ######################################################################################
    ## Many of the differences observed between de la Guerre's notation and today's,
    ## can be observed in the game by both the player and by de la Guerre herself,
    ## who comments with one when the player asks her for help.  Her comments, however,
    ## are made from the opposite perspective; it is contemporary notation which is
    ## less familiar to her.
    ######################################################################################
    pybutton(ACCI_DICT,(3*BUFFER+2*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    If you wish to raise or lower a note by a half step, select the button with a sharp/flat in the “toolbox”, 
    if that is what you call it.''',buttons)
    pybutton(NOTE_PICT_DICT,(4*BUFFER+3*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    Something something note durations''',buttons)
    pybutton(INVERTER_DICT,(5*BUFFER+4*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    Here is a place to go when you wish to flip the tail of your note. While I always make my notes 
    shaped like ‘d’ and ‘q’,
    it has become apparent to moi that the ‘q’ is now a ‘p’. Tres bizarre.''',buttons)
    pybutton(ERASER_DICT,(6*BUFFER+5*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    This is a, how you say, erase button? It looks like a penknife because, back in my day,
    if we made a wrong mark, we had to scratch the ink off with a knife—
    much harder than your fancy typewriters and correction tape nowadays. Be careful not to scratch the parchment!''',buttons)
    pybutton(DOT_DICT,(7*BUFFER+6*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    To extend a note by half its length, use this funny-looking dot.''',buttons)
    pybutton(AGREMENT_DICT,(8*BUFFER+7*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    Les agréments are most important if you wish to give more feeling to the piece. 
    Please, for my sake, give your musique some more flavor by pressing this button
    and clicking on your notes.''',buttons)
    playbutton = pybutton(PLAY_DICT,(WINDOW_DIM[0]-CHAT_WIDTH-BUFFER,BUTTON_RECT.top+BUFFER),'''
    Something about the harpischord for the play button.''')
    # Play button needs extra work to make it bigger.
    playbutton.rect.width = CHAT_WIDTH-2*BUFFER
    playbutton.rect.left = CHAT_RECT.left + BUFFER
    playbutton.image = pygame.Surface((CHAT_WIDTH-2*BUFFER,BUTTON_DIM[1]))
    playbutton.image.fill(UNCLICKED_BUTTON)
    playbutton.image.blit(PLAY_DICT['play'],(int(playbutton.rect.width/2-PLAY_DICT['play'].get_width()/2),0))
    screen.blit(clefbutton.image,clefbutton.rect)
    screen.blit(timebutton.image,timebutton.rect)
    screen.blit(playbutton.image,playbutton.rect)
    buttons.draw(screen)

    # Draw Elisabeth
    screen.blit(lispic,(CHAT_RECT.left,0))
    # The parle() method places text (a long string in the 'mots' argument) under the portrait.
    def parle(screen,mots):
        pygame.draw.rect(screen,PAPER_COLOR,CHAT_RECT)
        bliterate(screen,mots,CHAT_RECT.left,LIS_HEIGHT,CHAT_WIDTH,outerbuffer=10,buffer=5)
        pygame.display.update()
    # The wait_press() waits for the player to click on something or press a key;
    # if the player clicks on the 'x' button; it returns -1.  The syntax:
    # if wait_press() == -1:
    #   return
    # will allow the game to proceed as one expects, with the 'x' button working
    # and the game waiting for the player's move.
    def wait_press():
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return -1
                elif e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN:
                    return 0
    
    # Draw staff paper
    pygame.draw.rect(screen,PAPER_COLOR,PAPER_RECT)
    staves = []
    for s in range(SYSTEMS*STAVES_PER):
        staves.append(Staff(screen,(int(STAFF_HEIGHT/2),int((6*s+0.5)*STAFF_HEIGHT/2)),s))
    for eachstaff in range(len(staves)):
        if eachstaff % STAVES_PER != 0:
            staves[eachstaff].change_clef("bass")
        staves[eachstaff].generate_image()
    #staves.draw(screen)
    
    pygame.display.update()

    selected_function = 'select'

    # The redraw_staff_paper() blanks the staff area and redraws every staff and note.
    # Useful for when some part of a note is not erased because it strayed outside its staff.
    def redraw_staff_paper():
        pygame.draw.rect(screen,PAPER_COLOR,(int(STAFF_HEIGHT/2),int(STAFF_HEIGHT/2),PAGEDIM[0],PAGEDIM[1]))
        for eachstaff in staves:
            eachstaff.generate_image()
    
    # This code takes the notes on-screen and makes a MIDI piece of them.
    # It also gauges whether the player uses agréments, and returns that Boolean.
    ################################################################################
    ## In producing the game's MIDI output, it was necessary to make assumptions
    ## about dynamics and tempo, which are not indicated in either edition of de la Guerre's
    ## scores.  About dynamics, it is stated in
    ##
    ## Moersch, Charlotte Mattax.  “Keyboard Improvisation in the Baroque Period.”
    ## In Musical Improvisation:  Art, Education, and Society edited by Solis, Gabriel
    ## and Bruno Nettl, 150-170.  Chicago:  University of Illinois, 2009.
    ##
    ## that the harpsichord did not have dynamics (this is the namesake of the pianoforte,
    ## invented in 1720, nine years before de la Guerre's death); as such, every note is
    ## given the maximum volume.  Regarding tempo,
    ###################################################################################
    # TODO see if any sources describe tempo and if not try to figure it from a recording
    ##################################################################################
    ## The most interesting - and most difficult to interpret - feature of de la Guerre's works
    ## is the agréments.  Though de la Guerre did not publish a guide to interpreting them,
    ## other composers, such as d'Anglebert and Couperin, published conflicting guides
    ## at different times.
    ###################################################################################
    # TODO make dictionary of agréments.
    def output_music():
        agrements = False
        BEATS_PER_STAFF = staves[0].timesig[0]*MEASURES_PER
        outputMIDI = MIDIFile(1) # A one-track MIDI file
        outputMIDI.addTempo(0,0,120) # The arguments here are track, time in beats when track begins, and tempo.
        outputMIDI.addProgramChange(0,0,0,6) # Changes instrument to harpsichord (first three args are track, channel, time)
        # Note that a harpsichord is 7 is standard MIDI's 1-origin list, but 6 in the library's 0-origin list.
        # These allow for agrements on multiple notes.
        previousnote = ''
        previoushaddouble = False
        for eachstaff in staves:
            for eachnote in eachstaff.notes:
                ###############################################################################
                ## The way the game interprets agrements is determined from numerous sources.
                ## Most pertinent to Jacquet's own work are the pince (simple trill), tremblement (long trill),
                ## double, and port de voix, which are defined from Norton.
                ##
                ## d'Anglebert being her closest relation, his table is used to define cadence
                ## and the tremblement appuye.  Mordent also appears in his table, Hashimoto gives
                ## tips for defining.  He also says about trills... choose what I do about trills.
                ###############################################################################
                if previoushaddouble and previousnote != '':
                    outputMIDI.addNote(0,0,eachnote.midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(previousnote[1]),previousnote[1].midi_duration()/4,100)
                    outputMIDI.addNote(0,0,previousnote[1].midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(previousnote[1])+previousnote[1].midi_duration()/4,previousnote[1].midi_duration()/4,100)
                    outputMIDI.addNote(0,0,previousnote[0].midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(previousnote[1])+previousnote[1].midi_duration()/2,previousnote[1].midi_duration()/4,100)
                    outputMIDI.addNote(0,0,previousnote[1].midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(previousnote[1])+3*previousnote[1].midi_duration()/4,previousnote[1].midi_duration()/4,100)
                    previoushaddouble = False
                # No agrement - normal note!
                if eachnote.agrement == '': # The arguments are track, channel (as in both, left, or right), pitch, time, duration, and volume
                    outputMIDI.addNote(0,0,eachnote.midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote),eachnote.midi_duration(),100)
                else:
                    agrements = True # Add code for agréments here!
                    if eachnote.agrement == 'pince':
                        outputMIDI.addNote(0,0,eachnote.midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote),eachnote.midi_duration()/4,100)
                        if eachnote.midi_pitch() % 12 in [2,4,7,9,11]:
                            outputMIDI.addNote(0,0,eachnote.midi_pitch()-2,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+eachnote.midi_duration()/4,eachnote.midi_duration()/4,100)
                        else:
                            outputMIDI.addNote(0,0,eachnote.midi_pitch()-1,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+eachnote.midi_duration()/4,eachnote.midi_duration()/4,100)
                        outputMIDI.addNote(0,0,eachnote.midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+eachnote.midi_duration()/2,eachnote.midi_duration()/2,100)
                    elif eachnote.agrement == 'tremblement':
                        d = eachnote.midi_duration()/8
                        p = eachnote.midi_pitch()
                        if p % 12 in [2,4,7,9,11]:
                            m = p - 2
                        else:
                            m = p - 1
                        for i in range(4):
                            outputMIDI.addNote(0,0,p,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+2*i*d,d,100)
                            outputMIDI.addNote(0,0,m,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+2*i*d+d,d,100)
                    elif eachnote.agrement == 'appuye':
                        d = eachnote.midi_duration()/12
                        p = eachnote.midi_pitch()
                        if p % 12 in [2,4,7,9,11]:
                            m = p - 2
                        else:
                            m = p - 1
                        outputMIDI.addNote(0,0,p,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote),d*3,100)
                        outputMIDI.addNote(0,0,m,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+d*3,d,100)
                        for i in range(2,6):
                            outputMIDI.addNote(0,0,p,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+2*i*d,d,100)
                            outputMIDI.addNote(0,0,m,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+2*i*d+d,d,100)
                    elif eachnote.agrement == 'portdevoix':
                        outputMIDI.addNote(0,0,previousnote.midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote),eachnote.midi_duration()/2,100)
                        outputMIDI.addNote(0,0,eachnote.midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+eachnote.midi_duration()/2,eachnote.midi_duration()/2,100)
                    elif eachnote.agrement == 'mordent':
                        outputMIDI.addNote(0,0,eachnote.midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)-1/16,1/32,100)
                        outputMIDI.addNote(0,0,eachnote.midi_pitch()-1,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)-1/32,1/32,100)
                        outputMIDI.addNote(0,0,eachnote.midi_pitch(),BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote),eachnote.midi_duration(),100)
                    elif eachnote.agrement == 'cadence':
                        d = eachnote.midi_duration()/12
                        p = eachnote.midi_pitch()
                        if p % 12 in [2,4,7,9,11]:
                            m = p - 2
                        else:
                            m = p - 1
                        if m % 12 in [2,4,7,9,11]:
                            b = m - 2
                        else:
                            b = m - 1
                        outputMIDI.addNote(0,0,p,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote),d,100)
                        outputMIDI.addNote(0,0,b,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+2*d,d,100)
                        for i in range(6):
                            outputMIDI.addNote(0,0,m,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+2*i*d+d,d,100)
                        for i in range(2,6):
                            outputMIDI.addNote(0,0,p,BEATS_PER_STAFF*(eachstaff.id//STAVES_PER)+eachstaff.time_a_note(eachnote)+2*i*d,d,100)
                if eachnote.agrement == 'double':
                    previoushaddouble = True
                    previousnote = [previousnote,eachnote]
                else:
                    previousnote = eachnote
        filename = f"Harpischord in {previousnote.pitch[0].upper()}, No. {int(random.random()*100)}.mid"
        with open(filename,"wb") as output_file:
            outputMIDI.writeFile(output_file)
        os.startfile(filename)
        return agrements
    
    # The real game begins here!
    #########################################################################################
    ## Three things were considered in writing the dialogue for the character of Elisabeth
    ## Jean-Claude Jacquet de la Guerre.  Firstly, according to Cessac's biography, she was
    ## born and died in Paris, France, and composed vocal music in French and occasionally
    ## Italian and Latin; there is little evidence of her having spoken English, the native
    ## language of the game's intended audience; as such, her character speaks in English with
    ## occasional French words, in the style called "Poirot Speak"
    speech = '''Bonjour!  Je m'appelle Elisabeth Jean-Claude Jacquet de la Guerre.
    One of my favorite pastimes is to compose a beautiful harpsichord suite on a piece of parchment such as this.
    Care to join me, mon amis?
    \n\n
    [Press any key to continue.]'''
    parle(screen,speech) # Put her words up and wait for a keypress or mouse click.
    if wait_press() == -1:
        return
    speech = '''Incroyable!  First, let us commence with the time signature.
    Find a rhythm that suits you and choose what you must.
    \n\n
    [Press the time signature button to browse time signatures.
    Click the staff paper to apply one.]'''
    parle(screen,speech)
    timebutton.selectable = True # Let player click on the time signature button to scroll
    while timebutton.selectable: # through the time signatures available, then apply it
        for e in pygame.event.get(): # the moment staff paper is clicked.
            if e.type == pygame.QUIT:
                return
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if timebutton.rect.collidepoint(e.pos):
                    timebutton.feel_click()
                    screen.blit(timebutton.image,timebutton.rect)
                    pygame.display.update()
                elif PAPER_RECT.collidepoint(e.pos):
                    for s in range(SYSTEMS*STAVES_PER):
                        staves[s].change_time(timebutton.statuslist[timebutton.status])
                    timebutton.grey() # After time signature is chosen, player cannot change it.
                    screen.blit(timebutton.image,timebutton.rect) # What would that do to all the notes?
                    timebutton.selectable = False
    speech = '''Change or add a clef in your piece with this tool here.
    Unfortunately, to accommodate to your perverted modern ways of notation,
    I have made my C-clef shaped in a more wavy and less rigid manner.”
    \n\n
    [Click the clef button to select an upper clef.
    Click the staff paper to apply it.]'''
    parle(screen,speech) # Same process with choosing a C-clef or a G-clef for the upper register.
    clefbutton.selectable = True
    while clefbutton.selectable:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if clefbutton.rect.collidepoint(e.pos):
                    clefbutton.feel_click()
                    screen.blit(clefbutton.image,clefbutton.rect)
                    pygame.display.update()
                elif PAPER_RECT.collidepoint(e.pos):
                    for s in range(SYSTEMS):
                        staves[2*s].change_clef(clefbutton.statuslist[clefbutton.status])
                    clefbutton.grey()
                    screen.blit(clefbutton.image,clefbutton.rect)
                    clefbutton.selectable = False
    speech = '''Excellente!  To place a note, find whichever note on the bottom left of the parchment tickles your fancy.
    Then, let the artiste in you choose where in the piece to place it.
    \n\n
    [Press any key to continue.]'''
    parle(screen,speech) # Player must go through two dialogues before playing.
    if wait_press() == -1:
        return 
    speech = '''Once your composition is finished, push the play button on the bottom right of the parchment and let la musique play.
    After it has played, you may resume editing the piece if you wish.  Worry not about how magnifique it sounds, but just know that I will be silently judging.
    \n\n
    [Press any key to continue.]'''
    parle(screen,speech)
    if wait_press() == -1:
        return # Last message remains up.
    parle(screen,"Alright, mes amis, if you need any more instruction, just click on my beautiful visage.")

    for eachbutton in buttons:
        eachbutton.selectable = True

    # Main loop of game - all buttons except clef and time are available.
    # Check for game exiting and clicking on buttons, staff paper, and Elisabeth.
    # The player's current intentions are given by the 'selected_function' variable -
    # 'select' means player can only click buttons or Elisabeth,
    # 'explain' means player has just clicked on Elisabeth and whatever is clicked on next gives explanation, not function
    # anything else (the function of the most recently clicked button) is passed to staves/notes clicked on.
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if BUTTON_RECT.collidepoint(e.pos):
                    if selected_function == 'explain':
                        for eachbutton in buttons:
                            if eachbutton.rect.collidepoint(e.pos):
                                parle(screen,eachbutton.explanation)
                            selected_function = 'select'
                        if playbutton.rect.collidepoint(e.pos):
                            parle(screen,playbutton.explanation)
                    else:
                        selected_function = 'select'
                        for eachbutton in buttons:
                            if eachbutton.rect.collidepoint(e.pos):
                                eachbutton.feel_click()
                                selected_function = eachbutton.statuslist[eachbutton.status]
                            else:
                                eachbutton.unselect()
                        buttons.draw(screen)
                        if playbutton.rect.collidepoint(e.pos):
                            if output_music():
                                speech = '''Magnifique! I had my doubts, however, you have made a Baroque piece to rival even my talents (not really).'''
                            else:
                                speech = '''How dreadfully plain… so rigid and boring. What is a piece without embellishment?
                                Spice it up with some agréments, no?'''
                            parle(screen,speech)
                elif PAPER_RECT.collidepoint(e.pos):
                    new_agrement = False
                    if selected_function in AGREMENT_DONE_DICT and AGREMENT_DONE_DICT[selected_function] == False:
                        new_agrement = True
                    for eachstaff in staves:
                        if eachstaff.rect.collidepoint(e.pos):
                            eachstaff.feel_click(e.pos,selected_function)
                            if selected_function in ["eraser","inverse"]:
                                redraw_staff_paper()
                            elif selected_function in ["eighth","sixteenth"]:
                                eachstaff.generate_image()
                    if new_agrement and AGREMENT_DONE_DICT[selected_function]:
                        if selected_function == 'pince':
                            speech = "Pincé ... just a quaint little trill, is it not?"
                        elif selected_function == 'tremblement':
                            speech = "Ah, the tremblement, that is a trill to warm the fingers!"
                        elif selected_function == 'double':
                            speech = "The doublé certainly enlivens a scale passage."
                        elif selected_function == 'portdevoix':
                            speech = "The port de voix, just an easy simple to draw ... after my time, Rameau would use that symbol for everything."
                        elif selected_function == 'appuye':
                            speech = "No trill is stronger than the tremblement appuyé!"
                        elif selected_function == 'mordent':
                            speech = "I hope that is an important note, that one you emphasize with the mordent."
                        elif selected_function == 'cadence':
                            speech = "My fellow French composer Jean-Henri d'Anglebert liked that tricky trill, the cadence.  It's not too difficult for my fingers, either!"
                            ################################################################
                            ## Here Elisabeth's remarks give the player a clue as to what
                            ## the agréments do, the moment the player first adds one of any given kind.
                            ## Her remark about Rameau is justified; in:
                            ##
                            ##
                            ##
                            ## he writes that "French composers generally used signs (the most
                            ## common being +, which could indicate virtually any kind of
                            ## ornament)" and cited Rameau.
                            ################################################################
                        parle(screen,speech)
                elif e.pos[0] > CHAT_RECT.left and e.pos[1] < CHAT_RECT.top:
                    # TODO Have her object to being clicked on repeatedly?
                    speech = '''So you’ve come back for more… Listen, s’il vous plaît, and I will provide a few more tips.
                    \n\n
                    [Click on something for an explanation of it.]'''
                    parle(screen,speech)
                    selected_function = 'explain'

            pygame.display.update()

if __name__ == '__main__':
    main()
