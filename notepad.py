import os
import shlex
from tkinter import Tk
import wx
import PySimpleGUI as sg
import string
import variables as vr
import re
# initialize the tkinter framework and call the withdraw() API
# to ensure the blank Tkinter root dialog does not popup at runtime.


vr.lettersUPPER = list(string.ascii_uppercase)
addLetter = []
for letter in vr.lettersUPPER:
    new_letter_double = letter+letter
    addLetter.append(new_letter_double)
vr.lettersUPPER += addLetter
print(vr.lettersUPPER)

tk = Tk()
tk.withdraw()

wx_app = [] # pylint: disable=unused-variable
wx_app = wx.App(None)

# get the current working directory.
CURRENT_WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
APPLICATION_ICON = CURRENT_WORKING_DIRECTORY + '\\notepad.ico'

# toggle the status bar.
STATUS_BAR_SWITCH = False

# change the default theme.
sg.theme('DarkBlue17')

WINDOW_WIDTH: int = 70
WINDOW_HEIGHT: int = 25
FILE_NAME: str = None
DEFAULT_FONT_NAME: str = 'Times New Roman'
APP_NAME: str = 'JavaConverterPad'
SELECTED_THEME: str = ''
text_to_save: str = ''
selected_text: str = ''
# this is needed to control the displaying of the user prompt while closing.
# If the user closes the document just before closing the document,
# we do not want to display the prompt for save changes.
text_last_saved_manually: str = ''

Line: int = 1
Column: int = 1


# initialize the print data and set some default values
pdata = wx.PrintData()
pdata.SetPaperId(wx.PAPER_A3)
pdata.SetOrientation(wx.PORTRAIT)
margins = (wx.Point(15, 15), wx.Point(15, 15))

def ShowFontDialog():
    '''Get a font dialog to display and return all the
    font settings chosen to be applied to the editor.'''

    # the font styles supported by PySimpleGUI are mentioned
    # bold, italic, underline, and overstrike. These styles can be specified as a
    # string like - 'overstrike underline italic'

    font_style_modifier: str = ''

    dialog = wx.FontDialog(None, wx.FontData())
    if dialog.ShowModal() == wx.ID_OK:
        data = dialog.GetFontData()
        font = data.GetChosenFont()

        # extract the seletec settings in the dialog
        # to construct the font style modifiers.
        font_info = font.GetNativeFontInfoUserDesc()
        selected_styles = shlex.split(font_info)

        # font bold.
        if 'bold' in selected_styles:
            font_style_modifier += 'bold '

        # font italic.
        if 'italic' in selected_styles:
            font_style_modifier += 'italic '

        # font underline.
        if font.GetUnderlined():
            font_style_modifier += 'underline '

        # font strikethrough/overstrike.
        if font.GetStrikethrough():
            font_style_modifier += 'overstrike '

        # get the selected font/text color.
        font_color = data.GetColour()
        font_color = rgb2hex(font_color[0], font_color[1], font_color[2])

        # get the selected font name and size.
        font_facename = font.GetFaceName()
        font_size = font.GetPointSize()

        # update the font as per the above settings.
        WINDOW['-BODY-'].update(font=(font_facename, font_size, font_style_modifier.rstrip()),
                                text_color=font_color)

def ShowPrintDialog():
    '''Displays the System print dialog.'''
    data = wx.PrintDialogData()
    data.EnableSelection(True)
    data.EnablePrintToFile(True)
    data.EnablePageNumbers(True)
    data.SetMinPage(1)
    data.SetMaxPage(10)

    text_to_print = VALUES['-BODY-']
    # lines_to_print = text_to_print.split('\n')

    dialog = wx.PrintDialog(None, data)
    if dialog.ShowModal() == wx.ID_OK:
        data = dialog.GetPrintDialogData()
        data.GetPrintData().SetPaperId(wx.PAPER_A3)

        dc = dialog.GetPrintDC()
        dc.StartDoc("MyDoc")
        dc.StartPage()
        dc.SetMapMode(wx.MM_POINTS)

        dc.SetTextForeground("black")
        dc.DrawText(text_to_print, margins[0][0], margins[1][0])

        dc.EndPage()
        dc.EndDoc()
        del dc

        # printer = wx.Printer(data)
        dialog.Destroy()

def ShowPageSetupDialog():
    '''display the page setup dialog.'''
    global pdata
    global margins
    data = wx.PageSetupDialogData()
    data.SetPrintData(pdata)

    data.SetDefaultMinMargins(True)
    data.SetMarginTopLeft(margins[0])
    data.SetMarginBottomRight(margins[1])

    dlg = wx.PageSetupDialog(None, data)
    if dlg.ShowModal() == wx.ID_OK:
        data = dlg.GetPageSetupData()
        pdata = wx.PrintData(data.GetPrintData()) # force a copy
        pdata.SetPaperId(data.GetPaperId())
        margins = (data.GetMarginTopLeft(), data.GetMarginBottomRight())

    dlg.Destroy()

def rgb2hex(r, g, b):
    '''Convert RGB to hex values.'''
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

# file menu constants.
file_new: str = 'New              CTRL+N'
file_open: str = 'Open            CTRL+O'
file_save: str = 'Save              CTRL+S'
file_print: str = 'Print              CTRL+P'

# edit menu constants.
edit_cut: str = 'Cut                   CTRL+X'
edit_copy: str = 'Copy                CTRL+C'
edit_paste: str = 'Paste                CTRL+V'
edit_delete: str = 'Delete              Del'

#Binary files saving 
file_new_binary: str = 'New Binary             CTRL+H'
file_open_binary: str = 'Open Binary            CTRL+J'
file_save_binary: str = 'Save Binary             CTRL+K'

hide_status_menu_layout: list = [['&File', [file_new, file_open, file_save, file_new_binary, file_open_binary, file_save_binary,'Save As','Save As Binary', '______________________', 'Page Setup', file_print, '______________________', 'Exit']],
                    ['&Edit', [edit_cut, edit_copy, edit_paste, edit_delete]],
                    ['&Statistics', ['Word Count', 'Line Count', 'Character With Spaces', 'Character Without Spaces', ]],
                    ['F&ormat', ['Font', ]],
                    ['&View', ['Hide Status Bar', ]],
                    ['&Help', ['About']]]

