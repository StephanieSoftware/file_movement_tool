

"""
This is a small GUI based application for moving files.
"""
import wx
from datetime import datetime, timedelta
import shutil
import os
import sqlite3

class FileMovePanel(wx.Panel):
    """Main panel, three buttons, two labels. Handles the main functionality for events.."""
    def __init__(self, parent, *args, **kwargs):
        """Create the MainPanel."""
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.source = "none"
        self.destination = "none"
        self.parent = parent
        self.connection = sqlite3.connect('COMPANY.db')

        #Source buttom definitions
        SourceBtn = wx.Button(self, label="Select Source")
        SourceBtn.Bind(wx.EVT_BUTTON, lambda evt, buttonPressed = "source": self.OnOpen(evt, buttonPressed))

        #Destination button defitions
        DestBtn = wx.Button(self, label="Select Destination")
        DestBtn.Bind(wx.EVT_BUTTON, lambda evt, buttonPressed = "destination": self.OnOpen(evt, buttonPressed ))

        #Initiate file movement button definition
        MoveBtn = wx.Button(self, label="Move Files")
        MoveBtn.Bind(wx.EVT_BUTTON, self.OnMove)

        #Static text defintions. Note that timetext calls the retrieveTimeStamp() method upon start up to grab the current date
        self.SourceText = wx.StaticText(self, -1, "Current Source Folder: " + self.source)
        self.DestText = wx.StaticText(self, -1, "Current Destination Folder: " + self.source)
        self.TimeText = wx.StaticText(self, -1, "Last Time Script Ran: " + self.retrieveTimeStamp())
        
        
        
        #using a sizer for layouts. Sizers allow elements to move as the window size changes.
        Sizer = wx.BoxSizer(wx.VERTICAL)
        Sizer.Add(SourceBtn, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT, 5)
        Sizer.Add(self.SourceText, 0, wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT, 5)
        Sizer.Add(DestBtn, 0, wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT, 5)
        Sizer.Add(self.DestText, 0, wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT, 5)
        Sizer.Add(MoveBtn, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        Sizer.Add(self.TimeText, 0, wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT, 5)

        self.SetSizerAndFit(Sizer)
        
    def retrieveTimeStamp(self): #Grabs the initial timestamp from the database.
        with self.connection:
            c = self.connection.cursor()
            c.execute("SELECT * FROM FileHistory")
            date = c.fetchone()[0]


            return(date)
        
    def changeTimeStamp(self): #Updates the timestamp in the database, sets the text of the static time text, then updates the layout to propgate changes
        with self.connection:
            c = self.connection.cursor()

            c.execute("UPDATE FileHistory SET timeStamp = datetime('now','localtime')")
            self.connection.commit()
            c.execute("SELECT * FROM FileHistory")
            self.TimeText.SetLabel(c.fetchone()[0])
            self.Sizer.Layout() #MUST BE CALLED TO UPDATE LAYOUT!
            
    def modification_date(self, filename): #A method used to get the datetime from a file
        t = os.path.getmtime(filename)
        return datetime.fromtimestamp(t)

    def OnMove(self, event=None): #The event handler for clicking the move files button
        totalFiles = 0 #local variable, stores the amount of files changed as an int
        if(self.source == "none" or self.destination == "none"): #If source or destination hasn't been set
            dlg = wx.MessageDialog(self,
                               message="Destination or Source not set", #Launch a dialog box which gives an error.
                               caption='Error',
                               style=wx.OK|wx.ICON_INFORMATION
                               )
        
            dlg.ShowModal()
            dlg.Destroy()
        else: #otherwise move the files
            for a in os.listdir(self.source):
                if (datetime.utcnow() - self.modification_date(self.source+"\\"+a)) < timedelta(1): #NOTE THE DOUBLE BACKSLASH. wxpython uses backslashes in the dirDialog
                    totalFiles += 1 #If you DO NOT add that double backslashes between the directory and file, it will error.
                    shutil.move(self.source+"\\"+a, self.destination) ## This is like saying folder\folder + \ + filename. Double blackslash adds 1 backslash.
            
            dlg = wx.MessageDialog(self,
                           message="Moved: " + str(totalFiles),
                           caption='Success!',
                           style=wx.OK|wx.ICON_INFORMATION
                           )
            
            dlg.ShowModal()
            dlg.Destroy()
            self.changeTimeStamp() #call the changeTImeStamp method to update the timestamp upon finishing the method. Notice how it only gets called if things work.
            

    
    def OnOpen(self, event, buttonPressed): #Event Handler for both file buttons. Uses a lamda function within the event calls to pass parameters which consolidate code.
            #The parameter that's passed is button pressed.

        openFileDialog = wx.DirDialog(self, "Change Directory of Source Folder", "", 
                                        style=wx.DD_CHANGE_DIR)
        
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed their mind...

        
        # proceed loading the Dialog path chosen by the user based on the source of the button calling the event.
        if(buttonPressed == "source"):
                    self.source = openFileDialog.GetPath()
                    self.SourceText.SetLabel("Source Directory: " + self.source) #Update the static text with the directory path.
        elif(buttonPressed == "destination"):
                    self.destination = openFileDialog.GetPath()
                    self.DestText.SetLabel("Destination Directory: " + self.destination)
        self.Sizer.Layout() #MUST BE CALLED TO UPDATE TEXT

class DemoFrame(wx.Frame): #Basic frame.
    """Main Frame holding the Panel."""
    def __init__(self, *args, **kwargs):
        """Create the DemoFrame."""
        wx.Frame.__init__(self, *args, **kwargs)

        # Build the menu bar
        MenuBar = wx.MenuBar()

        FileMenu = wx.Menu()

        item = FileMenu.Append(wx.ID_EXIT, text="&Quit")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)

        MenuBar.Append(FileMenu, "&File")
        self.SetMenuBar(MenuBar)

        # Add the Widget Panel
        self.Panel = FileMovePanel(self)

        self.Fit()

    def OnQuit(self, event=None):
        """Exit application."""
        self.Close()

def createDatabase(): #Used to created the database. Only needs to be called once.
    with sqlite3.connect('COMPANY.db') as connection:
        c = connection.cursor()
        #c.execute("CREATE TABLE FileHistory(timeStamp DATETIME)")
        c.execute("INSERT INTO FileHistory VALUES (datetime('now','localtime'))")
        

if __name__ == '__main__': #swap out whats commented to create the database.
    app = wx.App()
    frame = DemoFrame(None, title="Micro App")
    frame.Show()
    app.MainLoop()
    #createDatabase()
    
