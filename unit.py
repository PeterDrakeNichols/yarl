"""
class for a creating a rig unit
@category Rigging @subcategory unit
@tags unit class
@author: petey
"""
import maya.cmds as mc
import control
import node


'''
Base class for all rig units I.E. limb, tail, tongue
A unit should be autonomous and transform from the attachSpace control without issue
'''

class Unit( object ):

    def __init__(
                self,
                prefix = 'new',
                suffix = '_ctl',
                scale = 1.0,
                curveShape = 'squareZ',
                attachTrans = ''
                ):

        self.unit = mc.group( n = prefix + 'Unit_grp', em = 1 )
        self.hide = mc.group( n = prefix + 'Hide_grp', em = 1 )
        self.noTouch = mc.group( n = prefix + 'NoTouch_grp', em = 1 )
        self.joints = mc.group( n = prefix + 'Joints_grp', em = 1 )
        self.prefix = prefix
        self.unitControl = control.Control( prefix = self.prefix + 'Unit', colorIdx = '', curveShape = curveShape, suffix = suffix )

        if attachTrans:

            mc.delete( mc.parentConstraint( attachTrans, self.unitControl.off ) )
       
        mc.parent( self.noTouch, self.joints, self.hide )
        mc.parent( self.hide, self.unitControl.c )
        mc.parent( self.unitControl.off, self.unit )
        mc.hide( self.hide )
        mc.setAttr( self.noTouch + '.it', 0 )

class LocalUnit( Unit ):

    def __init__( self ):

        # spaces

        super( LocalUnit, self ).__init__(  curveShape = 'fatCross' )
        self.globalSpace = control.Control( prefix = self.prefix + 'GlobalSpace', colorIdx = 29, curveShape = 'cross' )
        self.localSpace = control.Control( prefix = self.prefix + 'LocalSpace', colorIdx = 29, curveShape = 'cross' )
        self.bodySpace = control.Control( prefix = self.prefix + 'BodySpace', colorIdx = 29, curveShape = 'cross',)
        self.itemSpace = control.Control( prefix = self.prefix + 'ItemSpace', colorIdx = 29, curveShape = 'cross' )
        mc.parent( self.localSpace.off, self.bodySpace.off, self.globalSpace.off, self.itemSpace.off, self.unitControl.c )

        #visibility

        spaceVisPlug = self.unit + '.space_vis'
        spaceShapes = [ mc.listRelatives( curve, c = 1 )[0] for curve in [ self.globalSpace.c, self.localSpace.c, self.bodySpace.c, self.itemSpace.c, self.unitControl.c  ] ]
        mc.addAttr( self.unit, ln = 'space_vis', at = 'bool', dv = 0, h = 0, k = 1 )
        
        for shape in spaceShapes:

            mc.connectAttr( spaceVisPlug, shape + '.v'  )



class GlobalUnit( Unit ):

    def __init__( self, prefix = 'new' ):

        # global control

        super( GlobalUnit, self ).__init__(  prefix = 'superMover', curveShape = 'masterAnim' )
        mc.parent( self.unitControl.c, self.unit )
        rigScalePlug = self.unitControl.c + '.global_scale'
        mc.addAttr( self.unitControl.c, ln = 'global_scale', at = 'float', dv = 1, h = 0, k =1 )

        for attr in self.unitControl.s:

            mc.setAttr( attr, l = 0 )

        mc.connectAttr( rigScalePlug, self.unitControl.c + '.sx' )

        #scale reciprocal 

        scaleRecip = node.recipNode( prefix = 'superMover', inPlugOne = rigScalePlug )
        self.recipPlug = scaleRecip + '.ox'

        # groups

        self.modelGrp = mc.group( n = 'model_grp', em = 1 )
        self.deformGrp = mc.group( n = 'deform_grp', em = 1 )
        mc.parent( self.modelGrp, self.deformGrp, self.unit )

        # clean-up

        for attr in [ 't', 's', 'r' ]:

            mc.setAttr( self.unit + '.' + attr, l = 1 , cb = 0, k = 0 )

        mc.hide( self.deformGrp )
        mc.delete( self.unitControl.c + 'Shape1.cv[0:10]', self.unitControl.off,  )
        self.unit = mc.rename( self.unit, prefix + '_grp' )
        self.unitControl.c = mc.rename( self.unitControl.c,  'superMover_ctl' )

        # root control

        self.rootControl = control.Control( prefix = 'root', colorIdx = '', curveShape = 'circleY', scale = 0.45)
        mc.parent( self.rootControl.off, self.unitControl.c )





        



    



