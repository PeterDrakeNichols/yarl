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
                curveShape = 'squareZ',
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
       
        self.off = mc.group( n = '%sBuf1_grp' %prefix, em = 1 ) 
        self.c = prefix + suffix

        self.tx, self.ty, self.tz = self.c + '.tx', self.c + '.tz', self.c + '.tz'
        self.rx, self.ry, self.rz = self.c + '.rx', self.c + '.rz', self.c + '.rz'
        self.sx, self.sy, self.sz = self.c + '.sx', self.c + '.sz', self.c + '.sz'
        self.t = [ self.tx, self.ty, self.tz ]
        self.r = [ self.rx, self.ry, self.rz ]
        self.s = [ self.sx, self.sy, self.sz ]
        self.v = self.c + '.v'

        
        curve = createCurve( curveShape )
        mc.rename( curve, self.c ) 
        self._rotateCurveShape( self.c, scale, rotateShape ) 
        mc.rename( self.c, prefix + suffix )
        mc.parent( self.c, self.off )
        
        #color based on naming convention
        
        ctrlShapes = mc.listRelatives( self.c, s = 1, type = 'nurbsCurve' ) #returns name instead of list
        
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
        
        #match translation and rotation of self.off
        
        if mc.objExists( translateTo ):
            
            mc.delete( mc.pointConstraint( translateTo, self.off ) )
        
        if( mc.objExists( rotateTo ) ):
            
            mc.delete( mc.orientConstraint( rotateTo, self.off ) )
       
        #parent self.off
        
        if mc.objExists( parent ):
        
            mc.parent( self.off, parent )
        
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

            mc.setAttr( '%s.%s'%(self.c,at) , l = 1, k = 0 )

    def _rotateCurveShape(self, controlObject, scale, rotateShape):

        ctlShapes = mc.listRelatives( controlObject, s = 1, type = 'nurbsCurve' ) 
        
        for s in ctlShapes:
            
            cls = mc.cluster( s )[1]
            mc.xform(cls, ro = rotateShape, eu = 1)
            mc.scale( scale, scale, scale, cls)
            mc.delete( s, ch=1 )
