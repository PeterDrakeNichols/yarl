import maya.cmds as mc
import maya.mel as mm

"""
functions for making an arm (or other limb) twist that never flips. 
A nurbs surface with a twist deformer is created in world space.
The world space surface drives a ribbon with follicles attached to the limb via blendshape
Since There are no aim constraints involved so we dont have to worry about flipping 
Notes: 
assumes joints are oriented down X AXIS
naming fallows the convention r_shoulder1_jnt (side_part#_nodeType(abreviated 3 letters))
Usage Example:
shoulderData = makeTwistJoints( 'shoulder_jnt', 5, bone = 'shoulder' ) 
elbowData = makeTwistJoints( 'elbow_jnt', 5, bone = 'wrist' ) 
connectTwistJoints( elbowData, shoulderData )
@category Rigging @subcategory ribbon
@tags ribbon
@author: petey
"""

def makeTwistJoints( topJnt, numJnts, bone = 'shoulder' ):
    
    if mc.objExists( 'cMuscleSurfAttach1' ):
        
        mc.error( 'please rename your cMuscleSurfAttach stuff' )
    
    prefix = topJnt[0:-4]
    kidJnt = mc.listRelatives(topJnt, c = 1, type = 'joint')[0]
    jntLen = mc.getAttr( kidJnt + '.tx' )
    twistX = stepsBetweenFloats( 0, jntLen, numJnts - 1 )
    
    twistJnts = []
    
    for i, x in enumerate( twistX ):  
        
        name = topJnt[:-3] + '_jnt'
        jnt = mc.joint( topJnt, p = [ x, 0, 0 ], r = 1, n = prefix + str(i +1) + 'Twist_jnt', rad = 0.25 ) 
        twistJnts.append(jnt)
    
    rivetCrv = curveBetweenPoints( [0,0,0], [jntLen,0,0], prefix = prefix + 'Deform' ) 
    mc.rebuildCurve( rivetCrv, s = 5, d = 3, ch = 0 ) 
    rivetSrf = makeRibbonSrf( inCurve = rivetCrv, vect = [0, 0, 0.5] ) 
    driveSrf = mc.duplicate( rivetSrf, n = prefix + 'DriveTwist_srf' )
    mc.delete( mc.parentConstraint( topJnt, rivetSrf ), rivetCrv )
    
    if bone == 'shoulder':
        
        mc.parentConstraint( topJnt, rivetSrf, sr = [ 'x' ] )
    
    else:
        
        mc.bindSkin( rivetSrf, topJnt )
    
    twist = mc.nonLinear( driveSrf, type = 'twist') # name flag bugged
    twistNode = mc.listConnections( twist[1], d = 1, type = 'nonLinear' )[0]
    mc.rotate( 0, 0, 90, twist )
    bls = mc.blendShape( driveSrf, rivetSrf, foc = True, w = [0, 1], n = prefix + '_bls' )[0]
    
    vs = stepsBetweenFloats( 0, 1, numJnts - 1 )
    
    for i, v in enumerate( vs ):
        
        # This command is black boxed and really wonky to use but beats making follicles
        
        mc.select( mc.ls( '%sShape.uv[.5][%s]' %( rivetSrf[0], v  )) )
        r = mm.eval( 'cMuscleSurfAttachSetup();' )
        mc.select( clear = 1 )
        newName = prefix + str( i + 1 ) + '_riv'
        mc.rename( 'cMuscleSurfAttach1', newName )
        mc.orientConstraint( newName, twistJnts[i], mo = 1 )
    
    # clean and organize parts    
    
    partsGrp = mc.group( n = prefix + 'Twist_grp', em = 1 )
    mc.setAttr( partsGrp + '.it', 0 )
    mc.rename( 'grpSurfAttachRIG', prefix + 'Rivet_grp' )
    mc.rename(twistNode, prefix + 'Twist_nld' )
    mc.rename( twist[1], prefix + 'Twist_hdl' )
    attachGrp = prefix + 'Rivet_grp'
    twistHdl =  prefix + 'Twist_hdl'
    twistNode = prefix + 'Twist_nld'
    mc.parent( attachGrp, twistHdl, rivetSrf, driveSrf, partsGrp )
        
    # make additive nodes for start and end ( for connecting ribbons )
   
    addNodes = []
   
    for plug in [ 'end', 'start']:
   
        addNode = mc.createNode( 'addDoubleLinear', n = prefix + plug.title() + '_add' )
        mc.connectAttr( addNode + '.output', twistNode + '.' + plug + 'Angle' )
        addNodes.append( addNode )

    if bone == 'shoulder':
        
        mc.connectAttr( topJnt + '.rx', addNodes[1] + '.input1'  )
    
    else:
        
        mc.connectAttr( kidJnt + '.rx', addNodes[1] + '.input1' )
    
    return {
            'nonLinear': twistNode, 
            'addStart': addNodes[1] + '.input2',
            'addEnd': addNodes[0] + '.input2', 
            'topJnt': topJnt,
            'kidJnt': kidJnt  
           }

