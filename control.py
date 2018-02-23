"""
class for a creating a keyable control object
@category Rigging @subcategory control
@tags control class
@author: petey
"""

import maya.cmds as mc
from cgmCurves import createCurve

class Control():

    def __init__(
                self,
                prefix = 'new',
                suffix = '_ctl',
                curveShape = 'circleX',
                rotateShape = [0,90,0],
                scale = 1.0,
                translateTo = '',
                rotateTo = '',
                parent = '',
                colorIdx = '',
                lockChannels = [ 's', 'v' ]
                ):

        """
        @param prefix: str, prefix to name new objects
        @param curveShape: str, imported from assets folder print control.Control.curveFiles
        @param rotateShape: [angle, angle angle], rotate shape node this ammount
        @param scale: float, scale value for size of control shapes
        @param translateTo: str, reference object for control position
        @param rotateTo: str, reference object for control orientation
        @param parent: str, object to be parent of new control
        @param lockChannels: list( str ), list of channels on control to be locked and non-keyable
        @return: None
        """

        #control and offset group
       
        ctrlOffset = mc.group( n = '%s_grp' %prefix, em = 1 ) 
        ctrlObject = prefix + suffix
        curve = createCurve( curveShape )
        mc.rename( curve, ctrlObject ) 
        self._rotateCurveShape( ctrlObject, scale, rotateShape ) 
        mc.rename( ctrlObject, prefix + suffix )
        mc.parent( ctrlObject, ctrlOffset )
        
        #color based on naming convention
        
        ctrlShapes = mc.listRelatives( ctrlObject, s = 1, type = 'nurbsCurve' ) #returns name instead of list
        
        for s in ctrlShapes:

            mc.setAttr( '%s.ove'%s, 1 )

            if not colorIdx:
            
                if( prefix[0:2] == 'l_' ):
                    
                    mc.setAttr( '%s.ovc' %s, 6 )

                elif( prefix[0:2] == 'r_' ):

                    mc.setAttr( '%s.ovc' %s, 13 )

                else:

                    mc.setAttr( '%s.ovc' %s, 22 )

            else:

                mc.setAttr( '%s.ovc' %s, colorIdx )
        
        #match translation and rotation of ctrlOffset
        
        if mc.objExists( translateTo ):
            
            mc.delete( mc.pointConstraint( translateTo, ctrlOffset ) )
        
        if( mc.objExists( rotateTo ) ):
            
            mc.delete( mc.orientConstraint( rotateTo, ctrlOffset ) )
       
        #parent ctrlOffset
        
        if mc.objExists( parent ):
        
            mc.parent( ctrlOffset, parent )
        
        # lock controls
        
        singleAttributeLockList = []
        
        for lockChannel in lockChannels:
        
            if lockChannel in [ 't' , 'r', 's']:
        
                for axis in [ 'x', 'y', 'z']:
        
                    at = lockChannel + axis
        
                    singleAttributeLockList.append( at )
            else:

            #if not compound example:visibility
                
                singleAttributeLockList.append( lockChannel )
        
        for at in singleAttributeLockList:

            mc.setAttr( '%s.%s'%(ctrlObject,at) , l = 1, k = 0 )

        # add public membership

        self.c = ctrlObject
        self.off = ctrlOffset

    def _rotateCurveShape(self, ctrlObject, scale, rotateShape):

        ctlShapes = mc.listRelatives( ctrlObject, s = 1, type = 'nurbsCurve' ) 
        
        for s in ctlShapes:
            
            cls = mc.cluster( s )[1]
            mc.xform(cls, ro = rotateShape, eu = 1)
            mc.scale( scale, scale, scale, cls)
            mc.delete( s, ch=1 )
