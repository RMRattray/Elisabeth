# Elisabeth and the Music Maker

# MUS 381 - Music History until 1800
# Capstone project - multimedia

import pygame
from pygame import sprite
pygame.init()
import os

# Dimensions in pixels
WINDOW_DIM = (1200,800)
BUTTON_DIM = (60,80)
BUFFER = 10
CHAT_DIM = (200,WINDOW_DIM[1]-BUTTON_DIM[1]-2*BUFFER)
STAVES = 3
STAVES_PER = 2
MEASURES_PER = 4
STAFF_HEIGHT = int((WINDOW_DIM[1] - BUTTON_DIM[1] - 2*BUFFER)/(2*STAVES*STAVES_PER+1))
STAFF_LENGTH = WINDOW_DIM[0] - CHAT_DIM[0] - 4*STAFF_HEIGHT
SIGN_STAFF_LENGTH = 2*STAFF_HEIGHT
PAGEDIM = (STAFF_LENGTH+SIGN_STAFF_LENGTH+STAFF_HEIGHT,WINDOW_DIM[1]-BUTTON_DIM[1]-2*BUFFER-STAFF_HEIGHT)
NOTE_LINE = 4

# Colors
WINDOW_BACKGROUND = (240,240,240)
UNCLICKED_BUTTON = (200,200,200)
CLICKED_BUTTON = (180,180,180)
PAPER_COLOR = (230,230,200)
INK_COLOR = (40,20,20)

MAIN_DIR = os.path.dirname(os.getcwd())
def get_asset(assetname):
    return pygame.image.load(os.path.join(MAIN_DIR,'Elisabeth','Elisabeth_Assets',assetname))

# Graphics dictionaries
CLEF_DICT = {"cclef":get_asset("cclef.png"),"bass":get_asset("bass.png")}
CLEF_NOTE_DICT = {'treble':38,'cclef':36,'bass':26}
ACCI_DICT = {"sharp":get_asset("sharp.png"),"flat":get_asset("flat.png")}
NOTE_TIME_DICT = {"whole":1.0,"half":0.5,"quarter":0.25,"eighth":0.125,"sixteenth":0.0625}
NOTE_PICT_DICT = {"whole":get_asset("whole.png"),"half":get_asset("half.png"),"quarter":get_asset("quarter.png"),
    "eighth":get_asset("eighth.png"),"sixteenth":get_asset("sixteenth.png")}


## Classes
##
################################################################
#
# A class for the button objects, seen at the bottom of the screen.
class pybutton(pygame.sprite.Sprite): # Inherits from Sprite b/c has appearance
    def __init__(self,statusdict,position,*groups):
        super().__init__(*groups)
        for eachkey in statusdict:
            statusdict[eachkey] = pygame.transform.scale(statusdict[eachkey],BUTTON_DIM)
        self.statusdict = statusdict
        self.statuslist = list(statusdict)
        self.status = 0
        self.selected = False
        self.position = position
        self.rect = pygame.Rect(position[0],position[1],BUTTON_DIM[0],BUTTON_DIM[1])
        self.image = pygame.Surface(BUTTON_DIM)
        self.image.fill(UNCLICKED_BUTTON)
        self.image.blit(self.statusdict[self.statuslist[self.status]],(0,0))
    
    def feel_click(self):
        if not self.selected:
            self.selected = True
            self.image.fill(CLICKED_BUTTON)
            self.image.blit(self.statusdict[self.statuslist[self.status]],(0,0))
        else:
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

