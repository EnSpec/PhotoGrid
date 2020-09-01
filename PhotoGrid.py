##Simple Tkinter application
##Opens up a series of digital photos that are sampled for cover types according to a pre-determined grid.

import Tkinter, os, math, shutil,csv, numpy, time, platform, PIL
from Tkinter import *
import tkMessageBox,tkFileDialog
from PIL import ImageDraw, Image, ImageTk
from sys import argv

########################################################## BASE OPTIONS

# ... cover types to be considered
optList=['Shrub','Grass','Forb','NPV','Wood','Lichen','Moss','Moss-brown','Soil','Lava','Rock','Shadow','Mask']
optList.sort()

# ... one dimension of grid to create (will be squared to get total number of samples.)
numGrid=5

########################################################## END BASE OPTIONS

class myWindow():

    def __init__(self,inImage,sCS,optList,numGrid):

        # DEFINE CONSTANTS
        self.mw=Tkinter.Tk()
        # Set geometry
        w=self.mw.winfo_screenwidth()
        h=self.mw.winfo_screenheight()
        x=800
        y=800
        self.mw.geometry("%dx%d%+d%+d" % (x, y, (w/2)-(x/2), (h/2)-(y/2)))

        self.inImage=inImage
        aBN=os.path.basename(inImage)
        self.outArrX=[]
        self.outArrY=[]
        self.collectShapes=[]

        # Operators
        self.optList=optList
        self.numGrid=numGrid
        self.selOption=''
        self.coverTypes=[]
        self.coverCount=[]
        self.CS=sCS

        # Option window callback
        def selection(event):
            theOption=self.lb.get(ACTIVE)
            self.selOption=theOption
            self.coverTypes.append(theOption)
            nearRect=self.currRect
            self.canvas.addtag_withtag(theOption,nearRect)
            # Check if all have been clicked
            numTagged=len(self.canvas.find_withtag('Clicked'))
            if numTagged==(self.numGrid)**2:
                print 'Done!'
                for i in self.optList:
                    iCnt=self.coverTypes.count(i)
                    self.coverCount.append(iCnt)
                outRow=[self.inImage]+self.coverCount
                self.CS.writerow(outRow)
                print self.coverTypes
                print self.coverCount
                doneLoop()
            else:
                self.ow.destroy()

        # Create option window
        def optWindow(xyLoc,clipImg,buffPix):
            zoomFac=2
            rDim=20 # See where the dimensions of the original rectangles are set
            self.ow=Tkinter.Toplevel()
            self.w=xyLoc[0]
            self.h=xyLoc[1]
            h=self.ow.winfo_screenheight()
            y=(len(self.optList))*30 +10
            x=y+140+10
            self.ow.geometry("%dx%d%+d%+d" % (x, y, self.w, self.h))
            self.canvasL=Canvas(self.ow,width=y+10,height=y+10)
            self.canvasL.pack(side=LEFT,padx=5,pady=5,fill=Y)
            res_Img=clipImg.resize(tuple([zoomFac*x for x in clipImg.size]))
            #print res_Img.size
            #cropRect1=[buffPix*zoomFac,buffPix*zoomFac,res_Img.size[0]-(buffPix*zoomFac),res_Img.size[0]-(buffPix*zoomFac)]
            cropRect1=[((y+10)/2.)-(buffPix*zoomFac)/2.,((y+10)/2.)-(buffPix*zoomFac)/2.,((y+10)/2.)+(buffPix*zoomFac)/2.,((y+10)/2.)+(buffPix*zoomFac)/2.]
            #print cropRect1
            img_Tkc=ImageTk.PhotoImage(res_Img,Image.BICUBIC)
            self.canvasL.create_image((y+10)/2.,(y+10)/2.,image=img_Tkc,anchor=CENTER,tags="cImage")
            self.cropImage=img_Tkc
            self.canvasL.create_rectangle(cropRect1[0],cropRect1[1],cropRect1[2],cropRect1[3],outline='red',width=2,tags="cRect")
            self.canvasL.update()
            self.lb=Listbox(self.ow,bd=2,font=("Calibri",14),activestyle='dotbox',selectmode=SINGLE)
            self.lb.pack(side=RIGHT,padx=5,pady=5,fill=Y)
            for item in self.optList:
                self.lb.insert(END,item)
            self.lb.bind("<Double-Button-1>",selection)

        # Set canvas size fraction
        def getImgSize():
            self.theImg=PIL.Image.open(self.inImage)
            theSize=self.theImg.size
            #return(int(math.ceil(float(theSize[0])/float(self.mw.winfo_screenwidth()))))
            return(2)

        self.theFrac=getImgSize()
        print self.theFrac

        # ...pre-process Image
        def resizeImage():
            self.theImgFull=PIL.Image.open(self.inImage)
            #print self.theImgFull.size
            theSize=self.theImg.size
            self.theImg=self.theImgFull.resize((theSize[0]/self.theFrac,theSize[1]/self.theFrac))

        resizeImage()

        # DEFINE CALLBACKS
        def doneLoop():
            doneMessage="Done tagging all grids!"
            resp=tkMessageBox.showinfo("Done!",doneMessage)
            skipImage()

        def skipImage():
            self.mw.destroy()
        
        def callback(event):
            x=self.canvas.canvasx(event.x)
            y=self.canvas.canvasy(event.y)
            buffPix=50
            x0=event.x
            y0=event.y
            nearRect=self.canvas.find_closest(x,y,halo=10)
            self.currRect=nearRect
            theTag=self.canvas.gettags(nearRect)[0]
            allTag=self.canvas.gettags(nearRect)
            if theTag!='aImage' and not 'Clicked' in allTag:
                cropRect=[2*x for x in self.canvas.bbox(nearRect)]
                ext_Rect=[-buffPix,-buffPix,buffPix,buffPix]
                cropRect=[x+y for x,y in zip(cropRect,ext_Rect)]
                cropRect=tuple(cropRect)
                clipImg=self.theImgFull.crop(cropRect)
                self.canvas.addtag_withtag('Clicked',nearRect)
                self.canvas.itemconfigure(nearRect,outline='cyan')
                optWindow((x0,y0),clipImg,buffPix)
                theClass=self.selOption
                print theClass
            

        # ...END DEFINE CALLBACKS
        # START BUILDING WIDGETS

        # Create widgets

        self.mw.grid_rowconfigure(0,minsize=50,pad=10,weight=0)
        self.mw.grid_rowconfigure(1,minsize=50,pad=10,weight=0)
        self.mw.grid_rowconfigure(2,minsize=50,pad=10,weight=1)
        self.mw.grid_rowconfigure(3,minsize=50,pad=10,weight=0)

        self.mw.grid_columnconfigure(14,pad=10,weight=1)
        self.mw.grid_columnconfigure(15,pad=10)
        
        # Filename text label
        self.tfield=Label(self.mw,text='Current file: '+self.inImage,bg='white',font=("Calibri",14),anchor=W,padx=10)
        self.tfield.grid(row=0,columnspan=18,sticky=W+E,padx=10)

        # ...Image frame

        self.frame=Frame(self.mw,bd=2,relief=SUNKEN,padx=10)
        self.frame.grid_configure(row=2,column=0,columnspan=18,sticky=N+S+E+W,padx=5,pady=5)

        self.xscrollbar=Scrollbar(self.frame,orient=HORIZONTAL)
        self.yscrollbar=Scrollbar(self.frame,orient=VERTICAL)
        self.xscrollbar.pack(side=BOTTOM,fill=X)
        self.yscrollbar.pack(side=RIGHT,fill=Y)

        self.canvas=Canvas(self.frame,xscrollcommand=self.xscrollbar.set,yscrollcommand=self.yscrollbar.set,bg='white',height=self.theImg.size[1],cursor='X_cursor')
        self.xscrollbar.config(command=self.canvas.xview)
        self.yscrollbar.config(command=self.canvas.yview)
        img_Tk=ImageTk.PhotoImage(self.theImg)
        self.canvas.create_image(0,0,image=img_Tk,anchor=NW,tags="aImage")
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        self.canvas.pack(fill=BOTH)
        self.canvas.update()

        # Add selection polygons to Image canvas
        rDim=10
        theSize=self.theImg.size
        xSize=theSize[0]
        ySize=theSize[1]
        xStep=int(xSize/numGrid)
        yStep=int(ySize/numGrid)
        for i in range(numGrid):
            for j in range(numGrid):
                xLoc=xStep/2+(xStep*i)
                yLoc=yStep/2+(yStep*j)
                tagName='rect_'+str(i)+str(j)
                #self.canvas.create_rectangle(xLoc-rDim,yLoc-rDim,xLoc+rDim,yLoc+rDim,activefill='white',activeoutline='cyan',outline='red',width=3,tags=tagName)
                self.canvas.create_rectangle(xLoc-rDim,yLoc-rDim,xLoc+rDim,yLoc+rDim,activeoutline='cyan',outline='red',width=3,tags=tagName)
                self.canvas.update()
        
        # ...Bind canvas to button-clicks
        self.canvas.bind("<Button-1>", callback)

        # ...Skip button (Clicking skip will ignore current image and move to the next)
        self.btn2=Button(self.mw,text="Skip>>",command=skipImage,width=10)
        self.btn2.grid(row=3,column=17,sticky=W,padx=10)

        self.mw.mainloop()

# Get image files, output filename
root=Tkinter.Tk()
root.withdraw()
imageFiles=tkFileDialog.askopenfilename(title='Select image files',multiple=True)
save_File=tkFileDialog.asksaveasfilename(title='Select ouput filename',defaultextension='.csv',initialfile='PhotoCover.csv')
root.destroy()

#print imageFiles
if platform.system()=='Linux' or platform.system()=='Darwin':
    imageFiles=list(imageFiles)
elif platform.system()=='Windows':
    #imageFiles=imageFiles.split()
    imageFiles=list(imageFiles)

imageFiles=[x.encode('ascii','replace') for x in imageFiles]
save_File=save_File.encode('ascii','replace')

# Create CSV
sFL=open(save_File,'w')
sCS=csv.writer(sFL,delimiter=',',lineterminator='\n')
outHead=['Filename']+optList
outHead=[x.replace(' ','_') for x in outHead]
sCS.writerow(outHead)

# Run application
for inImage in imageFiles:
    myWindow(inImage,sCS,optList,numGrid)

# ...close CSV
sFL.close()

