import csv, os, sys, shutil
from collections import defaultdict

def ReadFromCSV(fname):
    with open(fname, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        data = defaultdict(list)
        for row in reader:
            for (key, value) in row.items():
                data[key].append(value)

        return data
    return None

def MoveImg(baseDir,CandInfo,ImageDir):
    for iterator in range(len(CandInfo["expnum"])):
        ImgIn=baseDir+CandInfo["expnum"][iterator]+'/'+CandInfo["expnum"][iterator]
        +'_cut'+'.jpeg'
        ImgOut=ImageDir+'/'+CandInfo["expnum"][iterator]+'_cut'+'.jpeg'
        shutil.copyfile(ImgIn,ImgOut)

def makeHomepage(baseDir,CandInfo):
    html= open('homepage.html',"w")
    Header="""<style>body {background-color:#ffffff;}h1"""+
    """{color: #660000; text-align: center; font-family: "Arial"; """+
    """text-decoration: underline}h2{font-family:"Arial" }"""+
    """ul{font-family: "Arial"}</style>
"""
    html.write(Header)
    

def makeHTML(baseDir,CandInfo,htmlName,CandName,ImageDir):
    html= open(baseDir+htmlName+'.html',"w")
    Header="""<html><head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8"><style>"""+
    """body {background-color:#ffffff;}h1 {color: #4f053c; text-align: center; """+
    """font-family: "Arial"}table {font-family: "Arial"; font-size: 12px; """+
    """text-align: center;}</style></head><body>"""+
    """<h1>DES Single Epoch Images of TNO """+
    CandName+"""</h1><table><colgroup><col width="50"><col width="200">"""+
    """<col width="300"><col width="200"><col width="200"><col width="200">"""+
    """</colgroup><tbody><tr><td>No</td><td>Image</td><td>Date</td><td>Exposure'"""+
    """ Number</td>"""+
    """<td>RA(HH:MM:SS,FK5)</td><td>DEC(HH:MM:SS,FK5)</td><td>Filter</td></tr>\n"""
    html.write(Header)
    for iterator in range(len(CandInfo["expnum"])):
        Imagelink="Images"+"/"+str(CandInfo["expnum"][iterator])+'_cut.jpeg'
        itera='<tr><td>'+str(iterator)+'</td><td>'
        date=str(CandInfo["date"][iterator])+'</td><td>'
        expnum=str(CandInfo["expnum"][iterator])+'</td><td>'
        ra=str(CandInfo["ra"][iterator])+'</td><td>'
        dec=str(CandInfo["dec"][iterator])+'</td><td>'
        img ='<img src='+Imagelink+' height="512" width="512" border="0"></td><td>'
        filt=str(CandInfo["band"][iterator])+'</td></tr>\n'
        Line=itera+img+date+expnum+ra+dec+filt

        html.write(Line)

    Footer='</tbody></table></body></html>'
    html.write(Footer)
    html.close()





if __name__ == "__main__":


    baseDir = sys.argv[1] # Pass in the location as a command line argument,
                          # means its configurable if another script wishes to
                          #use this script
    csvFile = sys.argv[2]

    htmlName = sys.argv[3]
    CandName= sys.argv[4]


    CandInfo = ReadFromCSV(baseDir + csvFile)
    ImageDir=baseDir+"Images"
    os.system('mkdir '+ ImageDir)


    MoveImg(baseDir,CandInfo,ImageDir)

    makeHTML(baseDir,CandInfo,htmlName,CandName,ImageDir)
