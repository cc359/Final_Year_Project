#!/usr/bin/ python
import csv, os, sys, requests,shutil
import easyaccess as ea
from collections import defaultdict


#Pre-requisites for use:
# requests : a python library for HTTP requests (http://docs.python-requests.org/en/master/)
# Montage: an incredibly powerful package for .fits manipulation (http://montage.ipac.caltech.edu/docs/download.html), read the documentation for installing carefully and learn how to use SubCube and mViewer.
#Access to the DES database , the password and username is those of DESSCI.  Please change these values in the script at lines 44 and 45.

###Currently only works for Y1 data, as it relies on Y1A1_FIRSTCUT_EVAL for RUN names . Update soon!
###Note if .csv contains ccd's in range of 0-9 the number will need a leading zero currently!!!
### The only variables that need changing are DESusername and DESpassword currently, I will add them in as arguments to the main process later as it is more secure that storing
####This command script works as follows in command line or terminal (this was programmed on a Linux distribution so may need changing):
####  python single_epoch_no_pass.py the/directory/your/working/from/ the_csv_you_want_to_analyse.csv argument3
##Argument3 = 'true' , if you want to make folders and download the fits files , argument3= 'false' if you simply want to cut and make .pngs of already existing .fits files



###Note if .csv contains ccd's in range of 0-9 the number will need a leading zero currently!!!


