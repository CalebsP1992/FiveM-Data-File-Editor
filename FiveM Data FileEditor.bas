'THIS SOFTWARE IS OPEN SOURCE FREEWARE'
'MODIFICATIONS TO THIS SOFTWARE IS WELCOME'
'YOU CAN MODIFY THIS TO IMPROVE IT -- AS LONG AS YOU  CREDIT ME'
'DISCORD -- https://discord.gg/prau4ysZSK --'
    'AUTHOR - PLAYDOUGH'
    'NAME -   FiveM Data File Editor'
    'SUPPORTED FILE TYPES - .lua .meta .json .txt .xml'
    'VERSION - 1.0.0'






'DEFAULT WINDOW SIZE'

    'IF YOU DONT KNOW WHAT YOURE DOING -- DONT TOUCH!'

        WindowWidth = 1000
        WindowHeight = 500



'GET RID OF MAIN WINDOW (CONSOLE LOG)'
        noMainWin




'PROVIDE BLANK STRING'
        open2$ = ""
        save1$ = ""



'BEGINNING SECTION'
    [Begin]


'DEFAULT OPEN PATH'
        path2$ = "C:\Users\peter\Desktop\FiveM MODS\FileName"

'DEFAULT SAVE PATH'
        path1$ = "C:\Users\peter\Desktop\FiveM MODS\FileName"

'THEME SETUP'

    'COLOR CONFIG'

        BackgroundColor$ = "darkgray"   'MAIN GUI COLOR'
        ForegroundColor$ = "darkgreen"  'TEXT COLOR'
        TexteditorColor$ = "gray"       'TEXT BACKGROUND COLOR'

'BUTTONS'
        Button #le.open, "Open", [open],UL, 7, 10, 95, 35
        Button #le.save, "Save", [save],UL, 7, 45, 95, 35

'TEXTEDITOR'
        texteditor #le.text, 107, 10, 873, 427

'OPENS MAIN GUI'
        Open "FiveM Data File Editor" for window as #le

'SETS UP TRAPCLOSE FOR NATIVE PROGRAM SHUTDOWN'
        print #le, "trapclose [exit]";

'SETS UP TEXTEDITOR'
        print #le.text, "!autoresize"
        print #le.text, "!font consolas 13"

    [DoNothing]
'DOES NOTHING'
        wait

    [codeColor]
'WIP - SYNTAX COLOR'
        Wait


    [save]
'OPENS GUI TO SAVE DATA FILE'
        filedialog "Save Data File...", "*.lua;*.meta;*.json;*.xml;*.txt", save1$
        if save1$ = "" then
            goto [DoNothing]
        else
            print #le.text, "!font consolas 13"
            print #le.text, "!contents? a$";
            open save1$ for binary as #save
            print #save, a$
            close #save
        end if
    Wait

    [open]
'OPENS GUI TO OPEN DATA FILE'
        filedialog "Open Data File", "*.lua;*.meta;*.json;*.xml;*.txt", open2$
        if open2$ = "" then
        goto [DoNothing]
        else
            print #le.text, "!cls"
            open open2$ for input as #openF
            code$ = input$(#openF, lof(#openF))
            print #le.text, code$
            print #le.text, "!contents code$"
            print #le.text, "!font consolas 13"
            close #openF
        end if
    Wait

    [exit]
'CHECKS TO SEE IF TASK #save or #openF IS RUNNING -- KILLS THEM IF THEY ARE -- CLOSES MAIN PROGRAM'
        if save1$ = "" then
            open "closer1" for binary as #save
            close #save
        else
            goto [closeOut]
        end if

        if open2$ = "" then
            open "closer2" for binary as #openF
            close #openF
        else
            goto [closeOut]
        end if

    [closeOut]
        close #le
        end