show_status_menu_layout: list = [['&File', [file_new, file_open, file_save, 'Save As', '______________________', 'Page Setup', file_print, '______________________', 'Exit']],
                    ['&Edit', [edit_cut, edit_copy, edit_paste, edit_delete]],
                    ['&Statistics', ['Word Count', 'Line Count', 'Character With Spaces', 'Character Without Spaces', ]],
                    ['F&ormat', ['Font', ]],
                    ['&View', ['Show Status Bar', ]],
                    ['&Help', ['About']]]



# Define and Create the menu layouts independently so as to
# toggle between Show/Hide the applicationstatus bar.
WINDOW_MENU = sg.Menu(hide_status_menu_layout)

layout: list = [[WINDOW_MENU],
                [sg.Text('New File:', font=('Times New Roman', 10),
                         size=(WINDOW_WIDTH, 1), key='-FILE_INFO-', visible=False)],
                [sg.Multiline(font=(DEFAULT_FONT_NAME, 12),
                              size=(WINDOW_WIDTH, WINDOW_HEIGHT),
                              key='-BODY-', reroute_cprint=True, enable_events=True)],
                [sg.StatusBar(text=f'| Ln {Line}, Col {Column}', size=(WINDOW_WIDTH, 1),
                              pad=(0, 0), text_color='white', relief=sg.RELIEF_FLAT,
                              justification='right', visible=True, key='status_bar')],
                
                [sg.Column([[sg.Button(button_text='CONVERT JAVA CODE TO BYTECODE',key="-CONVERT-BUTTON-",size=(20,5))]], vertical_alignment='center', justification='center')],
            
                
                [sg.Text('New File:', font=('Times New Roman', 10),
                         size=(WINDOW_WIDTH, 1), key='-FILE_INFO_SECOND-', visible=False)],
                [sg.Multiline(font=(DEFAULT_FONT_NAME, 12),
                              size=(WINDOW_WIDTH, WINDOW_HEIGHT),
                              key='-BODY-SECOND-', reroute_cprint=False, enable_events=True)],
            ]

WINDOW = sg.Window('untitled - ' + APP_NAME, layout=layout, margins=(0, 0),
                   resizable=True, return_keyboard_events=True,
                   icon=APPLICATION_ICON, finalize=True)

# redefine the callback for window close button by using tkinter code.
# this is required to delay the event of closing the main window incase
# the text is not saved before closing.

WINDOW.TKroot.protocol("WM_DESTROY_WINDOW", lambda:WINDOW.write_event_value("WIN_CLOSE", ()))
WINDOW.TKroot.protocol("WM_DELETE_WINDOW",  lambda:WINDOW.write_event_value("WIN_CLOSE", ()))

WINDOW.read(timeout=1)
WINDOW.maximize()
WINDOW['status_bar'].ParentRowFrame.pack(fill='x')
WINDOW['-BODY-'].expand(expand_x=True, expand_y=True)
WINDOW['-BODY-SECOND-'].expand(expand_x=True, expand_y=True)
def new_file() -> str:
    ''' Reset body and info bar, and clear FILE_NAME variable '''

    global text_last_saved_manually
    global text_to_save

    fname = WINDOW['-FILE_INFO-'].DisplayText

    save_current_file = SaveBeforeClose(fname)

    if save_current_file == 'Yes':
        save_file(fname)
    elif save_current_file == 'No':
        pass

    WINDOW['-BODY-'].update(value='')
    WINDOW['-FILE_INFO-'].update(value='New File:')
    WINDOW.set_title('untitled - ' + APP_NAME)
    text_last_saved_manually = ''
    text_to_save = ''
    
def new_file_binary() -> str:
    ''' Reset body and info bar, and clear FILE_NAME variable '''

    global text_last_saved_manually
    global text_to_save

    fname = WINDOW['-FILE_INFO_SECOND-'].DisplayText

    save_current_file = SaveBeforeClose(fname)

    if save_current_file == 'Yes':
        save_file(fname)
    elif save_current_file == 'No':
        pass

    WINDOW['-BODY-SECOND-'].update(value='')
    WINDOW['-FILE_INFO_SECOND-'].update(value='New File:')
    WINDOW.set_title('untitled - ' + APP_NAME)
    text_last_saved_manually = ''
    text_to_save = ''

def open_file() -> str:
    ''' Open file and update the infobar.'''

    global text_last_saved_manually
    fname = WINDOW['-FILE_INFO-'].DisplayText

    save_current_file = SaveBeforeClose(fname)

    if save_current_file == 'Yes':
        save_file(fname)
    elif save_current_file == 'No':
        pass

    WINDOW['-BODY-'].update(value='')

    try:
        file_name = sg.popup_get_file('Open File', no_window=True)
    except: # pylint: disable=bare-except
        return ''
    if file_name not in (None, '') and not isinstance(file_name, tuple):
        with open(file_name, 'r') as f:
            WINDOW['-BODY-'].update(value=f.read())
        WINDOW['-FILE_INFO-'].update(value=file_name)
    
    WINDOW.set_title(file_name + ' - ' + APP_NAME)
    text_last_saved_manually = VALUES.get('-BODY-')
    return file_name

def open_file_binary() -> str:
    ''' Open file and update the infobar.'''

    global text_last_saved_manually
    fname = WINDOW['-FILE_INFO_SECOND-'].DisplayText


    WINDOW['-BODY-SECOND-'].update(value='')

    try:
        file_name = sg.popup_get_file('Open File', no_window=True)
    except: # pylint: disable=bare-except
        return ''
    if file_name not in (None, '') and not isinstance(file_name, tuple):
        with open(file_name, 'r') as f:
            WINDOW['-BODY-SECOND-'].update(value=f.read())
        WINDOW['-FILE_INFO_SECOND-'].update(value=file_name)
    
    WINDOW.set_title(file_name + ' - ' + APP_NAME)
    text_last_saved_manually = VALUES.get('-BODY-SECOND-')
    return file_name