# Generic CSV file dictioanry generator
def ReadFromCSV(fname):
    with open(fname, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        data = defaultdict(list)
        for row in reader:
            for (key, value) in row.items():
                data[key].append(value)

        return data
    return None


def MakeFolders(baseDir, Candcsv):   #i.e. Candcsv = CandInfo["expnum"]
    for iterator in range(len(Candcsv["expnum"])):
        newPath = baseDir + Candcsv["expnum"][iterator]
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        else:
            print "Folder for " + Candcsv["expnum"][iterator] + " already exists"
    return None

def DownloadFits(baseDir, CandInfo):
    session = requests.Session()
    DESusername = 'cc359' #Username and Password to be stored separately as either variables or possibly user inputs on session start up
    DESpassword = 'jerry543' #Now expired pwd (as of 22/08/16, fine to use as demo)
    base = 'https://desar2.cosmology.illinois.edu/DESFiles/new_archive/Archive/OPS/red/'

    for iterator in range(len(CandInfo["expnum"])):

        os.chdir(baseDir+'/'+CandInfo["expnum"][iterator])
        #if CandInfo["expnum"][iterator] >= 20130815 and CandInfo["expnum"][iterator] <= 20140214: #FOR Y1N DR
        if CandInfo["nite"][iterator] >= 20130815 and CandInfo["nite"][iterator] <= 20140214:
            url = base+ CandInfo["RUN"][iterator] +'/red/DECam_00'+ CandInfo["expnum"][iterator] +'/'+'DECam_00'+CandInfo["expnum"][iterator]+'_'+CandInfo["ccd"][iterator]+'.fits.fz'
        #print url (e.g. DESFiles/new_archive/Archive/OPS/red/20130929204225_20130928/red/DECam_00239310/DECam_00239310_30.fits.fz
        else:
            url=base+
        request = session.get(url, auth=(DESusername,DESpassword),stream=True)
        print [iterator]
        # Place file into correct folder
        if request.status_code != 200:
			print 'Did not connect for url '+ url
        else:
            print "Downloading fits.fz file "+CandInfo["expnum"][iterator]+"_"+CandInfo["ccd"][iterator] +".fits.fz"
            with open('DECam_00'+CandInfo["expnum"][iterator]+'_'+CandInfo["ccd"][iterator]+'.fits.fz','wb') as f:   #writes the fits file in the folder with appropriate name
				shutil.copyfileobj(request.raw,f)
            os.system('for i in $(ls); do funpack $i; done')
            os.system('rm DECam_00'+CandInfo["expnum"][iterator]+'_'+CandInfo["ccd"][iterator]+'.fits.fz')

def GetRUN(CandInfo):
    connection=ea.connect()
    cursor=connection.cursor() ##create a cursor object to handle the DB

    query='select RA,DEC,RUN,nite,SOFTID from ' ##query

    QQ=cursor.execute(query)

def subCubeCut(baseDir,CandInfo):
    for iterator in range(len(CandInfo["expnum"])):
        os.chdir(baseDir+'/'+CandInfo["expnum"][iterator])

        x_y_param= '0.06667 0.06667' #x and y of cut length in degrees, this is approximately 4x4 arcmins
        cmd='mSubCube '+'DECam_00'+CandInfo["expnum"][iterator]+'_'+CandInfo["ccd"][iterator]+'.fits '+CandInfo["expnum"][iterator]+'_cut'+'.fits '+CandInfo["ra (deg)"][iterator]+' '+CandInfo["dec (deg)"][iterator]+' '+x_y_param
        os.system(cmd)



def WriteRegionFile(baseDir, CandInfo):
    for iterator in range(len(CandInfo["expnum"])):
        os.chdir(baseDir+'/'+CandInfo["expnum"][iterator])
        regname= open(CandInfo["expnum"][iterator]+'.reg',"w")

        x_circle=CandInfo["ra (deg)"][iterator]+'d'  #x position , d specifies it is in degrees , RA
        y_circle= CandInfo["dec (deg)"][iterator]+'d' #y position , "   "        "  " "   ", DEC
        radius= '5' #radius of circle to draw, physical units w/o d, again d specifies in degrees e.g. 0.008333d

        contents= 'circle '+x_circle+' '+y_circle+' '+radius+' # color=green' #circle(x,y,radius) , the '#' seperates the circle command and colors the circle in this case

        regname.write(contents)
        regname.close()

def Circles(baseDir,CandInfo):  #Applies the region file created by WriteRegionFile() and creates an image from the fits file in this case using a logarithmic scale colourmapped grey
    for iterator in range(len(CandInfo["expnum"])):
        os.chdir(baseDir+'/'+CandInfo["expnum"][iterator])
        fits_name=CandInfo["expnum"][iterator]+'_cut'+'.fits'
        bin_value= " -bin factor 3"
        exit= ' -exit'
        img= ' -saveimage jpeg '+CandInfo["expnum"][iterator]+'_cut'+'.jpeg'
        log= ' -scale linear -scale mode zscale -cmap grey -zoom 2 -pan to '+CandInfo["ra"][iterator]+' '+CandInfo["dec"][iterator]+' wcs fk5'   #-scale limits 400 400000 will set manual limits, however it is varying wildly for both

        cmd= 'ds9 -tile '+fits_name+' -regionfile '+ CandInfo["expnum"][iterator]+'.reg '+log+img+exit
        os.system(cmd)
        #os.system('ds9 -exit')


def mViewerImage(baseDir,CandInfo):  #Currently not in use!
    for iterator in range(len(CandInfo["expnum"])):
        os.chdir(baseDir+'/'+CandInfo["expnum"][iterator])
        cutfit= CandInfo["expnum"][iterator]+'_cut'+'.fits'
        imgout= CandInfo["expnum"][iterator]+'_cut'+'.png'
        cmd= 'mViewer -gray '+cutfit+' 0s 99.5% '+'linear -out '+imgout
        os.system(cmd)

def CopyImgs(baseDir,CandInfo):
    for iterator in range(len(CandInfo["expnum"])):
        filename= CandInfo["expnum"][iterator]+'_cut'+'.jpeg'
        filepath_input= baseDir+CandInfo["expnum"][iterator]+"/"+filename
        filepath_output= baseDir+"Images/"+filename
        cmd="cp "+filepath_input+" "+filepath_output

        os.system(cmd)


if __name__ == "__main__":


    baseDir = sys.argv[1] # Pass in the location as a command line argument,
                          # means its configurable if another script wishes to use this script
    csvFile = sys.argv[2]
    needToPreProcess= sys.argv[3]
    CandInfo = ReadFromCSV(baseDir + csvFile)

    if needToPreProcess == 'true':
        MakeFolders(baseDir, CandInfo)

        DownloadFits(baseDir, CandInfo)
        print "Finished batch downloading, cutting, and making images"
    else:
        print "Candidate List could not be retrieved"

    if needToPreProcess == 'false' :
            # Run Montage subCube cut process
        os.system("mkdir "+baseDir+"Images")
        WriteRegionFile(baseDir, CandInfo)
        subCubeCut(baseDir, CandInfo)
        Circles(baseDir,CandInfo)
        CopyImgs(baseDir,CandInfo)
            # Run Montage mViewer image from fits
        #mViewerImage(baseDir,CandInfo)

        print "Nothing new downloaded, cutting and image making done!"
    else:
        print "Something went wrong, check that your exposure directories are occupied with the relevant .fits file. \n Try re-downloading the files by typing 'true' as the third argument"
