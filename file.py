import collections
import json
import os
import maya.cmds as mc

def getFilePath( path = '' ):
    
    # opens a dialogue and returns the path set by user to a FILE
 
    if not path:
        
        try:
            
            path = mc.fileDialog2( dialogStyle = 2, fileMode = 1, okc = 'xX_Get_Path_Xx' )[0]
            
            return path
            
        except:
            
            return

    else:

    	return path

def getDirPath( path = '' ):
    
    # opens a dialogue and returns the path set by user to a DIRECTORY

    if not path:
        
        try:
            
            path = mc.fileDialog2( dialogStyle = 2, fileMode = 2, okc = 'xX_Get_Path_Xx' )[0] + '/'
            
            return path
            
        except:
            
            return
    else:

    	return path

def writeJson( path, fileName, data ):
    
    # exports $data called $fileName to specified $path

    print data
    print( ' Saving %s to -------> %s    *^_^+' %( fileName, path ) )
    
    with open( path + fileName, 'w') as outfile:
        
        json.dump( data, outfile, sort_keys = True, indent = 4, separators=(',', ': ') )

    file.close( outfile )
    
def readJson( fileName ):
    
    # imports $data called $fileName from specified $path
    
    print( ' reading %s  *^_^+' %( fileName ) )
    
    try:
      
      with open( fileName, 'r' ) as jsonFile:
      
          return json.load( jsonFile )
    
    except:
    
        mc.error( 'Could not read ' + fileName.rsplit( '/', )[-1] )