def save_file(file_name: str):
    ''' Save file instantly if already open; otherwise display `save-as` popup '''
    global text_last_saved_manually
    # Get the filename if already saved in the same session.
    file_name = WINDOW['-FILE_INFO-'].DisplayText
    if file_name not in (None, '', 'New File:'):
        with open(file_name, 'w') as f:
            if VALUES is not None:
                f.write(VALUES.get('-BODY-'))
                WINDOW['-FILE_INFO-'].update(value=file_name)
            else:
                f.write(text_to_save)

            # this is needed to control the displaying of the user prompt while closing.
            # If the user closes the document just before closing the document,
            # we do not want to display the prompt for save changes.
            text_last_saved_manually = text_to_save
    else:
        file_name = save_as()

def save_file_binary(file_name: str):
    ''' Save file instantly if already open; otherwise display `save-as` popup '''
    global text_last_saved_manually
    # Get the filename if already saved in the same session.
    file_name = WINDOW['-FILE_INFO_SECOND-'].DisplayText
    if file_name not in (None, '', 'New File:'):
        with open(file_name, 'w') as f:
            if VALUES is not None:
                f.write(VALUES.get('-BODY-SECOND-'))
                WINDOW['-FILE_INFO_SECOND-'].update(value=file_name)
            else:
                f.write(text_to_save)

            # this is needed to control the displaying of the user prompt while closing.
            # If the user closes the document just before closing the document,
            # we do not want to display the prompt for save changes.
            text_last_saved_manually = text_to_save
    else:
        file_name = save_as_binary()

    # We will skip this line while closing the dialog.
    if VALUES is not None:
        WINDOW.set_title(file_name + ' - ' + APP_NAME)

def save_as_binary() -> str:
    ''' Save new file or save existing file with another name '''
    global text_last_saved_manually
    try:
        file_name: str = sg.popup_get_file('Save As', save_as=True, no_window=True,
                                           file_types=(('Text Documents', '*.class'), ('ALL Files', '*.*'),),
                                           modal=True, default_path="*.class",
                                           icon=APPLICATION_ICON)
    except: # pylint: disable=bare-except
        return ''
    if file_name not in (None, ''):
        with open(file_name, 'w') as f:
            if VALUES is not None:
                f.write(VALUES.get('-BODY-SECOND-'))
                WINDOW['-FILE_INFO_SECOND-'].update(value=file_name)
            else:
                f.write(text_to_save)
        # this is needed to control the displaying of the user prompt while closing.
        # If the user closes the document just before closing the document,
        # we do not want to display the prompt for save changes.
        text_last_saved_manually = text_to_save
    return file_name

def save_as() -> str:
    ''' Save new file or save existing file with another name '''
    global text_last_saved_manually
    try:
        file_name: str = sg.popup_get_file('Save As', save_as=True, no_window=True,
                                           file_types=(('Text Documents', '*.txt'), ('ALL Files', '*.*'),),
                                           modal=True, default_path="*.txt",
                                           icon=APPLICATION_ICON)
    except: # pylint: disable=bare-except
        return ''
    if file_name not in (None, ''):
        with open(file_name, 'w') as f:
            if VALUES is not None:
                f.write(VALUES.get('-BODY-'))
                WINDOW['-FILE_INFO-'].update(value=file_name)
            else:
                f.write(text_to_save)
        # this is needed to control the displaying of the user prompt while closing.
        # If the user closes the document just before closing the document,
        # we do not want to display the prompt for save changes.
        text_last_saved_manually = text_to_save
    return file_name

def get_word_count():
    ''' Get the estimated word count '''
    total_words: int = 0
    if not validate_text():
        ShowMessageBox(title='JavaConverter Statistics',
                       message='Text Not Found.\nEnter some text to calculate the number of words.')
        return 0

    lines: list = VALUES['-BODY-'].splitlines()
    for line in lines:
        words = line.split()
        total_words += len(words)

    return total_words

def validate_text() -> bool:
    '''validates if the user has entered some text in the note body
    and returns True/False accordingly.'''

    user_text: str = VALUES['-BODY-']
    if user_text == '\n':
        return False
    else:
        return True

def character_count():
    '''Get the total number of characters in the file.'''

    if not validate_text():
        ShowMessageBox(title='JavaConverter+ Statistics',
                       message='Text Not Found.\nEnter some text to calculate the number of words.')
        return 0

    chars = len(VALUES['-BODY-']) - 1
    return chars

def characters_without_spaces():
    '''Get the total number of characters in the file.'''

    if not validate_text():
        ShowMessageBox(title='JavaConverter Statistics',
                       message='Text Not Found.\nEnter some text to calculate the number of words.')
        return 0

    chars_without_spaces: int = 0
    # total number of spaces is 1 less than the number of words.
    total_spaces: int = get_word_count() - 1

    if total_spaces == -1:
        chars_without_spaces = character_count()
    else:
        chars_without_spaces = character_count() - total_spaces

    return chars_without_spaces

def get_line_count():
    ''' Get the estimated line count '''

    if not validate_text():
        ShowMessageBox(title='JavaConverter Statistics',
                       message='Text Not Found.\nEnter some text to calculate the number of words.')
        return 0

    text: str = VALUES['-BODY-']
    
    # extract the lines in the editor body. '\n' is the line separator
    # so we use it to split the text. The last line ends with '\n' which
    # includes an extra empty string ('') entry adding +1 to the total lines.
    # so we strip the last new line ('\n') character.
    lines: list = [line for line in text.rstrip('\n').split('\n')]
    # lines: list = text.splitlines() # can also be used.
    line_count: int = len(lines)
    return line_count

def ShowMessageBox(title: str, message: str):
    '''Reusable function to show user popup.'''
    sg.PopupQuick(message, title=title, auto_close=False,
                  modal=True, icon=APPLICATION_ICON)

def AboutNotepadPyPlus():
    '''About the application'''

    ShowMessageBox(title='About JavaConverter+',
                   message='A simple JavaConverter like application created using PySimpleGUI framework.')

def SaveBeforeClose(fname: str):
    '''Save before close if the user wants to save
    the documentbefore closing the application.'''

    save_before_close: str = 'No'
    if fname not in (None, '') and \
        text_to_save.rstrip() != '' and \
        text_last_saved_manually != text_to_save:
        # display a user prompt incase the note is not yet saved asking the
        # user 'Do you want to save changes to Untitled?'
        user_prompt_msg: str = ''
        if fname == 'New File:':
            user_prompt_msg = 'Untitled'
        else:
            user_prompt_msg = fname

        save_before_close = sg.popup_yes_no('Do you want to save changes to ' +
                                            user_prompt_msg + "?",
                                            title='JavaConverter', modal=True,
                                            icon=APPLICATION_ICON)

    return save_before_close

