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
import math
import pygame
from pygame import sprite
pygame.init()
import os
from midiutil import MIDIFile

# The following lines determine the dimensions of various on-screen objects in pixels.
WINDOW_DIM = (1300,800) # Entire game window (width, height)
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
AGREMENT_DICT = {"agrement1":get_asset("1,5.png")}
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

## This research project was started because of unfamiliarity with the notation
## used by Elisabeth Jean-Claude Jacquet de la Guerre in her Suite in A Minor,
## so the appearance of notes in the game is based on her manuscript, specifically:
##
## Jacquet de la Guerre, Elisabeth.  Pièces de clavecín, livre 1 (Paris:  de Baussen, 1687).
##
## accessed through the Petrucci Music Library.  The Prelude presents the most challenging
## notation to imitate, with its own unique expectations for improvisation.  Such style
## is considered too complicated for this program, however, and the appearance of normal-ish
## notes and familiar bar lines makes up this game.  Details for note appearance
## atypical of today's music are marked with ## comments throughout the Note class.

class Note():
    def __init__(self,staff,time,duration,pitch,accidental='',agrement='',orientation=True):
        self.staff = staff # The staff in which the note appears (a Staff object)
        self.time = time # The position in time in which this note is played, as a tuple of measure and quarter.
        self.duration = duration # The duration for which this note is played; e.g., 0.75 for dotted half note.
        self.pitch = pitch # The pitch of this note without accidental, e.g., 'c4' for C-sharp above middle C
        self.accidental = accidental # Either 'sharp,' '' or 'flat.'
        ## As seen in the third measure of the first "Allemande," and throughout the suite,
        ## accidentals do not carry from note to note, even within the same octave and measure
        ## (or else de la Guerre is including unusually many courtesy accidentals).
        # As such, the variable self.accidental determines whether an accidental appears and is used to
        # find the pitch for the MIDI output all the same.
        self.agrement = agrement # Any agrement the note carries.
        self.orientation = orientation # True if, for a quarter note, shaped like a d, False if like a p.
        ## Also seen throughout the piece are inverted notes with their stems proceeding from their middle,
        ## not the left side.  This change of appearance is reflect in the game.  And though today it is
        ## conventional for notes' orientations to be determined by where they appear in relation to the
        ## central line of a staff, in Jacquet de la Guerre's pieces it is more often a function of its
        ## voicing (still typical of choral music today), so this orientation is determined by the player.
    
    def __str__(self):
        return f"Note {self.pitch} at {self.time} in Staff #{self.staff.id}."
    
    def set_position(self):
        # For the sake of simplicity, notes appear in precise locations based on beat.
        distalong = int((self.time[0]-1+(self.time[1]-1)*self.staff.timesig[1]/(4*self.staff.timesig[0]))*STAFF_LENGTH/MEASURES_PER)
        toprung = CLEF_NOTE_DICT[self.staff.clef]
        rung = {'c':0,'d':1,'e':2,'f':3,'g':4,'a':5,'b':6}[self.pitch[0]] + 7*int(self.pitch[1])
        self.stepsdown = toprung - rung
        headdown = int((self.stepsdown-1)*STAFF_HEIGHT/8)
        distdown = headdown - int(3*STAFF_HEIGHT/8)
        if self.orientation:
            distdown = headdown - int(9*STAFF_HEIGHT/8)
        self.position = ( int(self.staff.position[0]+STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+distalong), int(self.staff.position[1]+0.5*STAFF_HEIGHT+distdown) )
        centerx = int(STAFF_LENGTH/(32*MEASURES_PER)) + self.position[0]
        if self.orientation:
            self.tip_position = (int(centerx+STAFF_HEIGHT/8-NOTE_LINE),int(STAFF_HEIGHT/4+self.position[1]))
        else:
            self.tip_position = (int(centerx-STAFF_HEIGHT/8+NOTE_LINE),self.position[1]+self.rect.height)
        self.rect = pygame.Rect(self.position[0],self.position[1],int(self.duration*STAFF_LENGTH*self.staff.timesig[1]/(MEASURES_PER*self.staff.timesig[0])),int(1.25*STAFF_HEIGHT))
   
    def generate_image(self):
        # Make image surface
        #self.image = pygame.Surface((int(self.duration*STAFF_LENGTH/MEASURES_PER),int(1.25*STAFF_HEIGHT)))
        #self.image.fill(PAPER_COLOR)
        # Draw notehead to surface
        centerx = int(STAFF_LENGTH/(32*MEASURES_PER)) + self.position[0]
        headpos = (centerx,int(3*STAFF_HEIGHT/8) + self.position[1])
        if self.orientation:
            headpos = (centerx,int(9*STAFF_HEIGHT/8) + self.position[1])
        if self.duration >= 0.5:
            pygame.draw.circle(self.staff.screen,INK_COLOR,headpos,int(STAFF_HEIGHT/8),NOTE_LINE)
        else:
            pygame.draw.circle(self.staff.screen,INK_COLOR,headpos,int(STAFF_HEIGHT/8))
        # Draw note line to surface
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
    
    def feel_click(self,selected_function):
        if selected_function in ACCI_DICT:
            self.accidental = selected_function
            self.generate_image()
        elif selected_function == "inverse":
            if self.orientation:
                self.orientation = False 
            else:
                self.orientation = True 
            self.set_position()
        elif selected_function == "eraser":
            if self.agrement != '':
                self.agrement = ''
            elif self.accidental != '':
                self.accidental = ''
            else:
                self.staff.notes.remove(self)
        elif selected_function == "dot":
            if self.duration * 32 % 3 != 0:
                self.duration *= 1.5
                self.rect.width = int(self.rect.width*1.5)
                self.generate_image()
            else:
                self.duration *= 2/3
                self.rect.width = int(self.rect.width*2/3)
                self.generate_image()
        elif selected_function in AGREMENT_DICT:
            self.agrement = selected_function
            self.generate_image()

