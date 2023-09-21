
from math import sin, cos
import pi3d, os
import math
import numpy as np
import time
import krpc
from datetime import timedelta

red = (1.0, 0.0 , 0.0, 1.0)
orange = (1.0, 0.7 , 0.0, 1.0)
green = (0.0, 1.0 , 0.0, 1.0)
blue = (0.0, 0.0 , 1.0, 1.0)
white = (1.0, 1.0 , 1.0, 1.0)
gray = (0.5,0.5,0.5, 1.0)
purple = (1.0,0.0,1.0, 1.0)

class OrbitInfo(object):
    UT = 0
    apoapsis = 0
    time_to_apoapsis = "N/A"
    periapsis = 0
    time_to_periapsis = "N/A"
    inclination = 0
    SMinA = 0
    SMajA = 0
    bodyOrbitingRadius = 1
    eccentric_anomaly = 0
    eccentricity = 0
    vertices = []
    nodeEccentricAnomaly = 0

orbitInfo = OrbitInfo()

MAX_CIRCLE_POINTS = 120

class Orb:
    def __init__(self, controller):
        self.controller = controller
        backimg = pi3d.Texture('assets/page_orbit.png')
        self.back = pi3d.ImageSprite(texture = backimg, shader = controller.flatsh, w=1280, h=720)
        self.back.position(0, 0, 2)   

        self.text = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=400, point_size=64, )
        
        espace = 0.45
        newtxt = pi3d.TextBlock(300, 180, 0.1, 0.0, 10, data_obj=orbitInfo, attr="apoapsis",
                text_format="{:,d}", size=0.7, spacing="C", space=espace, justify = 0,
                colour=white)
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(300, 120, 0.1, 0.0, 10, data_obj=orbitInfo, attr="time_to_apoapsis",
                text_format="{:s}", size=0.7, spacing="C", space=espace, justify = 0,
                colour=green)
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(300, -20, 0.1, 0.0, 10, data_obj=orbitInfo, attr="periapsis",
                text_format="{:,d}", size=0.7, spacing="C", space=espace, justify = 0,
                colour=white)
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(300, -80, 0.1, 0.0, 10, data_obj=orbitInfo, attr="time_to_periapsis",
                text_format="{:s}", size=0.7, spacing="C", space=espace, justify = 0,
                colour=green)
        self.text.add_text_block(newtxt)
        newtxt = pi3d.TextBlock(300, -220, 0.1, 0.0, 10, data_obj=orbitInfo, attr="inclination",
                text_format="{:1.2f}", size=0.7, spacing="C", space=espace, justify = 0,
                colour=white)
        self.text.add_text_block(newtxt)

        self.ship_marker = pi3d.Plane(w=55, h=55, x=-200, y=0)
        self.ship_texture = pi3d.Texture('assets/ship_marker.png')

        self.zoom = 1
        self.numericZoom = 0
        self.orbit = self.Orbit(self.controller, blue, "main")

        self.prevNodes = 0

    def getCircleVertices(centerX, centerY, radius):
        vertices = []

        circumference = 2.0*math.pi*radius
        idealOrbitPoints = max(1, int(circumference/2.0))
        numSegments = min(MAX_CIRCLE_POINTS/2, idealOrbitPoints)
        dTheta = 2.0*math.pi/numSegments
        theta = 0.0

        lastVertex = (centerX+radius, centerY, 0)
        for x in range(int(numSegments)):
            vertices.append(lastVertex)
            theta += dTheta

            cosTheta = math.cos(theta)
            sinTheta = math.sin(theta)
            newVertex = (centerX+cosTheta*radius, centerY+sinTheta*radius, 0)
            vertices.append(newVertex)

            lastVertex = newVertex

        return vertices

    def getEllipseVertices(centerX, centerY, SMajA, SMinA, startTA, endTA):
        vertices = []

        circumference = 2.0*math.pi*SMajA
        idealOrbitPoints = max(1, int(circumference/2.0))
        numSegments = min(MAX_CIRCLE_POINTS/2, idealOrbitPoints)
        dTheta = (endTA-startTA)/numSegments
        theta = startTA

        cosTheta = math.cos(theta)
        sinTheta = math.sin(theta)
        lastVertex = (centerX+cosTheta*SMajA, centerY+sinTheta*SMinA, 0)

        for x in range(int(numSegments)):
            vertices.append(lastVertex)
            theta += dTheta

            
            cosTheta = math.cos(theta)
            sinTheta = math.sin(theta)
            newVertex = (centerX+cosTheta*SMajA, centerY+sinTheta*SMinA, 0)
            vertices.append(newVertex)

            lastVertex = newVertex


        return vertices

    def getHyperbolaVertices(centerX, centerY, e, SMajA, periapsis, startTA, endTA):
        vertices = []


        numSegments = MAX_CIRCLE_POINTS/2
        dTheta = (endTA-startTA)/numSegments
        theta = startTA

        b = SMajA*(((math.sqrt((e*e)-1))/e)/-(-(1/e)))

        x = -SMajA*((e+math.cos(theta))/(1+(e*math.cos(theta))))
        y= b*((math.sqrt((e*e)-1)*math.sin(theta))/(1+(e*math.cos(theta))))

        lastVertex = (centerX+x, centerY+y, 0)

        for x in range(int(numSegments)):
            vertices.append(lastVertex)
            theta += dTheta

            x = -SMajA*((e+math.cos(theta))/(1+(e*math.cos(theta))))
            y= b*((math.sqrt((e*e)-1)*math.sin(theta))/(1+(e*math.cos(theta))))

            newVertex = (centerX+x, centerY+y, 0)
            vertices.append(newVertex)

            lastVertex = newVertex


        return vertices


    class Planets:
        def __init__(self, controller, streams):
            self.controller = controller
            self.prev_target = None

            #---------- MAIN BODY ----------
            self.mainBodyRadius = streams.vesselOrbit.body.equatorial_radius

            if streams.vesselOrbit.body.has_atmosphere:
                self.mainBodyAtmosphereRadius = streams.vesselOrbit.body.atmosphere_depth+self.mainBodyRadius
                mainBodyAtmVertices = []
                for x in range(MAX_CIRCLE_POINTS):
                    mainBodyAtmVertices.append((0,0,0))
                self.mainBodyAtmosphere = pi3d.Lines(vertices=mainBodyAtmVertices, material=gray, line_width=0, closed=False, x=0, y=0)

            mainBodyVertices = []
            for x in range(MAX_CIRCLE_POINTS):
                mainBodyVertices.append((0,0,0))
            self.mainBody = pi3d.Lines(vertices=mainBodyVertices, material=white, line_width=0, closed=False, x=0, y=0)
            
        def createNewBody(self, body):

            #---------- TARGET BODY ----------
            self.targetBodyName = body.name
            self.targetBodyRadius = body.equatorial_radius
            self.targetBodyAltitude = body.orbit.radius

            if body.has_atmosphere:
                self.targetBodyAtmosphereRadius = body.atmosphere_depth+self.targetBodyRadius
                targetBodyAtmVertices = []
                for x in range(MAX_CIRCLE_POINTS):
                    targetBodyAtmVertices.append((0,0,0))
                self.targetBodyAtmosphere = pi3d.Lines(vertices=targetBodyAtmVertices, material=gray, line_width=0, closed=False, x=0, y=0)

            targetBodyVertices = []
            for x in range(MAX_CIRCLE_POINTS):
                targetBodyVertices.append((0,0,0))
            self.targetBody = pi3d.Lines(vertices=targetBodyVertices, material=white, line_width=0, closed=False, x=0, y=0)  

            
        def draw(self, zoom, streams):

            #---------- CHECK FOR NEW TARGET ----------
            targetBody = streams.targetBody()
            if(targetBody != self.prev_target):
                print("NEW TARGET BODY")
                if targetBody != None:
                    self.createNewBody(targetBody)
                else:
                    try:
                        del(self.targetBody)
                    except:
                        print("tried to delete targetbody but the variable doesn't exist :(")
                    try:
                        del(self.targetBodyAtmosphere)
                    except:
                        print("tried to delete targetbodyAtmosphere but the variable doesn't exist :(")

            self.prev_target = targetBody
            
            #---------- MAIN BODY ----------
            offsetX = zoom*(int(-streams.vesselSMajA())+int(streams.vesselPeriapsis())+self.mainBodyRadius)

            tempVertices = Orb.getCircleVertices(-200-offsetX,0, self.mainBodyRadius*zoom)
            self.mainBody.re_init(pts = tempVertices)
            self.mainBody.draw()
            if hasattr(self, 'mainBodyAtmosphereRadius'):
                tempVertices = Orb.getCircleVertices(-200-offsetX,0, self.mainBodyAtmosphereRadius*zoom)
                self.mainBodyAtmosphere.re_init(pts = tempVertices)
                self.mainBodyAtmosphere.draw()

            #---------- TARGET BODY ----------

            if hasattr(self, 'targetBody'):
                self.targetBodyOffset = -offsetX+(zoom*self.targetBodyAltitude)
                tempVertices = Orb.getCircleVertices(-200+self.targetBodyOffset,0, self.targetBodyRadius*zoom)
                self.targetBody.re_init(pts = tempVertices)
                self.targetBody.draw()

            if hasattr(self, 'targetBodyAtmosphere'):
                self.targetBodyOffset = -offsetX+(zoom*self.targetBodyAltitude)
                tempVertices = Orb.getCircleVertices(-200-self.targetBodyOffset,0, self.targetBodyAtmosphereRadius*zoom)
                self.targetBodyAtmosphere.re_init(pts = tempVertices)
                self.targetBodyAtmosphere.draw()
                

    class Orbit:
        def __init__(self, controller, color, orbitType):
            self.controller = controller
            self.prevNumberOfOrbits = 1
            for x in range(MAX_CIRCLE_POINTS):
                orbitInfo.vertices.append((0,0,0))
            self.orbit = pi3d.Lines(vertices=orbitInfo.vertices, material=color, line_width=0, closed=False, x=0, y=0)
            self.type = orbitType

        def createNewOrbit(self, orbitNb):
            if orbitNb == 1:
                color = orange
            elif orbitNb == 2:
                color = purple
            elif orbitNb == 3:
                color = green
            else:
                color = gray
           
            self.secondaryOrbitsFigure[f'orbit{orbitNb}_vertices'] = []
            for x in range(MAX_CIRCLE_POINTS):
                self.secondaryOrbitsFigure[f'orbit{orbitNb}_vertices'].append((0,0,0))
            self.secondaryOrbitsFigure[f'orbit{orbitNb}_figure'] = pi3d.Lines(vertices=self.secondaryOrbitsFigure[f'orbit{orbitNb}_vertices'], material=color, line_width=0, closed=False, x=0, y=0)

        def drawSecondaryOrbits(self, zoom, offset, streams, orbitNb):
            UT = int(streams.UT())
            eccentricity = streams.secondaryOrbits[f'orbit{orbitNb}_eccentricity']()
            timeToSOIChange = streams.secondaryOrbits[f'orbit{orbitNb}_SOI_change']()
            timeToSOIEnter = streams.secondaryOrbits[f'orbit{orbitNb}_SOI_in']()
            periapsis = int(streams.secondaryOrbits[f'orbit{orbitNb}_periapsis']())
            SMajA = int(streams.secondaryOrbits[f'orbit{orbitNb}_SMajA']())
           
            if self.eccentricity < 1 and str(timeToSOIChange) == 'nan': #ORBIT IS AN ELLIPSE
                apoapsis = int(streams.secondaryOrbits[f'orbit{orbitNb}_apoapsis']())
                SMinA = int(streams.secondaryOrbits[f'orbit{orbitNb}_SMinA']())
                startTA = 0
                endTA = 2*math.pi

                self.secondaryOrbitsFigure[f'orbit{orbitNb}_vertices'] = Orb.getEllipseVertices(-200+offset,0, SMajA*zoom,SMinA*zoom, startTA, endTA)
                
                
            elif str(timeToSOIChange) != 'nan': #ORBIT IS NOT AN ELLIPSE OR VESSEL IS GOING TO CHANGE SOI
                startTA = streams.trueAnomalyAt(self.UT+timeToSOIEnter)
                endTA = streams.trueAnomalyAt(self.UT+timeToSOIChange)
                if endTA < startTA:
                    endTA += 2*math.pi

                self.secondaryOrbitsFigure[f'orbit{orbitNb}_vertices'] = Orb.getHyperbolaVertices(-200+offset,0, eccentricity, SMajA*zoom, periapsis*zoom, startTA, endTA)

            self.secondaryOrbitsFigure[f'orbit{orbitNb}_figure'].re_init(pts = self.secondaryOrbitsFigure[f'orbit{orbitNb}_vertices'])
            self.secondaryOrbitsFigure[f'orbit{orbitNb}_figure'].draw()


        def draw(self, zoom, streams, planets): 

            #---------- DRAW THE MAIN ORBIT ----------
            if self.type == "main":
                self.bodyOrbiting = streams.bodyOrbiting()
                self.periapsis = int(streams.vesselPeriapsis())
                self.SMajA = int(streams.vesselSMajA())          
                self.eccentricity = float(streams.vesselEccentricity())
                self.bodyOrbitingRadius = int(streams.bodyOrbitingRadius)            
                vesselTimeToSOIChange = streams.vesselTimeToSOIChange()
                self.rotation = 0
                self.positionX = 0
                self.positionY = 0
            
            elif self.type == "node":
                orbit = streams.nodesOrbits[f'nodeOrbit0']()
                orbitInfo.nodeEccentricAnomaly = streams.eccentricAnomalyAt(streams.nodesOrbits[f'nodeOrbit0_ut']())
                self.bodyOrbiting = orbit.body.name
                self.periapsis = int(orbit.periapsis_altitude)
                self.SMajA = int(orbit.semi_major_axis)          
                self.eccentricity = float(orbit.eccentricity)
                self.bodyOrbitingRadius = int(orbit.body.equatorial_radius)            
                vesselTimeToSOIChange = orbit.time_to_soi_change

                self.rotation = orbitInfo.nodeEccentricAnomaly
                self.positionX = -200
                self.positionY = 0

            self.UT = int(streams.UT())

            if self.eccentricity < 1 and str(vesselTimeToSOIChange) == 'nan': #ORBIT IS AN ELLIPSE
                self.apoapsis = int(streams.vesselApoapsis())
                self.SMinA = int(streams.vesselSMinA())
                startTA = 0
                endTA = 2*math.pi
                orbitInfo.vertices = Orb.getEllipseVertices(-200,0, self.SMajA*zoom,self.SMinA*zoom, startTA, endTA)
                
            elif self.eccentricity < 1 and str(vesselTimeToSOIChange) != 'nan': #ORBIT IS AN ELLIPSE AND VESSEL IS GOING TO CHANGE SOI
                self.apoapsis = int(streams.vesselApoapsis())
                self.SMinA = int(streams.vesselSMinA())
                startTA = streams.eccentricAnomalyAt(self.UT)
                endTA = streams.eccentricAnomalyAt(self.UT+vesselTimeToSOIChange)
                if endTA < startTA:
                    endTA += 2*math.pi
                orbitInfo.vertices = Orb.getEllipseVertices(-200,0, self.SMajA*zoom,self.SMinA*zoom, startTA, endTA)

            elif self.eccentricity > 1 and str(vesselTimeToSOIChange) != 'nan': #ORBIT IS NOT AN ELLIPSE AND VESSEL IS GOING TO CHANGE SOI
                self.apoapsis = 0
                self.SMinA = 0
                startTA = streams.trueAnomalyAt(self.UT)
                endTA = streams.trueAnomalyAt(self.UT+vesselTimeToSOIChange)
                if endTA < startTA:
                    endTA += 2*math.pi
                orbitInfo.vertices = Orb.getHyperbolaVertices(-200,0, self.eccentricity, self.SMajA*zoom, self.periapsis*zoom, startTA, endTA)

            orbitInfo.apoapsis = self.apoapsis
            orbitInfo.periapsis = self.periapsis
            
            self.orbit.re_init(pts = orbitInfo.vertices)
            self.orbit.position(self.positionX, self.positionY, 0)
            self.orbit.rotateToZ(math.degrees(self.rotation))
            self.orbit.draw()

            #---------- TRY ANY SECONDARY ORBITS ----------

            if hasattr(streams, 'secondaryOrbits'):
                numberOfOrbits = streams.secondaryOrbits[f'numberOfOrbits']+1
            else:
                numberOfOrbits = 1

            if numberOfOrbits != self.prevNumberOfOrbits: #IF NEW, CREATE THE ORBITS
                if numberOfOrbits != 1: 
                    orbitNb = 1
                    self.secondaryOrbitsFigure = {}
                    for orbit in range(int((len(streams.secondaryOrbits)-1)/8)):
                        self.createNewOrbit(orbitNb)
                        orbitNb += 1
                
                else: 
                    del self.secondaryOrbitsFigure

            self.prevNumberOfOrbits = numberOfOrbits

            #---------- IF THEY EXIST, DRAW THEM ----------

            if hasattr(self, 'secondaryOrbitsFigure'):
                orbitNb = 1
                for orbit in range(int((len(streams.secondaryOrbits)-1)/8)):
                    if str(streams.secondaryOrbits[f'orbit{orbitNb}_body']()) == str(self.bodyOrbiting):
                        self.drawSecondaryOrbits(zoom, 0, streams, orbitNb)
                        
                    else:
                        if hasattr(planets, 'targetBodyName'):
                            if str(streams.secondaryOrbits[f'orbit{orbitNb}_body']()) == str(planets.targetBodyName):
                                self.drawSecondaryOrbits(zoom, planets.targetBodyOffset+(planets.targetBodyRadius*zoom)+(planets.mainBodyRadius*zoom), streams, orbitNb)
                    
                    orbitNb += 1


        def getBounds(self):
            bounds = []
            temp = self.orbit.get_bounds()    
            bounds.append(abs(temp[0])+abs(temp[3]))
            bounds.append(abs(temp[1])+abs(temp[4]))
            return bounds    

    class Icons:
        def __init__(self, controller, streams):
            self.controller = controller

            self.ship_marker = pi3d.Plane(w=55, h=55, x=-200, y=0)
            self.ship_texture = pi3d.Texture('assets/ship_marker.png')

            self.apoapsis_marker = pi3d.Plane(w=50, h=55, x=-200, y=0)
            self.apoapsis_texture = pi3d.Texture('assets/apoapsis_marker.png')

            self.periapsis_marker = pi3d.Plane(w=50, h=55, x=-200, y=0)
            self.periapsis_texture = pi3d.Texture('assets/periapsis_marker.png')

            self.node_marker = pi3d.Plane(w=50, h=55, x=-200, y=0)
            self.node_marker.set_material(orange)
            self.node_texture = pi3d.Texture('assets/manoeuver_marker.png')

        def draw(self, zoom, streams):
            self.bodyOrbiting = streams.bodyOrbiting()
            self.periapsis = int(streams.vesselPeriapsis())
            self.SMajA = int(streams.vesselSMajA())          
            self.eccentricity = float(streams.vesselEccentricity())
            self.bodyOrbitingRadius = int(streams.bodyOrbitingRadius)
            self.UT = int(streams.UT())
            self.eccentricAnomaly = float(streams.vesselEccentricAnomaly())
            vesselTimeToSOIChange = streams.vesselTimeToSOIChange()

            if self.eccentricity < 1 and str(vesselTimeToSOIChange) == 'nan': #ORBIT IS AN ELLIPSE

                #------SHIP ICON------
                self.apoapsis = int(streams.vesselApoapsis())
                self.SMinA = int(streams.vesselSMinA())

                shipPosX = self.SMajA*math.cos(self.eccentricAnomaly)
                shipTranslateX = shipPosX*zoom
                shipPosY = self.SMinA*math.sin(self.eccentricAnomaly)
                shipTranslateY = shipPosY*zoom

                #------APOAPSIS ICON------
                
                apoapsisTranslateX = -200-self.SMajA*zoom
                apoapsisTranslateY = 0
                    

                #------PERIAPSIS ICON------
                
                periapsisTranslateX = -200+self.SMajA*zoom
                periapsisTranslateY = 0

                #------NODE ICON------
                if streams.nodesNb > 0: 
                    eccentricAnomaly = orbitInfo.nodeEccentricAnomaly
                    
                    nodePosX = self.SMajA*math.cos(eccentricAnomaly)
                    nodeTranslateX = nodePosX*zoom
                    nodePosY = self.SMinA*math.sin(eccentricAnomaly)
                    nodeTranslateY = nodePosY*zoom

                    self.node_marker.positionX(-200+nodeTranslateX)
                    self.node_marker.positionY(nodeTranslateY)
                    self.node_marker.scale(zoom*1500, zoom*1500, 1)
                    self.node_marker.draw(self.controller.shader, [self.node_texture])


                    
                    
               
                
            elif self.eccentricity < 1 and str(vesselTimeToSOIChange) != 'nan': #ORBIT IS AN ELLIPSE AND VESSEL IS GOING TO CHANGE SOI
                self.apoapsis = int(streams.vesselApoapsis())
                self.SMinA = int(streams.vesselSMinA())
             

            elif self.eccentricity > 1 and str(vesselTimeToSOIChange) != 'nan': #ORBIT IS NOT AN ELLIPSE AND VESSEL IS GOING TO CHANGE SOI
                pass

            

            self.ship_marker.positionX(-200+shipTranslateX)
            self.ship_marker.positionY(shipTranslateY)
            self.ship_marker.scale(zoom*1500, zoom*1500, 1)
            self.ship_marker.draw(self.controller.shader, [self.ship_texture])
            
            if self.apoapsis > 0:
                self.apoapsis_marker.positionX(apoapsisTranslateX)
                self.apoapsis_marker.positionY(apoapsisTranslateY)
                self.apoapsis_marker.scale(zoom*1000, zoom*1000, 1)
                self.apoapsis_marker.draw(self.controller.shader, [self.apoapsis_texture])
            
            if self.periapsis > 0:
                self.periapsis_marker.positionX(periapsisTranslateX)
                self.periapsis_marker.positionY(periapsisTranslateY)
                self.periapsis_marker.scale(zoom*1000, zoom*1000, 1)
                self.periapsis_marker.draw(self.controller.shader, [self.periapsis_texture])


    def show(self, streams, first_call, encoder=0):
        self.controller.DISPLAY.clear()
        if first_call:
            self.controller.DISPLAY.add_sprites(self.back)
            self.planets = self.Planets(self.controller, streams)
            self.icons = self.Icons(self.controller, streams)
            
            

        #------------ ZOOM ----------------------

        orbitSizeOnScreen = self.orbit.getBounds()

        if orbitSizeOnScreen[0] > 750 or orbitSizeOnScreen[1] > 650:
            self.numericZoom -= 1

        temp = encoder.getValue()
        temp += self.numericZoom         

        if temp < 0:
            self.zoom = 1/math.exp(-temp/20)
        elif temp > 0:
            self.zoom = math.exp(temp/20)
        else:
            self.zoom = 1

        self.zoom = self.zoom/2500

        #------------ ICONS -------------------

        self.icons.draw(self.zoom, streams)
        #------------ SHIP ORBIT -------------------
        orbitInfo.inclination = float(math.degrees(streams.vesselInclination()))
        orbitInfo.eccentricAnomaly = float(streams.vesselEccentricAnomaly())
        if not math.isinf(streams.vesselTimeToApoapsis()):
            orbitInfo.time_to_apoapsis = str(timedelta(seconds=int(streams.vesselTimeToApoapsis())))
        else:
            orbitInfo.time_to_apoapsis = "N/A"

        if not math.isinf(streams.vesselTimeToPeriapsis()) and streams.vesselTimeToPeriapsis() >= 0:
            orbitInfo.time_to_periapsis = str(timedelta(seconds=int(streams.vesselTimeToPeriapsis())))
        else:
            orbitInfo.time_to_periapsis = "N/A"

        self.orbit.draw(self.zoom, streams, self.planets)

        #------------ NODES ----------------------

        if self.prevNodes != streams.nodesNb: #IF UPDATE OF THE NODES, CREATE NEW ASSETS
            if streams.nodesNb > 0:
                self.nodeOrbit = self.Orbit(self.controller, orange, "node")
                print("created node orbit")
            else:
                del self.nodeOrbit 
                print("deleted node orbit")

        if streams.nodesNb > 0 : #IF ASSETS EXISTS, DRAW THEM
            self.nodeOrbit.draw(self.zoom, streams, self.planets)


        self.prevNodes = streams.nodesNb
        

        #------------ PLANETS ----------------------
        self.planets.draw(self.zoom, streams)

        #------------ TEXT ----------------------
        self.text.regen()
        self.text.draw()

        

            
        

    def remove_sprite(self):
        self.controller.DISPLAY.remove_sprites(self.back)




        
        
        