def integerParse(words):
    contains = False
    if(len(words) < 2):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the integer value parsing ::: at line " + str(vr.line)+ "\n";
        return;
    elif(len(words) == 2):
        newList = words[1].split("=")
        newList.append(newList[1])
        newList[1] = "=";
        print(newList)
        words.pop()
        for item in newList:
            words.append(item)
        print(words)
    if(len(words) < 4):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the integer value parsing ::: at line " + str(vr.line)+ "\n";
        return;
    deklaracja = ''
    przypisanie = 'ISTORE '+ words[1];
    removetable = str.maketrans('', '', '@#%;!+-,&*^$_')
    words_cleared = [s.translate(removetable) for s in words]
    contains = False
   
    if(not intTryParse(words_cleared[3])):
        return;
    
        
        
    for character in words_cleared [2]:
        if character == '=':
            contains = True
    if(not contains):
        return;
    
    if(int(words_cleared [3]) >= 2 and int(words_cleared [3]) <= 5):
        deklaracja = 'ICONST_'+words_cleared [3];
    else:
        deklaracja = 'BIPUSH '+ words_cleared [3];
    vr.middle += "\n"+deklaracja+"\n"+przypisanie+"\n";
    vr.integersDiciontary[words[1]] = words_cleared [3];

def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the int value parsing ::: at line " + str(vr.line)+"\nProgram exit with status 0";
        
        vr.errorOccured = True
        return False
    
    
def floatTryParse(value):
    try:
        return float(value), True
    except ValueError:
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the value parsing ::: at line " + str(vr.line)+ "\nCheck for additional symbols in number\n Might contains '.' example: '3.14' \n \nProgram exit with status 0";
        
        vr.errorOccured = True
        return False
        

def floatParse(words):
    contains = False
    if(len(words) < 2):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the float value parsing ::: at line " + str(vr.line)+ "\n";
        return;
    elif(len(words) == 2):
        newList = words[1].split("=")
        newList.append(newList[1])
        newList[1] = "=";
        print(newList)
        words.pop()
        for item in newList:
            words.append(item)
        print(words)
    if(len(words) < 4):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the float value parsing ::: at line " + str(vr.line)+ "\n";
        return;
    deklaracja = ''
    przypisanie = 'FSTORE '+ words[1];
    removetable = str.maketrans('', '', '@#%;!+-,&*^$_')
    words_cleared = [s.translate(removetable) for s in words]
    contains = False
    for character in words_cleared[2]:
        if character == '=':
            contains = True
    if(not contains):
        return;
    if(not floatTryParse(words_cleared[3])):
        return;
    
    deklaracja = 'LDC '+ words_cleared[3]+"F";
    vr.middle += "\n"+deklaracja+"\n"+przypisanie+"\n";
    vr.floatsDictionary[words[1]] = words_cleared [3]
        
def doubleParse(words):
    contains = False
    if(len(words) < 2):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the double value parsing ::: at line " + str(vr.line)+ "\n";
        return;
    elif(len(words) == 2):
        newList = words[1].split("=")
        newList.append(newList[1])
        newList[1] = "=";
        print(newList)
        words.pop()
        for item in newList:
            words.append(item)
        print(words)
    if(len(words) < 4):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the double value parsing ::: at line " + str(vr.line)+ "\n";
        return;
    deklaracja = ''
    przypisanie = 'DSTORE '+ words[1];
    removetable = str.maketrans('', '', '@#%;!+-,&*^$_')
    words_cleared = [s.translate(removetable) for s in words]
    contains = False
    for character in words_cleared[2]:
        if character == '=':
            contains = True
    if(not contains):
        return;
    if(not floatTryParse(words_cleared[3])):
        return;
    
    deklaracja = 'LDC '+ words_cleared[3]+"D";
    vr.middle += "\n"+deklaracja+"\n"+przypisanie+"\n";
    vr.doublesDiciontary[words[1]] = words_cleared [3];
    
def stringParse(words):
    contains = False
    if(len(words) < 2):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the string value parsing ::: at line " + str(vr.line)+ "\n";
        return;
    elif(len(words) == 2):
        newList = words[1].split("=")
        newList.append(newList[1])
        newList[1] = "=";
        print(newList)
        words.pop()
        for item in newList:
            words.append(item)
        print(words)
    if(len(words) < 4):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the string value parsing ::: at line " + str(vr.line)+ "\n";
        return;
    deklaracja = ''
    przypisanie = 'ASTORE '+ words[1];
    removetable = str.maketrans('', '', ';')
    words_cleared = [s.translate(removetable) for s in words[len(words)-1]]
    print(len(words))
    if(len(words) <= 2):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the string value parsing ::: at line " + str(vr.line)+"\nString format incorrect\nExpected format: String NAME = \"VALUE\"\nProgram exit with status 0";
        vr.errorOccured = True;
        return;
    clearvalue = ' '
    for x in words_cleared:
        clearvalue += ''+ x
    words[len(words)-1] = clearvalue
    contains = False
    for character in words[2]:
        if character == '=':
            contains = True
    if(not contains):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the string value parsing ::: at line " + str(vr.line)+"\nProgram exit with status 0";
        vr.errorOccured = True;
        return;
    contains = False
    print(len(words))
    if(len(words) == 4):
        words[3] = " ".join(str(words[3]).split())
        if words[3].startswith("\"") and words[3].endswith("\""):
            contains = True
        if(not contains):
                vr.start = ""
                vr.middle = "------ERROR------\nError occured in the string value parsing ::: at line " + str(vr.line)+"\nProgram exit with status 0";
                vr.errorOccured = True;
                return;
        contains = False
        clearvalue = words[3]
        deklaracja = 'LDC '+clearvalue+"";
        vr.middle += "\n"+deklaracja+"\n"+przypisanie+"\n";
    elif len(words) > 4:
        for character in words[3]:
            if character == '"':
                contains = True
        if(not contains):
                vr.start = ""
                vr.middle = "------ERROR------\nError occured in the string value parsing ::: at line " + str(vr.line)+"\nProgram exit with status 0";
                vr.errorOccured = True;
                return;
        contains = False
        stringValue = "" + str(words[3])
        for word in words[4::]:
            stringValue += str(word)
            for character in word:
                if character == '"':
                    contains = True;
                    break;
        if(not contains):
            vr.start = ""
            vr.middle = "------ERROR------\nError occured in the string value parsing ::: at line " + str(vr.line)+"\nProgram exit with status 0";
            vr.errorOccured = True;
            return
        clearvalue = ' '
        for x in stringValue:
            clearvalue += ' '+ x
        deklaracja = 'LDC '+clearvalue+"";
        vr.middle += "\n"+deklaracja+"\n"+przypisanie+"\n";
    else: 
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the string value parsing ::: at line " + str(vr.line)+"\nString format incorrect\nExpected format: String NAME = \"VALUE\"\nProgram exit with status 0";
        vr.errorOccured = True;
