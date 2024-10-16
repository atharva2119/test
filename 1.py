from tkinter import *
from tkinter import ttk
import tkinter.filedialog
from PIL import ImageTk, Image
from tkinter import messagebox
import os

class Stegno:
    def main(self, root):
        root.title('Image Steganography')
        root.geometry('500x600')
        root.resizable(width=False, height=False)
        f = Frame(root)

        title = Label(f, text='Image Steganography')
        title.config(font=('courier', 33))
        title.grid(pady=10)

        b_encode = Button(f, text="Encode", command=lambda: self.frame1_encode(f), padx=14)
        b_encode.config(font=('courier', 14))
        b_encode.grid(pady=12)

        b_decode = Button(f, text="Decode", command=lambda: self.frame1_decode(f), padx=14)
        b_decode.config(font=('courier', 14))
        b_decode.grid(pady=12)

        f.grid()
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def frame1_decode(self, f):
        f.destroy()
        d_f2 = Frame(root)
        
        label_art = Label(d_f2, text='Select Image with Hidden Text:')
        label_art.config(font=('courier', 18))
        label_art.grid()

        bws_button = Button(d_f2, text='Select', command=lambda: self.frame2_decode(d_f2))
        bws_button.config(font=('courier', 18))
        bws_button.grid()

        back_button = Button(d_f2, text='Cancel', command=lambda: self.home(d_f2))
        back_button.config(font=('courier', 18))
        back_button.grid(pady=15)

        d_f2.grid()

    def frame2_decode(self, d_f2):
        d_f3 = Frame(root)
        
        myfile = tkinter.filedialog.askopenfilename(filetypes=[('png', '*.png'), ('jpeg', '*.jpeg'), ('jpg', '*.jpg'), ('All Files', '*.*')])
        
        if not myfile:
            messagebox.showerror("Error", "You have selected nothing!")
            return
        
        myimg = Image.open(myfile)
        
        hidden_data = self.decode(myimg)
        
        l2 = Label(d_f3, text='Hidden Data:')
        l2.config(font=('courier', 18))
        l2.grid(pady=10)

        text_area = Text(d_f3, width=50, height=10)
        text_area.insert(INSERT, hidden_data)
        text_area.configure(state='disabled')
        text_area.grid()

        back_button = Button(d_f3, text='Cancel', command=lambda: self.home(d_f3))
        back_button.config(font=('courier', 11))
        back_button.grid(pady=15)

        d_f3.grid(row=1)
        
    def decode(self, image):
        data = ''
        
        imgdata = iter(image.getdata())
        
        while True:
            pixels = [value for value in imgdata.__next__()[:3] +
                      imgdata.__next__()[:3] +
                      imgdata.__next__()[:3]]
            binstr = ''
            for i in pixels[:8]:
                binstr += '0' if i % 2 == 0 else '1'

            data += chr(int(binstr, 2))

            if pixels[-1] % 2 != 0:
                return data

    def frame1_encode(self, f):
        f.destroy()
        
        f2 = Frame(root)
        
        l1 = Label(f2, text='Select the Image in which you want to hide text:')
        l1.config(font=('courier', 18))
        l1.grid()

        bws_button = Button(f2, text='Select', command=lambda: self.frame2_encode(f2))
        bws_button.config(font=('courier', 18))
        bws_button.grid()

         back_button = Button(f2, text='Cancel', command=lambda: self.home(f2))
         back_button.config(font=('courier', 18))
         back_button.grid(pady=15)

         f2.grid()

    def frame2_encode(self, f2):
         ep = Frame(root)
         
         myfile = tkinter.filedialog.askopenfilename(filetypes=[('png', '*.png'), ('jpeg', '*.jpeg'), ('jpg', '*.jpg'), ('All Files', '*.*')])
         
         if not myfile:
             messagebox.showerror("Error", "You have selected nothing!")
             return

         myimg = Image.open(myfile).convert('RGB')  # Ensure the image is in RGB format
         myimage = myimg.resize((300, 200))  
         img = ImageTk.PhotoImage(myimage)

         l3 = Label(ep, text='Selected Image')
         l3.config(font=('courier', 18))
         l3.grid()

         panel = Label(ep, image=img)
         panel.image = img
         panel.grid()

         l2 = Label(ep, text='Enter the message')
         l2.config(font=('courier', 18))
         l2.grid(pady=15)

         text_area = Text(ep, width=50, height=10)
         text_area.grid()

         encode_button = Button(ep, text='Cancel', command=lambda: self.home(ep))
         encode_button.config(font=('courier', 11))

         back_button = Button(ep, text='Encode',
                              command=lambda: [self.enc_fun(text_area, myimg), self.home(ep)])
         
         back_button.config(font=('courier', 11))
         
         back_button.grid(pady=15)
         
         encode_button.grid()
         
         ep.grid(row=1)
         
         f2.destroy()

    def enc_fun(self,text_area,myimg):
       data = text_area.get("1.0", "end-1c")
       
       if len(data) == 0:
           messagebox.showinfo("Alert", "Kindly enter text in TextBox")
           return

       newimg = myimg.copy()
       self.encode_enc(newimg,data)

       save_path = tkinter.filedialog.asksaveasfilename(defaultextension=".png",
                                                         filetypes=[('PNG files (*.png)', '*.png')])
       if save_path:
           newimg.save(save_path)
           messagebox.showinfo("Success", "Encoding Successful\nFile is saved as {}".format(os.path.basename(save_path)))

    def encode_enc(self,newimg,data):
       w,h=newimg.size
       (x,y)=(0,0)

       for pixel in self.modPix(newimg.getdata(),data):
           newimg.putpixel((x,y),pixel)
           if (x==w-1):
               x=0
               y+=1
           else:
               x+=1

    def modPix(self,pix,data):
       datalist=self.genData(data)
       lendata=len(datalist)
       imdata=iter(pix)

       for i in range(lendata):
           # Extracting 3 pixels at a time
           pix=[value for value in imdata.__next__()[:3] +
                imdata.__next__()[:3] +
                imdata.__next__()[:3]]

           for j in range(0,8):
               if (datalist[i][j]=='0') and (pix[j]%2!=0):
                   pix[j]-=1

               elif (datalist[i][j]=='1') and (pix[j]%2==0):
                   pix[j]-=1

           if (i==lendata-1):
               if (pix[-1]%2==0):
                   pix[-1]-=1
           else:
               if (pix[-1]%2!=0):
                   pix[-1]-=1

           pix=tuple(pix)
           yield pix[0:3]
           yield pix[3:6]
           yield pix[6:9]

    def genData(self,data):
       newd=[]
       for i in data:
           newd.append(format(ord(i),'08b'))
       return newd

    def home(self, frame):
            frame.destroy()
            self.main(root)

root = Tk()
o = Stegno()
o.main(root)
root.mainloop()
