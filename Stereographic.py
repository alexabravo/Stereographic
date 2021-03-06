import struct
from math import tan, pi 
from Funciones import *
from FuncionesM import *
from collections import namedtuple

MAX_RECURSION_DEPTH = 3

class Raytracer(object):

    def __init__(self, filename):
      self.scene = []
      self.width = 0
      self.height = 0
      self.xVP = 0
      self.yVP= 0
      self.hPV = 0
      self.wVP = 0
      self.glClear()
      self.light = None
      self.framebuffer = []
      self.filename = filename
      self.clear_color = color(0, 0, 51)

    def glClear(self):
      self.framebuffer = [[self.clear_color for x in range(self.width)] for y in range(self.height)]
      self.zbuffer = [[-float('inf') for x in range(self.width)] for y in range(self.height)]

    def glpoint(self, x, y):
      self.framebuffer[y][x] = self.clear_color

    def glCreateWindow(self, width, height):
      self.width = width
      self.height = height

    def writebmp(self):
        
      f = open(self.filename, 'bw')
      f.write(char('B'))
      f.write(char('M'))
      f.write(dword(14 + 40 + self.width * self.height * 3))
      f.write(dword(0))
      f.write(dword(14 + 40))

      f.write(dword(40))
      f.write(dword(self.width))
      f.write(dword(self.height))
      f.write(word(1))
      f.write(word(24))
      f.write(dword(0))
      f.write(dword(self.width * self.height * 3))
      f.write(dword(0))
      f.write(dword(0))
      f.write(dword(0))
      f.write(dword(0))

      for x in range(self.height):
        for y in range(self.width):
          f.write(self.framebuffer[x][y].toBytes())
      f.close()

    def glFinish(self):
      self.writebmp()

    def cast_ray(self, orig, direction, recursion=0):
      material, impact = self.scene_intersect(orig, direction)

      if material is None or recursion >= MAX_RECURSION_DEPTH:  
        return self.clear_color

      offset_normal = mul(impact.normal, 1.1)

      if material.albedo[2] > 0:
        reverse_direction = mul(direction, -1)
        reflected_dir = reflect(reverse_direction, impact.normal)
        reflect_orig = sub(impact.point, offset_normal) if dot(reflected_dir, impact.normal) < 0 else sum(
          impact.point, offset_normal)
        reflected_color = self.cast_ray(reflect_orig, reflected_dir, recursion + 1)
      else:
        reflected_color = color(0, 0, 0)

      if material.albedo[3] > 0:
        refract_dir = refract(direction, impact.normal, material.refractive_index)
        refract_orig = sub(impact.point, offset_normal) if dot(refract_dir, impact.normal) < 0 else sum(
          impact.point, offset_normal)
        refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
      else:
        refract_color = color(0, 0, 0)



      light_dir = norm(sub(self.light.position, impact.point))
      light_distance = length(sub(self.light.position, impact.point))

      shadow_orig = sub(impact.point, offset_normal) if dot(light_dir, impact.normal) < 0 else sum(
        impact.point, offset_normal)
      shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
      shadow_intensity = 0

      if shadow_material and length(sub(shadow_intersect.point, shadow_orig)) < light_distance:
        shadow_intensity = 0.9

      intensity = self.light.intensity * max(0, dot(light_dir, impact.normal)) * (1 - shadow_intensity)

      reflection = reflect(light_dir, impact.normal)
      specular_intensity = self.light.intensity * (
              max(0, -dot(reflection, direction)) ** material.spec
      )

      diffuse = material.diffuse * intensity * material.albedo[0]
      specular = color(255, 255, 255) * specular_intensity * material.albedo[1]
      reflection = reflected_color * material.albedo[2]
      refraction = refract_color * material.albedo[3]

      return diffuse + specular + reflection + refraction


    def scene_intersect(self, orig, dir):
      zbuffer = float('inf')
      material = None
      intersect = None

      for obj in self.scene:
        hit = obj.ray_intersect(orig, dir)
        if hit is not None:
          if hit.distance < zbuffer:
            zbuffer = hit.distance
            material = obj.material
            intersect = hit

      return material, intersect

    def StereographicRender(self,this = False):
      fov = int(pi / 2)
      
      for y in range(self.height):
          
        for x in range(self.width):
          i = (2 * (x + 0.5) / self.width - 1) * tan(fov / 2) * self.width / self.height
          j = (2 * (y + 0.5) / self.height - 1) * tan(fov / 2)
          direction = norm(V3(i, j, -1))
          
          if (this):
            rougeb = self.cast_ray(V3(0.35, 0, 0), direction)
            bleub = self.cast_ray(V3(-0.35, 0, 0), direction)
            
            if not rougeb.equals(self.clear_color):rougeb = rougeb * 0.55 + color(100, 0, 0)
            if not bleub.equals(self.clear_color):bleub = bleub * 0.55 + color(0, 0, 100)
            
            ours = rougeb + bleub
            self.framebuffer[y][x] = ours
            
          else:
            self.framebuffer[y][x] = self.cast_ray(V3(1, 0, 0), direction)


#Create ---------------------------------------------------------
ivory = Material(diffuse=color(100, 100, 80), albedo=(0.6, 0.3, 0.1, 0), spec=50)
rubber = Material(diffuse=color(80, 0, 0), albedo=(0.9, 0.1, 0, 0, 0), spec=10)
mirror = Material(diffuse=color(255, 255, 255), albedo=(0, 10, 0.8, 0), spec=1425)
glass = Material(diffuse=color(150, 180, 200), albedo=(0, 0.5, 0.1, 0.8), spec=125)

cafe = Material(diffuse=color(186,91,41), albedo=(0.9, 0.1, 0, 0, 0),spec=10)
cafeleger = Material(diffuse=color(235,169,133), albedo=(0.9, 0.1, 0, 0, 0),spec=11)

r = Raytracer('Ositooo.bmp')
r.glCreateWindow(800,600)
r.glClear()

r.light = Light(
  position=V3(-20, 20, 20),
  intensity=1.5
)


r.scene = [
    #Cabeza
    Sphere(V3(0, 2.0, -10), 1.5, cafeleger),
    Sphere(V3(0, 1.4, -8), 0.5, cafe),
    Sphere(V3(-1, 3.5, -10), 0.7, cafe),
    Sphere(V3(1.5, 3.5, -10), 0.7, cafe),
    Sphere(V3(-0.5, 2.0, -8), 0.125, rubber),
    Sphere(V3(0.5, 2.0, -8), 0.125, rubber),
    Sphere(V3(0, 1.5, -7), 0.125, rubber), 

    #Cuerpo
    Sphere(V3(0, -0.8, -11), 1.7, rubber),
    Sphere(V3(1.5, -0.1, -10), 0.75, cafeleger),
    Sphere(V3(-1.65, -0.1, -10), 0.75, cafeleger),
    Sphere(V3(1.25, -2.2, -10), 0.75, cafeleger),
    Sphere(V3(-1.5, -2.2, -10), 0.75, cafeleger),
    ]

r.StereographicRender(True)
r.glFinish()