def charParse(words):
    contains = False
    if(len(words) < 2):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the char value parsing ::: at line " + str(vr.line)+ "\nCheck for additional symbols and number\n Example of using: 'char 'NAME' = 'VALUE'; \n \nProgram exit with status 0";
        return;
    elif(len(words) == 2):
        newList = words[1].split("=")
        newList.append(newList[1])
        newList[1] = "=";
        print(newList)
        words.pop()
        for item in newList:
            words.append(item)
        print(words)
    if(len(words) < 4):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the char value parsing ::: at line " + str(vr.line)+ "\nCheck for additional symbols and number\n Example of using: 'char 'NAME' = 'VALUE'; \n \nProgram exit with status 0";
        return;
    if words[3].startswith("\"") and words[3].endswith("\";"):
            contains = True
    if(not contains):
            vr.start = ""
            vr.middle = "------ERROR------\nError occured in the char value parsing ::: at line " + str(vr.line)+"\nProgram exit with status 0";
            vr.errorOccured = True;
            return;
    deklaracja = ''
    przypisanie = 'ISTORE '+ words[1];
    removetable = str.maketrans('', '', '";')
    words_cleared = [s.translate(removetable) for s in words]
    clearvalue = ''
    for x in words_cleared:
        clearvalue += ''+ x
    words[len(words)-1] = clearvalue
    contains = False
    if(len(words_cleared) < 4):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the char value parsing ::: at line " + str(vr.line)+"\nProgram exit with status 0";
        vr.errorOccured = True;
        return;
    print(words_cleared)
    for character in words_cleared[2]:
        if character == '=':
            contains = True
            break;
    if(not contains):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the char value parsing ::: at line " + str(vr.line)+"\nProgram exit with status 0";
        vr.errorOccured = True;
        return;
    print(words_cleared[3])
    if(int(ord(words_cleared [3])) >= 0 and int(ord(words_cleared [3])) <= 127):
        deklaracja = 'BIPUSH_'+str(ord(words_cleared [3]));
    vr.middle += "\n"+deklaracja+"\n"+przypisanie+"\n";   

def boolParse(words):
    if(len(words) < 2):
        return;
    elif(len(words) == 2):
        newList = words[1].split("=")
        newList.append(newList[1])
        newList[1] = "=";
        print(newList)
        words.pop()
        for item in newList:
            words.append(item)
        print(words)
    if(len(words) < 4):
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the boolean value parsing ::: at line " + str(vr.line)+ "\nCheck for additional symbols and numbers exception\n Example of using: 'bool 'NAME' = true/false; \n \nProgram exit with status 0";
        return;
    deklaracja = ''
    przypisanie = 'ISTORE '+ words[1];
    removetable = str.maketrans('', '', '@#%;!+-,&*^$_')
    words_cleared = [s.translate(removetable) for s in words]
    contains = False
    for character in words_cleared [2]:
        
        if character == '=':
            contains = True
    if(not contains):
        return;
    if('false' in words_cleared[3]):
        deklaracja = 'ICONST_0';
    elif('true' in words_cleared[3]):
        deklaracja = 'ICONST_1';
    else:
        vr.start = ""
        vr.middle = "------ERROR------\nError occured in the boolean value parsing ::: at line " + str(vr.line)+ "\nCheck for additional symbols in number\n Example of using: 'bool 'NAME' = true/false; \n \nProgram exit with status 0";
        
        vr.errorOccured = True
        return
    vr.middle += "\n"+deklaracja+"\n"+przypisanie+"\n";
    
def forParser(words):
    if(words[2] == 'int'):
        integerParse(words[2::])
        dodajEtykiete()
        vr.middle += "\nILOAD "+words[3]+"\n";   
        vr.typeOfVariableFor = 'int'
        
    elif words[2] == 'float':
        floatParse(words[2::])
        dodajEtykiete()
        vr.middle += "\nFLOAD "+words[3]+"\n";  
        vr.typeOfVariableFor = 'float'
        
    elif words[2] == 'double':
        doubleParse(words[2::])
        dodajEtykiete()
        vr.middle += "\nDLOAD "+words[3]+"\n";  
        vr.typeOfVariableFor = 'double'
        
    else:
        return;
    if('<' in words):
        vr.middle += "IFGE "+vr.lettersUPPER[vr.letter_index+3]+"\n";  
    elif('<=' in words):
        vr.middle += "IFGT "+vr.lettersUPPER[vr.letter_index+3]+"\n";  
    elif('>=' in words):
        vr.middle += "IFLT "+vr.lettersUPPER[vr.letter_index+3]+"\n";  
    elif('>' in words):    
        vr.middle += "IFLE "+vr.lettersUPPER[vr.letter_index+3]+"\n"; 
    elif('==' in words):
        vr.middle += "IFNE "+vr.lettersUPPER[vr.letter_index+3]+"\n";
    elif('!=' in words):
        vr.middle += "IFEQ "+vr.lettersUPPER[vr.letter_index+3]+"\n";
        
    
    vr.forVariable.append(words[9])
    vr.forVariable.append(words[10])
    vr.forVariable.append(words[11])
    

        
    
    
