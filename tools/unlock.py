"""Close one presentation that an interrupted build left open in PowerPoint (without saving).

    python tools/unlock.py PATH.pptx

Only the named file is touched, and only if it is open; use it for build outputs / tagged sources, never for a
deck the user is editing.
"""
import os, sys
import win32com.client

target = os.path.normcase(os.path.abspath(sys.argv[1]))
app = win32com.client.Dispatch('PowerPoint.Application')
for i in range(app.Presentations.Count, 0, -1):
    p = app.Presentations(i)
    if os.path.normcase(p.FullName) == target:
        p.Saved = True
        p.Close()
        print('closed', target)
        break
else:
    print('not open', target)