class Note(pygame.sprite.Sprite): # A note that appears on the paper, not including any marks.
    def __init__(self,time,duration,pitch,accidental='natural',agrement=None,orientation=True,*groups):
        super().__init__(*groups)
        self.time = time # The position in time in which this note is played, as a tuple of measure and quarter.
        self.duration = duration # The duration for which this note is played; e.g., 0.75 for dotted half note.
        self.pitch = pitch # The pitch of this note without accidental, e.g., 'c4' for C-sharp above middle C
        self.accidental = accidental # Either 'sharp,' 'natural,' or 'flat.'
        self.accidented = False # Whether the note's symbol needs to be shown.
        self.agrement = agrement # Any agrement the note carries.
        self.orientation = orientation # True if, for a quarter note, shaped like a d, False if like a p.
    
    def set_position(self,staffpos,stafftime,staffclef):
        distalong = int((self.time[0]-1+(self.time[1]-1)*stafftime[1]/(4*stafftime[0]))*STAFF_LENGTH/MEASURES_PER)
        toprung = CLEF_NOTE_DICT[staffclef]
        rung = {'c':0,'d':1,'e':2,'f':3,'g':4,'a':5,'b':6}[self.pitch[0]] + 7*int(self.pitch[1])
        self.stepsdown = toprung - rung
        headdown = int(self.stepsdown*STAFF_HEIGHT/8-NOTE_LINE/2)
        distdown = headdown - int(3*STAFF_HEIGHT/8)
        if self.orientation:
            distdown = headdown - int(9*STAFF_HEIGHT/8)
        self.position = ( int(staffpos[0]+STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+distalong), int(staffpos[1]+0.5*STAFF_HEIGHT+distdown) )
        print(f"Time: {self.time}")
   
    def generate_image(self):
        # Make image surface
        self.image = pygame.Surface((int(self.duration*STAFF_LENGTH/MEASURES_PER),int(1.25*STAFF_HEIGHT)))
        self.rect = pygame.Rect(self.position[0],self.position[1],self.image.get_width(),self.image.get_height())
        self.image.fill(PAPER_COLOR)
        # Draw notehead to surface
        centerx = int(STAFF_LENGTH/(32*MEASURES_PER))
        headpos = (centerx,int(3*STAFF_HEIGHT/8))
        if self.orientation:
            headpos = (centerx,int(9*STAFF_HEIGHT/8))
        if self.duration >= 0.5:
            pygame.draw.circle(self.image,INK_COLOR,headpos,int(STAFF_HEIGHT/8),NOTE_LINE)
        else:
            pygame.draw.circle(self.image,INK_COLOR,headpos,int(STAFF_HEIGHT/8))
        # Draw note line to surface
        if self.duration < 1:
            if self.orientation:
                pygame.draw.line(self.image,INK_COLOR,(int(centerx+STAFF_HEIGHT/8-NOTE_LINE),headpos[1]),(int(centerx+STAFF_HEIGHT/8-NOTE_LINE),int(STAFF_HEIGHT/4)),NOTE_LINE)
            else:
                pygame.draw.line(self.image,INK_COLOR,(int(centerx-STAFF_HEIGHT/8-NOTE_LINE),headpos[1]),(int(centerx-STAFF_HEIGHT/8-NOTE_LINE),self.image.get_height()),NOTE_LINE)
        # Draw dot (if it exists)
        if self.duration * 16 % 1 != 0:
            pygame.draw.circle(self.image,INK_COLOR,(headpos[0]+int(STAFF_HEIGHT/8),headpos[1]),NOTE_LINE)
        # Draw accidental (if it is marked)
        if self.accidented:
            mark = pygame.transform.scale(ACCI_DICT[self.accidental],(STAFF_HEIGHT/4,STAFF_HEIGHT/3))
            mark.blit(self.image,(int(headpos[0]-STAFF_HEIGHT/4),int(headpos[1]-STAFF_HEIGHT/3)))
        # Draw agrement (if it exists)
        # !!!!!!! Add agrements here!  They go above the note.
    
    def feel_click(self,selected_function):
        print(selected_function)

class Staff(pygame.sprite.Sprite):
    def __init__(self,position,clef='cclef',timesig=(4,4),notes=[],*groups):
        super().__init__(*groups)
        self.position = position # Absolute position on the screen.  Tuple.
        self.clef = clef # Clef at the front, as a string.
        self.timesig = timesig # Time signature, as a tuple, e.g. (3,4) for waltz time.
        self.notes = pygame.sprite.Group() # Group of Note objects
        
        self.image = pygame.Surface((STAFF_LENGTH+SIGN_STAFF_LENGTH+STAFF_HEIGHT,2*STAFF_HEIGHT))
        self.rect = pygame.Rect(self.position[0],self.position[1],self.image.get_width(),self.image.get_height())
        self.image.fill(PAPER_COLOR)
        for l in range(5):
            pygame.draw.line(self.image,INK_COLOR,(int(STAFF_HEIGHT/2),int((2+l)*STAFF_HEIGHT/4)),(int(STAFF_LENGTH+SIGN_STAFF_LENGTH+STAFF_HEIGHT/2),int((2+l)*STAFF_HEIGHT/4)))
        for m in range(MEASURES_PER):
            pygame.draw.line(self.image,INK_COLOR,(int(STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+m*STAFF_LENGTH/MEASURES_PER),int(STAFF_HEIGHT/2)),(int(STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+m*STAFF_LENGTH/MEASURES_PER),int(3*STAFF_HEIGHT/2)))
        self.image.blit(pygame.transform.scale(CLEF_DICT[self.clef],(STAFF_HEIGHT,STAFF_HEIGHT)),(int(STAFF_HEIGHT/2),int(STAFF_HEIGHT/2)))

    def generate_image(self):
        self.image = pygame.Surface((STAFF_LENGTH+SIGN_STAFF_LENGTH+STAFF_HEIGHT,2*STAFF_HEIGHT))
        self.rect = pygame.Rect(self.position[0],self.position[1],self.image.get_width(),self.image.get_height())
        self.image.fill(PAPER_COLOR)
        for l in range(5):
            pygame.draw.line(self.image,INK_COLOR,(int(STAFF_HEIGHT/2),int((2+l)*STAFF_HEIGHT/4)),(int(STAFF_LENGTH+SIGN_STAFF_LENGTH+STAFF_HEIGHT/2),int((2+l)*STAFF_HEIGHT/4)))
        for m in range(MEASURES_PER):
            pygame.draw.line(self.image,INK_COLOR,(int(STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+m*STAFF_LENGTH/MEASURES_PER),int(STAFF_HEIGHT/2)),(int(STAFF_HEIGHT/2+SIGN_STAFF_LENGTH+m*STAFF_LENGTH/MEASURES_PER),int(3*STAFF_HEIGHT/2)))
        self.image.blit(pygame.transform.scale(CLEF_DICT[self.clef],(STAFF_HEIGHT,STAFF_HEIGHT)),(int(STAFF_HEIGHT/2),int(STAFF_HEIGHT/2)))
        # Add time signature blit here
        for eachnote in self.notes:
            self.image.blit(eachnote.image,(eachnote.position[0]-self.position[0],eachnote.position[1]-self.position[1]))
    
    def change_clef(self):
        cleflist = list(CLEF_DICT)
        place = cleflist.index(self.clef)
        if place == len(cleflist) - 1:
            place = 0
        else:
            place += 1
        self.clef = cleflist[place]

        self.generate_image()

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
                    return False
            if selected_function in NOTE_TIME_DICT:
                duration = NOTE_TIME_DICT[selected_function]
                distalong = relpos[0] - 2.5*STAFF_HEIGHT
                measure = 1 + distalong // (STAFF_LENGTH/MEASURES_PER)
                beatinown = 1 + (distalong - (measure-1)*STAFF_LENGTH/MEASURES_PER) // (duration*STAFF_LENGTH/MEASURES_PER)
                print(f"Beat in own: {beatinown}")
                time = (measure,(beatinown-1)*4*duration+1)
                stepsdown = (relpos[1] - 5*STAFF_HEIGHT/16) // (STAFF_HEIGHT/8)
                toprung = CLEF_NOTE_DICT[self.clef]
                notename = {0:'c',1:'d',2:'e',3:'f',4:'g',5:'a',6:'b'}[(toprung-stepsdown) % 7]
                noteoctave = (toprung-stepsdown) // 7
                newnote = Note(time,duration,notename+str(noteoctave))
                newnote.set_position(self.position,self.timesig,self.clef)
                newnote.generate_image()
                self.notes.add(newnote)
                self.generate_image()

