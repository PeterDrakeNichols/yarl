from file import *
import maya.cmds as mc
from rigit.v1_0.utils import anim

def animToDrivenKey( driverAt, ignoreDriver = False, ignoreStatic = True ):
    
    '''
    Returns animation keys as a convenient dictionary for exporting driven keys
    
    Notes: - records within the minimum and maximum values set on the range slider
           - only records on frames where the driver attribute is keyed
           - set animation tangent type to linear before conversion
    
    @param driverAt: str, the attribute that should drive the animation
    @param ignoreDriver: bool, should the other channels on the driver object be ignored?
    @param ignoreStatic: bool, should unchanging values be ignored?
    @return dictionary
    '''
          
    drivenNodes = mc.ls( type = [ 'animCurveTL', 'animCurveTT', 'animCurveTA', 'animCurveTU' ] )
    driverNode = mc.listConnections( driverAt , d = 0, s = 1, type = 'animCurve' )[0]   
    
    min, max = mc.playbackOptions( q = 1, ast = 1 ), mc.playbackOptions( q = 1, aet = 1 )
    times = mc.keyframe( driverAt, time=( min, max ), q = 1, tc = 1)
    values = mc.keyframe( driverAt, time=( min, max ), q = 1, vc = 1)
    
    animTable = collections.OrderedDict()
    animTable[ 'title' ] = driverAt.replace( '.' , '_' )
    animTable[ 'driverAt' ] = driverAt
    animTable[ 'driverVals' ] = values  
    
    if ignoreDriver: 
    
        driver = driverAt.split('.')[0]
        driverNodes = mc.listConnections( driver , d = 0, s = 1, type = 'animCurve' ) 
        
        for node in driverNodes:
            
            drivenNodes.remove( node )
    
    else:
        
        drivenNodes.remove( driverNode )
        
    for node in drivenNodes:
        
        channel = mc.listConnections( node, s = 0, d = 1, p = 1)[0]
        
        if ignoreStatic:
            
            values = mc.keyframe( channel , time=( min, max ), q = 1, vc = 1 )
            
            if values[1:] == values[:-1]:
                
                continue
        
        values = []
        
        for time in times:
            
            mc.currentTime( time, e = 1 )
            value = [ mc.getAttr( channel ) ][0]
            values.append( value )
        
        animTable[ channel ] = values

    return animTable
    
def loadDrivenKeys( filePath = '' ):
    
    '''
    Imports driven keys from a .json file formated by animToDrivenKey() and exported with writeJson()
    
    @param filePath: str, optional if not specified calls getFilePath()
    @return None
    '''
    
    if not filePath:
        
        filePath = getFilePath()
        
    data = readJson( filePath )  
    driver = data.pop( 'driverAt' )
    driverVals = data.pop( 'driverVals' )
    driverTitle = data.pop( 'title' )
    
    for driven in data:
        
        anim.setDrivenKey( driver, driven, driverVals, data[ driven ], cleanDrivenPlug = True, 
                           preinf = 0, postinf = 0, intangtype = 'flat', outtangtype = 'flat', 
                           verbose = True )

# animTable = animToDrivenKey( 'mirror_ctl.tx',  ignoreStatic = True, ignoreDriver = True )
# fileName = animTable[ 'title' ] + '.json'
# animPath = getDirPath()
# writeJson( animPath, fileName, animTable )
# loadDrivenKeys()