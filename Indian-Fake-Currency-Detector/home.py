from tkinter import *
from tkinter import messagebox
import os

class FirstPage(Tk) :
    def __init__(self):
        super(FirstPage,self).__init__()

        self.title("First page")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry("%dx%d" % (width, height))




        self.lbl1= Label(self, text="Fake Currency detector", font="Georgia 80 bold", fg="red").place(x=00, y=200)

        # button
        self.bt1 = Button(self, text="Register", font="RockwellExtraBold 20 bold underline", command=self.clickme_register, bd=0)
        self.bt1.place(x=1000, y=30)

        self.bt2 = Button(self, text="Login", font="RockwellExtraBold 20 bold underline", command=self.clickme_login, bd=0)
        self.bt2.place(x=1150, y=30)



    def clickme_register(self):
        os.system('registration.py')


    def clickme_login(self):
        os.system('login.py')

root=FirstPage()
root.mainloop()