class Staff():
    def __init__(self,screen,position,id,clef='cclef',timename="common"):
        self.screen = screen
        self.position = position # Absolute position on the screen.  Tuple.
        self.clef = clef # Clef at the front, as a string.
        self.timename = timename # Time signature, as a string, e.g. "common"
        self.timesig = TIME_TUPLE_DICT[timename] # Time signature, as a tuple, e.g. (4,4)
        self.notes = []
        self.id = id
        self.rect = pygame.Rect(self.position[0],self.position[1],STAFF_LENGTH+SIGN_STAFF_LENGTH+STAFF_HEIGHT,2*STAFF_HEIGHT)

    # The process by which a staff renders itself, based on the notation in Elisabeth Jean-Claude Jacquet de la Guerre's
    # own score for her Suite in A Minor, is described below.
    def generate_image(self):
        # Erase the rest of what's in the staff's area
        pygame.draw.rect(self.screen,PAPER_COLOR,self.rect)
        # Draw five horizontal lines and vertical lines in between measures.
        for l in range(5):
            pygame.draw.line(self.screen,INK_COLOR,(int(STAFF_HEIGHT/2+self.position[0]),int((2+l)*STAFF_HEIGHT/4+self.position[1])),(int(STAFF_LENGTH+SIGN_STAFF_LENGTH+STAFF_HEIGHT/2)+self.position[0],int((2+l)*STAFF_HEIGHT/4+self.position[1])))
        for m in range(MEASURES_PER):
            pygame.draw.line(self.screen,INK_COLOR,(int(STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+m*STAFF_LENGTH/MEASURES_PER+self.position[0]),int(STAFF_HEIGHT/2+self.position[1])),(int(STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+m*STAFF_LENGTH/MEASURES_PER+self.position[0]),int(3*STAFF_HEIGHT/2+self.position[1])))
        # Draw the clef at the front of each staff.  The C-clef can reach half the staff height below the staff.
        self.screen.blit(pygame.transform.scale(CLEF_DICT[self.clef],(STAFF_HEIGHT,int(1.5*STAFF_HEIGHT))),(int(STAFF_HEIGHT/2+self.position[0]),int(STAFF_HEIGHT/2+self.position[1])))
        # Draw the time signature immediately following the clef.
        self.screen.blit(pygame.transform.scale(TIME_DICT[self.timename],(STAFF_HEIGHT,STAFF_HEIGHT)),(int(3*STAFF_HEIGHT/2+self.position[0]),int(STAFF_HEIGHT/2+self.position[1])))
        # Draw the notes, or at least, their heads, stems, and special marks, as these can be done independently.
        for eachnote in self.notes:
            eachnote.generate_image()
        # Connect stems of eighth notes, sixteeth notes in same beat
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
                            pygame.draw.line(self.screen,INK_COLOR,(left_note.tip_position[0],left_note.tip_position[1]+4*NOTE_LINE),(right_note.tip_position[0],right_note.tip_position[1]+4*NOTE_LINE),2*NOTE_LINE)
                        else:
                            xchange = (right_note.tip_position[0] - left_note.tip_position[0]) // 2
                            pygame.draw.line(self.screen,INK_COLOR,(left_note.tip_position[0],left_note.tip_position[1]+4*NOTE_LINE),(left_note.tip_position[0]+xchange,int(left_note.tip_position[1]+slope*xchange+4*NOTE_LINE)),2*NOTE_LINE)
                    elif right_note.duration < 0.125 and everypair == len(noteset) - 2:
                        xchange = (right_note.tip_position[0] - left_note.tip_position[0]) // 3
                        pygame.draw.line(self.screen,INK_COLOR,(right_note.tip_position[0],right_note.tip_position[1]+4*NOTE_LINE),(right_note.tip_position[0]+xchange//2,int(right_note.tip_position[1]+slope*xchange/2+4*NOTE_LINE)),2*NOTE_LINE)
                        pygame.draw.line(self.screen,INK_COLOR,(right_note.tip_position[0],right_note.tip_position[1]),(right_note.tip_position[0]+xchange//2,int(right_note.tip_position[1]+slope*xchange/2)),2*NOTE_LINE)
        beat = 0
        shared_upper_notes = []
        shared_lower_notes = []
        itsbeat = 0
        for eachnote in range(len(self.notes)):
            # Go through notes, beat by beat, ignoring all without flags.
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

    def change_clef(self,clef):
        self.clef = clef
        self.generate_image()
    
    def change_time(self,time):
        self.timename = time 
        self.timesig = TIME_TUPLE_DICT[time]
        self.generate_image()
    
    def time_a_note(self,note):
        return note.time[0]*self.timesig[0] + note.time[1]

    def feel_click(self,mousepos,selected_function):
        relpos = (mousepos[0]-self.position[0],mousepos[1]-self.position[1])
        if relpos[0] < 1.5*STAFF_HEIGHT:
            self.change_clef()
            return False
        elif relpos[0] < 2.5*STAFF_HEIGHT:
            pass # Change time signature here.
        else:
            for eachnote in self.notes:
                if eachnote.rect.collidepoint(mousepos):
                    eachnote.feel_click(selected_function)
                    self.generate_image()
                    return False
            if selected_function in NOTE_TIME_DICT:
                # Algorithm for when a staff is clicked on with the note placement tool.
                # First, find the time of the note.
                duration = NOTE_TIME_DICT[selected_function]
                distalong = relpos[0] - 2.5*STAFF_HEIGHT
                measure = 1 + distalong // (STAFF_LENGTH/MEASURES_PER)
                beatinown = 1 + (distalong - (measure-1)*STAFF_LENGTH/MEASURES_PER) // (duration*STAFF_LENGTH*self.timesig[1]/(MEASURES_PER*self.timesig[0]))
                # For example, the eighth note in the seventh eighth of a measure has a 'beatinown' of 7.
                while duration*beatinown > self.timesig[0]/self.timesig[1]:
                    duration *= 0.5
                    beatinown = 1 + 2*(beatinown-1)
                time = (measure,(beatinown-1)*4*duration+1)
                # Second, the pitch of the note.
                stepsdown = (relpos[1] - 5*STAFF_HEIGHT/16) // (STAFF_HEIGHT/8)
                toprung = CLEF_NOTE_DICT[self.clef]
                notename = {0:'c',1:'d',2:'e',3:'f',4:'g',5:'a',6:'b'}[(toprung-stepsdown) % 7]
                noteoctave = (toprung-stepsdown) // 7
                newnote = Note(self,time,duration,notename+str(noteoctave))
                newnote.set_position()
                #newnote.generate_image(screen)
                self.notes.append(newnote)
                self.notes.sort(key=self.time_a_note)
                self.generate_image()

# Main function

def main():
    # Initialize display window
    screen = pygame.display.set_mode(pygame.Rect((0,0,WINDOW_DIM[0],WINDOW_DIM[1])).size)
    screen.fill(WINDOW_BACKGROUND)
    pygame.display.set_caption("Elisabeth and the Music Maker")

    # Set up buttons
    buttons = pygame.sprite.Group()
    clefbutton = pybutton(UPPER_CLEF_DICT,(BUFFER,BUTTON_RECT.top+BUFFER))
    timebutton = pybutton(TIME_DICT,(2*BUFFER+BUTTON_DIM[0],BUTTON_RECT.top+BUFFER))
    pybutton(ACCI_DICT,(3*BUFFER+2*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    Something something accidentals''',buttons)
    pybutton(NOTE_PICT_DICT,(4*BUFFER+3*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    Something something note durations''',buttons)
    pybutton(INVERTER_DICT,(5*BUFFER+4*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    Here is a place to go when you wish to flip the tail of your note. While I always make my notes shaped like ‘d’ and ‘q’,
    it has become apparent to moi that the ‘q’ is now a ‘p’. Tres bizarre.''',buttons)
    pybutton(ERASER_DICT,(6*BUFFER+5*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    This is a, how you say, erase button? It looks like a penknife because, back in my day,
    if we made a wrong mark, we had to scratch the ink off with a knife—
    much harder than your fancy typewriters and correction tape nowadays. Be careful not to scratch the parchment!''',buttons)
    pybutton(DOT_DICT,(7*BUFFER+6*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    To extend a note by half its length, use this funny-looking dot.''',buttons)
    pybutton(AGREMENT_DICT,(8*BUFFER+7*BUTTON_DIM[0],BUTTON_RECT.top+BUFFER),'''
    Something something agrements.''',buttons)
    playbutton = pybutton(PLAY_DICT,(WINDOW_DIM[0]-CHAT_WIDTH-BUFFER,BUTTON_RECT.top+BUFFER),'''
    Something about the harpischord for the play button.''')
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
    def parle(screen,mots):
        pygame.draw.rect(screen,PAPER_COLOR,CHAT_RECT)
        bliterate(screen,mots,CHAT_RECT.left,LIS_HEIGHT,CHAT_WIDTH,outerbuffer=10,buffer=5)
        pygame.display.update()
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
        staves.append(Staff(screen,(int(STAFF_HEIGHT/2),int((6*s+1.5)*STAFF_HEIGHT/2)),s))
    for eachstaff in range(len(staves)):
        if eachstaff % STAVES_PER != 0:
            staves[eachstaff].change_clef("bass")
        staves[eachstaff].generate_image()
    #staves.draw(screen)
    
    pygame.display.update()

    selected_function = 'select'

    def redraw_staff_paper():
        pygame.draw.rect(screen,PAPER_COLOR,(int(STAFF_HEIGHT/2),int(STAFF_HEIGHT/2),PAGEDIM[0],PAGEDIM[1]))
        for eachstaff in staves:
            eachstaff.generate_image()
    
    # The real game begins here!
    speech = '''Bonjour!  Je m'appelle Elisabeth Jean-Claude Jacquet de la Guerre.
    One of my favorite pastimes is to compose a beautiful harpsichord suite on a piece of parchment such as this.
    Care to join me, mon amis?
    \n\n
    [Press any key to continue.]'''
    parle(screen,speech)
    if wait_press() == -1:
        return
    speech = '''Incroyable!  First, let us commence with the time signature.
    Find a rhythm that suits you and choose what you must.
    \n\n
    [Press the time signature button to browse time signatures.
    Click the staff paper to apply one.]'''
    parle(screen,speech)
    timebutton.selectable = True
    while timebutton.selectable:
        for e in pygame.event.get():
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
                    timebutton.grey()
                    screen.blit(timebutton.image,timebutton.rect)
                    timebutton.selectable = False
    speech = '''Something something C clef in my day.
    \n\n
    [Click the clef button to select an upper clef.
    Click the staff paper to apply it.]'''
    parle(screen,speech)
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
    parle(screen,speech)
    if wait_press() == -1:
        return 
    speech = '''Once your composition is finished, push the play button on the bottom right of the parchment and let la musique play.
    After it has played, you may resume editing the piece if you wish.  Worry not about how magnifique it sounds, but just know that I will be silently judging.
    \n\n
    [Press any key to continue.]'''
    parle(screen,speech)
    if wait_press() == -1:
        return
    parle(screen,"Alright, mon amis, if you need any more instruction, just click on my beautiful visage.")

    for eachbutton in buttons:
        eachbutton.selectable = True

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
                    else:
                        selected_function = 'select'
                        for eachbutton in buttons:
                            if eachbutton.rect.collidepoint(e.pos):
                                eachbutton.feel_click()
                                selected_function = eachbutton.statuslist[eachbutton.status]
                            else:
                                eachbutton.unselect()
                        buttons.draw(screen)
                elif PAPER_RECT.collidepoint(e.pos): # If a click in the paper area.
                    for eachstaff in staves:
                        if eachstaff.rect.collidepoint(e.pos):
                            eachstaff.feel_click(e.pos,selected_function)
                            if selected_function in ["eraser","inverse"]:
                                redraw_staff_paper()
                            elif selected_function in ["eighth","sixteenth"]:
                                eachstaff.generate_image()
                elif e.pos[0] > CHAT_RECT.left and e.pos[1] < CHAT_RECT.top:
                    speech = '''So you’ve come back for more… Listen, s’il vous plaît, and I will provide a few more tips.
                    \n\n
                    [Click on something for an explanation of it.]'''
                    parle(screen,speech)
                    selected_function = 'explain'
                elif playbutton.rect.collidepoint(e.pos):
                    speech = '''How dreadfully plain… so rigid and boring. What is a piece without embellishment?
                    Spice it up with some agréments, no?'''
                    parle(screen,speech)

            pygame.display.update()

if __name__ == '__main__':
    main()