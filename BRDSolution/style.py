## Custom Module
from alcustoms.tkinter import style


defaultstyle = {
    'Valid.TEntry':{
            'configure':{
                'font':('Times',12,'bold'),
                'foreground':'gold'}
            },
    'Invalid.TEntry':{
            'configure':{
                'font':('Times',12,'italic'),
                'foreground':'red'}
            },
    }

def loadstyle():
    style.loadstyle(defaultstyle)