def curveBetweenPoints( pointA, pointB, prefix = 'new', constrainCurve = False ):

    '''
    creates curve from between two transform nodes or [ x,y,z  ]
    
    @param pointA: str, name of transform node or [linear, linear, linear]
    @param pointB: str, name of transform node or [linear, linear, linear]
    @param prefix: str, prefix for naming objects
    @param contrainCurve: bool, constrain the curve with weighted cluster
    @return: list(str), curve object
    '''

    xforms = [ pointA, pointB ]
    
    for xform in xforms:
        
        if len( xform ) > 3:
            
            xform = mc.xform( xform, q = 1, t = 1, ws = 1 )
    
    abCurve = mc.curve( n = prefix + '_crv',d =1, p = [xforms[0],xforms[1]] )
    
    if constrainCurve:
    
        mc.cluster(abCurve + '.cv[0]', n = prefix + 'crvPointA_cls', wn = [pointA, pointA], bs =1)
        mc.cluster(abCurve + '.cv[1]', n = prefix + 'crvPointB_cls', wn = [pointB, pointB], bs =1)
    
    return abCurve  
   
def makeRibbonSrf( inCurve = 'spine_crv', vect = [0,0.5,0] ):
    
    '''
    lofts a surface from supplied curve in a given vector
    
    @param inCurve: str, the curve to make a ribbon from
    @param vect: [ linear, linear, linear ], vector + magnitude for extrusion
    '''
    
    invVect = [axis * -1.0 for axis in vect]
    
    dupCrv1 = mc.duplicate( inCurve, n= 'loft1' + inCurve )
    mc.move( invVect[0], invVect[1], invVect[2], dupCrv1 )
    dupCrv2 = mc.duplicate( inCurve, n= 'loft2' + inCurve )
    mc.move( vect[0], vect[1], vect[2] ,dupCrv2)
    
    srfName = inCurve[0:-4] + '_srf'
    ribSrf = mc.loft( dupCrv1, dupCrv2, n=srfName,d=1, ch=False )
    mc.delete(dupCrv1, dupCrv2)
    
    return ribSrf

def stepsBetweenFloats( min, max, ammount ):
    
    min, max = float( min ), float( max ) 
    dif = max - min
    step = dif / ammount   
    floats = [ min ]
    
    for i in range( ammount ):

        min += step
        floats.append( min )
    
    return floats

def connectTwistJoints( driverData, kidData ):

    prefix = driverData[ 'topJnt' ][:-4]    
    mlt = mc.createNode( 'multDoubleLinear', n = prefix + '_mlt' )
    mc.setAttr( mlt + '.input1', 0.5 )
    mc.connectAttr( elbowData[ 'kidJnt' ] + '.rx', mlt + '.input2' )
    mc.connectAttr( mlt + '.output', driverData[ 'addEnd' ] )    
    mc.connectAttr( mlt + '.output', kidData[ 'addStart' ] )