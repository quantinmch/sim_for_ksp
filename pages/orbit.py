
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

class OrbitInfo(object):
    apoapsis = 0
    time_to_apoapsis = "N/A"
    periapsis = 0
    time_to_periapsis = "N/A"
    inclination = 0
    SMinA = 0
    SMajA = 0
    bodyOrbitingRadius = 1
    eccentric_anomaly = 0

orbitInfo = OrbitInfo()



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

        self.Kerbin = self.Planet(self.controller)
        self.orbit = self.Orbit(self.controller, blue)

    class Planet:
        def __init__(self, controller):
            self.controller = controller
            self.planet_figure = pi3d.Plane(w=500, h=500, x=-200, y=0)
            self.orbit_draw = pi3d.Texture('assets/orbit_draw.png')

        def draw(self, zoom, orbite):
            self.vesselPeriapsis = orbite.periapsis
            self.vesselSMajA = orbite.SMajA
            self.vesselBodyOrbitingRadius = orbite.bodyOrbitingRadius
            
            translateX = ((self.vesselSMajA-self.vesselBodyOrbitingRadius-self.vesselPeriapsis)*250*zoom)/self.vesselBodyOrbitingRadius
            self.planet_figure.positionX(-200-translateX)

            self.planet_figure.scale(zoom, zoom, 1)
            self.planet_figure.draw(self.controller.flatsh, [self.orbit_draw])

    class Orbit:
        def __init__(self, controller, color):
            self.controller = controller

            self.orbit_figure = pi3d.Plane(w=500, h=500, x=-200, y=0)
            self.orbit_draw = pi3d.Texture('assets/orbit_draw.png')
            self.orbit_figure.set_material(color)

            self.apoapsis_marker = pi3d.Plane(w=50, h=55, x=-200, y=0)
            self.apoapsis_texture = pi3d.Texture('assets/apoapsis_marker.png')

            self.periapsis_marker = pi3d.Plane(w=50, h=55, x=-200, y=0)
            self.periapsis_texture = pi3d.Texture('assets/periapsis_marker.png')

        def draw(self, zoom, orbite):
            self.apoapsis = orbite.apoapsis
            self.periapsis = orbite.periapsis
            self.SMajA = orbite.SMajA
            self.SMinA = orbite.SMinA
            self.bodyOrbitingRadius = orbite.bodyOrbitingRadius
            

            if self.apoapsis > 0:
                translateX = (self.SMajA*250*zoom)/self.bodyOrbitingRadius
                self.apoapsis_marker.positionX(-200+translateX)
                self.apoapsis_marker.scale(zoom, zoom, 1)
                self.apoapsis_marker.draw(self.controller.shader, [self.apoapsis_texture])

            if self.periapsis > 0:
                translateX = (self.SMajA*250*zoom)/self.bodyOrbitingRadius
                self.periapsis_marker.positionX(-200-translateX)
                self.periapsis_marker.scale(zoom, zoom, 1)
                self.periapsis_marker.draw(self.controller.shader, [self.periapsis_texture])

            ratioX = self.SMajA/self.bodyOrbitingRadius
            ratioY = self.SMinA/self.bodyOrbitingRadius

            self.orbit_figure.scale(zoom*ratioX, zoom*ratioY, 1)
            self.orbit_figure.draw(self.controller.shader, [self.orbit_draw])

    def show(self, streams, first_call, encoder):
        self.controller.DISPLAY.clear()
        if first_call:
            self.controller.DISPLAY.add_sprites(self.back)

        orbitInfo.apoapsis = int(streams.vesselApoapsis())
        orbitInfo.periapsis = int(streams.vesselPeriapsis())
        orbitInfo.inclination = float(math.degrees(streams.vesselInclination()))
        orbitInfo.SMajA = int(streams.vesselSMajA())
        orbitInfo.SMinA = int(streams.vesselSMinA())
        orbitInfo.bodyOrbitingRadius = int(streams.bodyOrbitingRadius)
        self.eccentricAnomaly = float(streams.vesselEccentricAnomaly())

        orbitInfo.time_to_apoapsis = str(timedelta(seconds=int(streams.vesselTimeToApoapsis())))
        orbitInfo.time_to_periapsis = str(timedelta(seconds=int(streams.vesselTimeToPeriapsis())))

        shipPosX = orbitInfo.SMajA*math.cos(self.eccentricAnomaly)
        translateX = (shipPosX*250*self.zoom)/orbitInfo.bodyOrbitingRadius
        shipPosY = orbitInfo.SMinA*math.sin(self.eccentricAnomaly)
        translateY = (shipPosY*250*self.zoom)/orbitInfo.bodyOrbitingRadius

        self.ship_marker.positionX(-200-translateX)
        self.ship_marker.positionY(-translateY)
        self.ship_marker.scale(self.zoom, self.zoom, 1)
        self.ship_marker.draw(self.controller.shader, [self.ship_texture])

        self.Kerbin.draw(self.zoom, orbitInfo)
        self.orbit.draw(self.zoom, orbitInfo)
        
        self.text.regen()
        self.text.draw()

        temp = encoder.getValue()
        if temp < 0:
            self.zoom = 1/math.exp(-temp/20)
        elif temp > 0:
            self.zoom = math.exp(temp/20)
        else:
            self.zoom = 1

    def remove_sprite(self):
        self.controller.DISPLAY.remove_sprites(self.back)




        
        
        