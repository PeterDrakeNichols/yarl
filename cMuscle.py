import maya.cmds as mc
import maya.mel as mm
import maya.api.OpenMaya as om
import file

class SmartCollision( object ):
    
    def __init__( self, smartGrp ):
        
        self.smartGrp = smartGrp
        self.smartOff = mc.listRelatives( smartGrp, ad = 1, type = 'transform' )[0]
        self.jntA = mc.listConnections( self.smartGrp + '.JOINT_A' )[0]
        self.jntB = mc.listConnections( self.smartGrp + '.JOINT_B' )[0]
    
    @property
    def worldMatrix( self ):

        return mc.xform( self.smartOff, m = 1, q = 1, ws = 1 ) 
    
    @worldMatrix.setter
    def worldMatrix( self, coords ):
        
        mc.xform( self.smartOff, m = coords, ws = 1 )
    
    @classmethod
    def build( kls, jntA, jntB ):
         
        if mc.objExists( 'grpCMuscleSmartCollide1' ):
            
            mc.error( '<--- ABORTING: un-named smart collision groups in scene --->' ) 
            
            return None
        
        side = jntA[:2] if jntA[1] == '_' else ''
        side = jntB[:2] if jntB[1] == '_' else ''

        baseName = side + jntA.rsplit( '_' )[1] + jntB.rsplit( '_' )[1]
        mc.select( clear = 1 )
        mc.select( jntA, jntB, add = 1 )
        mm.eval( 'cMuscleSmartCollide_setup()' )

        dagNodes = [ 'grpCMuscleSmartCollide1' ]
        dagNodes.extend( mc.listRelatives( dagNodes[0], ad = 1 ) )
        newNames = [ baseName + suffix for suffix in [ 'Top_grp', 'node_colShape', 'Node_col', 'Const_grp', 'Base_grp' ] ]
        
        renamedNodes = []

        for i, node in enumerate( dagNodes ):
            
            renamedNode = mc.rename( node, newNames[i] ) 
            renamedNodes.append( renamedNode )

        _smartGrp = renamedNodes[0]
        
        mc.addAttr(  _smartGrp, sn = 'JOINT_A', at = 'message',)
        mc.addAttr(  _smartGrp, sn = 'JOINT_B', at = 'message')

        for jntAt in [ ( jntA , _smartGrp + '.JOINT_A' ), ( jntB , _smartGrp + '.JOINT_B' ) ]:

            if mc.attributeQuery('SMART_GRP', node = jntAt[0], ex = 1 ):

                attrIdx = kls.recurseMultiConnectable( jntAt[0] + '.SMART_GRP' )
                mc.connectAttr( jntAt[1], attrIdx )

            else:

                mc.addAttr( jntAt[0], sn = 'SMART_GRP', at = 'message', multi = 1 ) 
                mc.connectAttr( jntAt[1], jntAt[0] + '.SMART_GRP[0]' )
        
        return  kls( _smartGrp )

    @staticmethod
    def recurseMultiConnectable( attr, i = 0 ):

        availableChannel = attr + '[' + str( i ) + ']'

        if not mc.connectionInfo( availableChannel, sfd = True ):

            return availableChannel

        return ( SmartCollision.recurseMultiConnectable( attr, i = i + 1 ) )

    @staticmethod
    def exportSmartCollisions( smartCollisonsGrp = 'grpCMuscleSmartCollides', fileName = '', path = '' ):

        smartGrps = [ SmartCollision( smartGrp ) for smartGrp in mc.listRelatives( smartCollisonsGrp, c = 1, type = 'transform' ) ]
        smartData = [ [ smartGrp.jntA, smartGrp.jntB, smartGrp.worldMatrix ] for smartGrp in smartGrps ]
        print smartData

        filePath = file.getDirPath( path )
        file.writeJson( filePath, fileName, smartData )

    @staticmethod
    def importSmartCollisions( path = '' ):

        filePath = file.getFilePath( path )
        smartData = file.readJson( filePath )
        
        for entry in smartData:

            newSmartCol =  SmartCollision.build( entry[0], entry[1] )
            newSmartCol.worldMatrix = entry[2]

    def mirror( self ):

        name = self.smartGrp
        flipSide = 'r_' if self.smartGrp[:2] == 'l_' else 'l_'
        mirrorGrp = flipSide + self.smartGrp[2:]
        mirrorJntA = flipSide + self.jntA[2:] if self.jntA[1] == '_' else self.jntA
        mirrorJntB = flipSide + self.jntB[2:] if self.jntB[1] == '_' else self.jntB

        worldNegXMatrix = [ 1, -1, -1, 1,
                            1, -1, -1, 1,
                            1, -1, -1, 1,
                            -1, 1,  1, 1 ]

        if mc.objExists( mirrorGrp ):

            mc.error( '<--- ABORTING: %s already exists in scene --->' %( mirrorGrp ) ) 

            return None

        mirrorSmrtCol = self.build( mirrorJntA, mirrorJntB )
        mirrorSmrtCol.worldMatrix = [ value[0] * value[1] for value in zip( self.worldMatrix, worldNegXMatrix )  ]