# Main function

def main():
    # Initialize display window
    screen = pygame.display.set_mode(pygame.Rect((0,0,WINDOW_DIM[0],WINDOW_DIM[1])).size)
    screen.fill(WINDOW_BACKGROUND)
    pygame.display.set_caption("Elisabeth and the Music Maker")

    # Set up buttons
    clefbutton = pybutton(CLEF_DICT,(BUFFER,WINDOW_DIM[1]-BUTTON_DIM[1]-BUFFER))
    accibutton = pybutton(ACCI_DICT,(2*BUFFER+BUTTON_DIM[0],WINDOW_DIM[1]-BUTTON_DIM[1]-BUFFER))
    notebutton = pybutton(NOTE_PICT_DICT,(3*BUFFER+2*BUTTON_DIM[0],WINDOW_DIM[1]-BUTTON_DIM[1]-BUFFER))
    buttons = pygame.sprite.Group(clefbutton,accibutton,notebutton)
    buttons.draw(screen)

    # Draw Elisabeth
    lispic = get_asset("Elisabeth.jpg")
    screen.blit(pygame.transform.scale(lispic,(CHAT_DIM[0],int(CHAT_DIM[0]*lispic.get_height()/lispic.get_width()))),(WINDOW_DIM[0]-CHAT_DIM[0],0))
    
    # Draw staff paper
    pygame.draw.rect(screen,PAPER_COLOR,(int(STAFF_HEIGHT/2),int(STAFF_HEIGHT/2),PAGEDIM[0],PAGEDIM[1]))
    staves = pygame.sprite.Group()
    for s in range(STAVES*STAVES_PER):
        staves.add(Staff((int(STAFF_HEIGHT/2),int((4*s+1)*STAFF_HEIGHT/2))))
    staves.draw(screen)
    
    pygame.display.update()

    selected_function = 'select'

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if e.pos[1] > WINDOW_DIM[1] - BUTTON_DIM[1]: # In other words, if a click was made in the button area
                    #clickrect = pygame.Rect(e.pos[0],e.pos[1],0,0)
                    selected_function = 'select'
                    for eachbutton in buttons:
                        if eachbutton.rect.collidepoint(e.pos[0],e.pos[1]):
                            eachbutton.feel_click()
                            selected_function = eachbutton.statuslist[eachbutton.status]
                        else:
                            eachbutton.unselect()
                
                    buttons.draw(screen)
                elif e.pos[0] < WINDOW_DIM[0] - CHAT_DIM[0]: # If a click in the paper area.
                    for eachstaff in staves:
                        if eachstaff.rect.collidepoint(e.pos):
                            eachstaff.feel_click(e.pos,selected_function)
                            eachstaff.notes.draw(screen)
            pygame.display.update()

if __name__ == '__main__':
    main()