def ConvertStart():
    lines: list = VALUES['-BODY-'].splitlines()
   
    WINDOW['-BODY-SECOND-'].update('')
   
    vr.start = "\nDEFINE PUBLIC STATIC main([Ljava/lang/String; args)V\n"+vr.lettersUPPER[vr.letter_index]+":\nLINE "+vr.lettersUPPER[vr.letter_index]+" "+str(vr.lineID)+"\n";
    
    vr.middle = ''
    for line in lines:
        if(vr.errorOccured):
            break
        vr.line += 1;
        words = line.split()
        LineConvert(words)
        
        print(words)

    
    if( vr.errorOccured):
        vr.end = "";
    else:
        vr.end = "\nRETURN\n"+vr.lettersUPPER[vr.letter_index+1]+":";
    WINDOW['-BODY-SECOND-'].update(value = (vr.start+vr.middle+vr.end))
def LineConvert(words):
    print(words)
    if(len(words) == 0):
        return;
    vr.lineID += 1
    if(vr.letter_index+1 == len(vr.lettersUPPER)):
        AddNumbers()
        

         
    if '{'  in words:
        vr.flaga = True
        vr.idTab = vr.letter_index
        print('I found { ')
        if('for' in words and '(' in words and ')' in words):
            print('Parse for')
            forParser(words)
            vr.flagaFor = True;
        
    if '{' not in words:
        if(not vr.flaga):
            vr.letter_index += 1        
            vr.middle += "\n"+vr.lettersUPPER[vr.letter_index]+":\n"
            vr.middle += "\nLINE "+vr.lettersUPPER[vr.letter_index]+" "+str(vr.lineID)
    if '}' in words and vr.flagaFor:
        vr.letter_index += 1  
        vr.middle += "\n"+vr.lettersUPPER[vr.letter_index]+":\n"
        vr.middle += "\nLINE "+vr.lettersUPPER[vr.letter_index]+" "+str(vr.lineID)+"\n"
        print(vr.forVariable[1] )
        if(vr.forVariable[1] == '++' ):
            if(vr.typeOfVariableFor == 'int'):
                vr.middle += "IINC "+vr.forVariable[0]+" 1\n"
            elif(vr.typeOfVariableFor == 'double'):
                vr.middle += "FINC "+vr.forVariable[0]+" 1\n"
            elif(vr.typeOfVariableFor == 'float'):
                vr.middle += "DINC "+vr.forVariable[0]+" 1\n"
        elif(vr.forVariable[1] == '--' ):
            if(vr.typeOfVariableFor == 'int'):
                vr.middle += "IDEC "+vr.forVariable[0]+" 1\n"
            elif(vr.typeOfVariableFor == 'double'):
                vr.middle += "FDEC "+vr.forVariable[0]+" 1\n"
            elif(vr.typeOfVariableFor == 'float'):
                vr.middle += "DDEC "+vr.forVariable[0]+" 1\n"
        elif(vr.forVariable[1] == '+' ):
            if(vr.typeOfVariableFor == 'int'):
                vr.middle += "IINC "+vr.forVariable[0]+ " "+ vr.forVariable[2]+ "\n"
            elif(vr.typeOfVariableFor == 'double'):
                vr.middle += "DINC "+vr.forVariable[0]+ " "+ vr.forVariable[2]+ "\n"
            elif(vr.typeOfVariableFor == 'float'):
                vr.middle += "FINC "+vr.forVariable[0]+ " "+ vr.forVariable[2]+ "\n"
        elif(vr.forVariable[1] == '-' ):
            if(vr.typeOfVariableFor == 'int'):
                vr.middle += "IDEC "+vr.forVariable[0]+ " "+ vr.forVariable[2]+ "\n"
            elif(vr.typeOfVariableFor == 'double'):
                vr.middle += "DDEC "+vr.forVariable[0]+ " "+ vr.forVariable[2]+ "\n"
            elif(vr.typeOfVariableFor == 'float'):
                vr.middle += "FDEC "+vr.forVariable[0]+ " "+ vr.forVariable[2]+ "\n"
        vr.middle += "GOTO "+vr.lettersUPPER[vr.letter_index-1]+"\n"
        vr.flagaFor = False;
        
        
    if '}' in words:
        vr.flaga = False
        vr.middle += "\nLINE "+vr.lettersUPPER[vr.idTab]+" "+str(vr.lineID)
    if("System.out.print(" in words):
        if( '"' not in words[1]):
            dodajEtykiete()
            dodajLinie()
            vr.middle += "\nGETSTATIC java/lang/System.out Ljava/io/PrintStream;\nILOAD "+words[1]+"\nINVOKEVIRTUAL java/io/PrintStream.print(I)V"
        else:
            dodajEtykiete()
            dodajLinie()
            vr.middle += "\nGETSTATIC java/lang/System.out Ljava/io/PrintStream;\nLDC "+words[1]+"\nINVOKEVIRTUAL java/io/PrintStream.print(Ljava/lang/String;)V"
        
    if("System.out.println(" in words):
        if( '"' not in words[1]):
            dodajEtykiete()
            dodajLinie()
            vr.middle += "\nGETSTATIC java/lang/System.out Ljava/io/PrintStream;\nILOAD "+words[1]+"\nINVOKEVIRTUAL java/io/PrintStream.print(I)V"
        else:
            dodajEtykiete()
            dodajLinie()
            vr.middle += "\nGETSTATIC java/lang/System.out Ljava/io/PrintStream;\nLDC "+words[1]+"\nINVOKEVIRTUAL java/io/PrintStream.printlnLjava/lang/String;)V"
            
    for x in words:
        if( x in vr.integersDiciontary):
            variableIntegerOperations(x,words)
            break;
        elif( x in vr.floatsDictionary):
            variableFloatsOperations(x,words)
            break;
        elif( x in vr.doublesDiciontary):
            variableDoublesOperations(x,words)
            break;
        elif(x in vr.integerTabsDictionary):
            variableIntegerTabOperations(x,words)
            break;
        
        
    
    if(words[0] == 'int[]'):
        tabIntParse(words)
    elif(words[0] == 'int'):
        if(len(words) <= 2):
            integerParse(words)
            return
        removetable = str.maketrans('', '', '()1234567890;')
        words_cleared = [s.translate(removetable) for s in words]
        words_cleared[3] = words_cleared[3].replace(".nextInt","")
        print(words_cleared)
        for x in words_cleared:
            if( x in vr.randomsDictionary):
                randomOperations(words[1],words,x)
                break;
        else:
            integerParse(words)
    elif words[0] == 'float':
        floatParse(words)
    elif words[0] == 'double':
        doubleParse(words)
    elif words[0] == 'String':
        stringParse(words)
    elif words[0] == 'char':
        charParse(words)
    elif words[0] == 'bool':
        boolParse(words)
    elif words[0] == 'Random':
        randomParse(words)
    
    
    
    print('')

