



if __name__ == "__main__":
    import tkinter
    import style
    root = tkinter.Tk()
    style.loadstyle()
    import BRDSolution.inventory.controllers
    con = BRDSolution.inventory.controllers.MainController(parentpane=root)
    con.startup()
    root.mainloop()