def randomParse(words):
    if(not("Random" in words and "new" in words and "Random();" in words)):
        vr.errorOccured = True;
        vr.middle = "__ERROR__\n Random function initializing\n" 
        return;
    else:
        dodajEtykiete()
        dodajLinie()
        vr.middle += "\nNEW java/util/Random\nDUP\nINVOKESPECIAL java/util/Random.<init>()V\nASTORE "+words[1];
        vr.randomsDictionary[words[1]] = ''
        
def randomOperations(variable, words,randomVariable):
    words_cleared =  re.sub("[^0-9]", "", words[3])
    print(str(words_cleared))
    vr.middle += "\nALOAD "+str(randomVariable)+"\nBIPUSH "+words_cleared+"\nINVOKEVIRTUAL java/util/Random.nextInt(I)I\nISTORE "+variable+"\n"
    
def tabIntParse(words):
    removetable = str.maketrans('', '', '@#;!,&^$_newint[]abcdefghijklmnoprstuvwx')
    words_cleared = [s.translate(removetable) for s in words]
    contains = False
    for character in words_cleared [2]:
        if character == '=':
            contains = True
    if(not contains):
        return;
    print(str(words_cleared))
    vr.middle += "\nBIPUSH "+str(words_cleared [4])+"\nNEWARRAY I\nASTORE "+words[1]+"\n"
    vr.integerTabsDictionary[words[1]] = words_cleared [4];
def variableIntegerTabOperations(variable,words):
    
    start = "\nALOAD "+ variable
    usuwanie = '[];'+variable
    removetable = str.maketrans('', '', str(usuwanie))
    words_cleared = [s.translate(removetable) for s in words]
    contains = False
    for character in words_cleared:
        if character == '=':
            contains = True
    if(not contains):
        return;
   
    print(words_cleared)
    miejsce = "\nBIPUSH "+ words_cleared[1];
    dane = "\nBIPUSH "+ words_cleared[3];
    przypisanie = '\nIASTORE\n'
    vr.middle += start + miejsce + dane + przypisanie
 
def variableIntegerOperations(variable,words):
    przypisanie = 'ISTORE '+ variable;
    removetable = str.maketrans('', '', '@#;!,&^$_')
    words_cleared = [s.translate(removetable) for s in words]
    contains = False
    for character in words_cleared [1]:
        if character == '=':
            contains = True
    if(not contains):
        return;
    
    step = 1;
    operand = ''
    for word in words[2::]:
        if(step%2 == 1):
            vr.middle += "\nILOAD "+word+"\n"
        else:
            if('+' in word):
                operand = "IADD"
            elif("-" in word):
                operand = "ISUB"
            elif("*" in word):
                operand = "IMUL"
            elif("/" in word):
                operand = "IDIV"
            elif("%" in word):
                operand = "IREM"
        if(step/3 == 1):
            step = 1
            vr.middle += "\n"+operand+"\n"
        step += 1
    step = 1;
    vr.middle += "\n"+przypisanie+"\n";

    
def variableFloatsOperations(variable,words):
    przypisanie = 'ISTORE '+ variable;
    removetable = str.maketrans('', '', '@#;!,&^$_')
    words_cleared = [s.translate(removetable) for s in words]
    contains = False
    for character in words_cleared [1]:
        if character == '=':
            contains = True
    if(not contains):
        return;
    
    step = 1;
    operand = ''
    for word in words[2::]:
        if(step%2 == 1):
            vr.middle += "\nFLOAD "+word+"\n"
        else:
            if('+' in word):
                operand = "FADD"
            elif("-" in word):
                operand = "FSUB"
            elif("*" in word):
                operand = "FMUL"
            elif("/" in word):
                operand = "FDIV"
            elif("%" in word):
                operand = "FREM"
        if(step/3 == 1):
            step = 1
            vr.middle += "\n"+operand+"\n"
        step += 1
    step = 1;
    vr.middle += "\n"+przypisanie+"\n";
def variableDoublesOperations(variable,words):
    przypisanie = 'DSTORE '+ variable;
    removetable = str.maketrans('', '', '@#;!,&^$_')
    words_cleared = [s.translate(removetable) for s in words]
    contains = False
    for character in words_cleared [1]:
        if character == '=':
            contains = True
    if(not contains):
        return;
    
    step = 1;
    operand = ''
    for word in words[2::]:
        if(step%2 == 1):
            vr.middle += "\nDLOAD "+word+"\n"
        else:
            if('+' in word):
                operand = "DADD"
            elif("-" in word):
                operand = "DSUB"
            elif("*" in word):
                operand = "DMUL"
            elif("/" in word):
                operand = "DDIV"
            elif("%" in word):
                operand = "DREM"
        if(step/3 == 1):
            step = 1
            vr.middle += "\n"+operand+"\n"
        step += 1
    step = 1;
    vr.middle += "\n"+przypisanie+"\n";



    
    
def dodajEtykiete():
    vr.letter_index += 1        
    vr.middle += "\n"+vr.lettersUPPER[vr.letter_index]+":"



def dodajLinie():
    vr.middle += "\nLINE "+vr.lettersUPPER[vr.letter_index]+" "+str(vr.lineID)
# read the events and take appropriate actions.


def AddNumbers():
    addLetter = []
    for letter in vr.lettersUPPER:
        new_letter_double = letter+str(vr.added)
        addLetter.append(new_letter_double)
    vr.lettersUPPER += addLetter
    vr.added += 1
    

while True:

    EVENT, VALUES = WINDOW.read()
    
    if EVENT in (sg.WINDOW_CLOSED, 'Exit', "WIN_CLOSE"):
        # Get the filename if already saved in the same session.
        file_name = WINDOW['-FILE_INFO-'].DisplayText

        user_prompt_action = SaveBeforeClose(file_name)

        if user_prompt_action == 'Yes':
            save_file(FILE_NAME)
        elif user_prompt_action == 'No':
            break

        # finally breakout of the event loop and end the application.
        break

    # file menu events.
    if EVENT in (file_new, 'n:78'):
        new_file()
    if EVENT in (file_open, 'o:79'):
        FILE_NAME = open_file()
    if EVENT in (file_save, 's:83'):
        save_file(FILE_NAME)
    if EVENT in (file_new_binary, 'n:78'):
        new_file_binary()
    if EVENT in (file_open_binary, 'o:79'):
        FILE_NAME = open_file_binary()
    if EVENT in (file_save_binary, 's:83'):
        save_file_binary(FILE_NAME)
    if EVENT in ('Save As',):
        FILE_NAME = save_as()
    if EVENT in ('Save As Binary',):
        FILE_NAME = save_as_binary()
    if EVENT in (file_print, 'p:80'):
        ShowPrintDialog()
    if EVENT == 'Page Setup':
        ShowPageSetupDialog()

    # edit menu events.
    if EVENT == edit_cut:
        try:
            selected_text = WINDOW['-BODY-'].Widget.selection_get()
            tk.clipboard_clear()
            tk.clipboard_append(selected_text)
            tk.update()
            WINDOW['-BODY-'].Widget.delete("sel.first", "sel.last")
        except: # pylint: disable=bare-except
            selected_text = ''
            ShowMessageBox(title='Text Selection Error',
                           message='An active text selection was not found. Please select some text to cut.')

    if EVENT == edit_copy:
        try:
            selected_text = WINDOW['-BODY-'].Widget.selection_get()
            tk.clipboard_clear()
            tk.clipboard_append(selected_text)
            tk.update() # now it stays on the clipboard after the window is closed
        except: # pylint: disable=bare-except
            selected_text = ''
            ShowMessageBox(title='Text Selection Error',
                           message='An active text selection was not found. Please select some text to copy.')

    if EVENT == edit_paste:
        clip_text = tk.clipboard_get()

        try:
            selected_text = WINDOW['-BODY-'].Widget.selection_get()
        except: # pylint: disable=bare-except
            selected_text = ''

        if selected_text != '':
            WINDOW['-BODY-'].Widget.delete("sel.first", "sel.last")

        WINDOW['-BODY-'].Widget.insert("insert", clip_text)

    if EVENT == edit_delete:
        try:
            WINDOW['-BODY-'].Widget.delete("sel.first", "sel.last")
        except:
            selected_text = ''
            ShowMessageBox(title='Text Selection Error',
                           message='An active text selection was not found. Please select some text to delete.')

    if EVENT in ('Word Count',):
        WORDS = get_word_count()
        if WORDS != 0:
            ShowMessageBox(title='JavaConverter Statistics', message='Word Count: {:,d}'.format(WORDS))
    if EVENT in ('Line Count',):
        LINES = get_line_count()
        if LINES != 0:
            ShowMessageBox(title='JavaConverterStatistics', message='Line Count: {:,d}'.format(LINES))
    if EVENT in ('Character With Spaces',):
        CHARS = character_count()
        if CHARS != 0:
            ShowMessageBox(title='JavaConverter Statistics',
                           message='Characters With Spaces: {:,d}'.format(CHARS))
    if EVENT in ('Character Without Spaces',):
        CHAR_WITHOUT_SPACES = characters_without_spaces()
        if CHAR_WITHOUT_SPACES != 0:
            ShowMessageBox(title='JavaConverterStatistics',
                           message='Characters Without Spaces: {:,d}'.format(CHAR_WITHOUT_SPACES))
    if EVENT in ('About',):
        AboutNotepadPyPlus()

    # Format Menu
    if EVENT in ('Font',):
        ShowFontDialog()

    # Show/Hide Status Bar.
    if EVENT in ('Hide Status Bar', 'Show Status Bar'):
        if STATUS_BAR_SWITCH:
            WINDOW['status_bar'].ParentRowFrame.pack(fill='x')
            WINDOW['status_bar'].update(visible=True)
            WINDOW['status_bar'].Widget.pack(fill='x')

           
            # toggle effect for show/hide status bar button.
          
            WINDOW_MENU.Update(hide_status_menu_layout)
            STATUS_BAR_SWITCH = False
        else:
            WINDOW['status_bar'].update(visible=False)
            WINDOW['status_bar'].ParentRowFrame.pack_forget()

           
            # toggle effect for show/hide status bar button.
            
            WINDOW_MENU.Update(show_status_menu_layout)
            STATUS_BAR_SWITCH = True

    # Update the line and column values in the statusbar
    # with every character / escape sequences keyed-in.
    if EVENT == '-CONVERT-BUTTON-':
        WINDOW['-BODY-SECOND-'].update(value=VALUES['-BODY-'])
        vr.letter_index = 0
        vr.start = ''
        vr.middle = ''
        vr.end = ''
        vr.added = 0 
        vr.lineID = 7
        vr.flaga = False
        vr.idTab = 0
        vr.line = 0
        vr.flagaFor = False
        vr.forVariable = []
        vr.typeOfVariableFor = ''
        vr.integersDiciontary = {}
        vr.floatssDiciontary = {}
        vr.doublesDiciontary = {}
        vr.integerTabsDictionary ={}
        vr.errorOccured = False
        ConvertStart()
    if EVENT == '-BODY-':
        Line, Column = WINDOW['-BODY-'].Widget.index('insert').split('.')
        WINDOW['status_bar'].update(f'| Ln {Line}, Col {Column}')
  
    # record the text after each event to ensure the
    # file/text is saved.
    try:
        # if File -> New menu option is chosen and the new blank editor window is closed, then we do
        # not want to display the Save File prompt. Executing this block on the event of a new file
        # resets the 'text_to_save' variable to old text in the editor and 
        # causes to display the save prompt.
        if EVENT != file_new:
            text_to_save = VALUES['-BODY-']
    except: # pylint: disable=bare-except
        pass

    # Set focus to the editor.
    WINDOW.Element('-BODY-').SetFocus()

