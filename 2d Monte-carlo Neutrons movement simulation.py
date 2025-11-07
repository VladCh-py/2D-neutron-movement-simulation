'''
 Программа позволяет моделировать движение нейтронов в 2D-пространстве с тремя средами:
  1. environment - среда с поглощением и рассеянием;
  2. reflector (отражатель) - область, с большим сечением рассеяния*;
  3. vacuum (вакуум) - среда с пренебрежимо малыми коэффициентами поглощения и рассеивания.
 Нейтроны рождены со случайной позицией и случайным направлением внутри заданной среды.
При рождении нейтрона генерируется его свободный пробег(из экспоненциального закона). Нейтрона движется прямолинейно 
весь свободный пробег. После этого рассчитывается вероятность возможных исходов(поглощение/рассеяние 
на случайный угол относительно предыдущего движения) и разыгрывается взаимодействие. Во время работы программы выводится 
движение нейтронов в средах и гистограмма отображающая поток 
(расчитывается как количество нейтронов в единице площади) нетронов по оси абсцисс.


*В данной версии возможно использовать отражатель другим образом: Если раскомментировать куски кода, приведенные ниже, нейтрон может отражаться от отражателя
абсолютно упруго(с сохранением равенства углов падения и отражения).

'''

import pygame                               # для отображения симуляции
from math import *                          # содержит необходимые математические операции
import matplotlib.pyplot as plt             # отображение гистограммы
import random as rnd                        # генерация случайных величин
import shapely.geometry as gmt              # работа с геометрией
from shapely.ops import nearest_points
ax = plt.subplots()[1]
import keyboard                             # обработка нажатий с клавиатуры


# начало работы PyGame
pygame.init()
# геометрические параметры окна
L = 100
width0 = 800
height0 = 700
width = width0
height = height0
win = pygame.display.set_mode((width0, height0))

color = (255, 255, 255)

dt = 0.1
m1 = 1
r1 = 3
Charge = 0
positive_percent = 50
k = 9
MAX_iterations = 10000

particles = []
running = True
animation=True
iterations = 0

# Функция, позволяющая прекращать выполнение программы при закрытии окна Пайгейм
def check_stop_PyGame():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            global running
            running = False


# функция спавна нейтронов. Принимает среду, в которой нейтрон необходимо заспавнить и его скорость(модуль)

def spawn_neutron(env, speed):

    
    # Выбираем случайным образом точку внутри области. Для этого опрделяем максимальные координаты области и в этих пределах ставим случайным образом точки
    # если точка попала в область, спавним нейтрон в ней. если не попала, ищем другую, пока не попадем.
    minx, miny, maxx, maxy = env.area.bounds
    while True:
        x = rnd.uniform(minx, maxx)         #выбор координат случайным образом
        y = rnd.uniform(miny, maxy) 
        point = gmt.Point(x, y)             #создаем объект Point, принадлежащий библиотеке Shaptly. Это позволит упростить работу с ним в дальнейшем        
        if point.within(env.area):          #с помощью встроенного метода библиотеки Шейпли проверяем, что точка попадает в нужную область
            break

    # выбор случайного направления угла. Модуль скорости задается параметром, приниммаемом функцией
    angle = rnd.uniform(0, 2 * pi)
    velocity_x = speed * cos(angle)
    velocity_y = speed * sin(angle)
    #создается объект класса Neuton и возвращается в качестве результата работы 
    neutron = Neutron(
        radius=3,
        mass=1,
        x=x,
        y=y,
        velocity_x=velocity_x,
        velocity_y=velocity_y,
        color=(0, 255, 0),
        Enviroment=env,
    )
    return neutron
# вспомогательная функция присваивания цвета частице в зависимости от ее заряда(в данной версии программы не используется)
def assignment_color(charge, color):
    if charge < 0:
        participle_color = (0, 0, 255)
    else:
        participle_color = (255, 0, 0)
    if color == (0, 255, 0):
        participle_color = (0, 255, 0)
    if charge == 0:
        participle_color = (125, 125, 255)
    return participle_color

# функция позволяющая завершить программу клавишей esc
def STOP():
    global running
    running = False
keyboard.add_hotkey("esc", STOP)

# класс отвечающий за среду. Содержит все необходимые параметры (сечения, цвет, область) и функцию отрисовки с помощью PyGame
class Enviroment:
    def __init__(self, area, Sigma_a=0, Sigma_s=0, color=(0, 0, 0), reflective=False, vacuum=False):
        """
        area — объект shapely (Polygon, Point.buffer и т.п.)
        Sigma_a, Sigma_s — макросечения (поглощение и рассеяние)
        color — цвет при визуализации
        reflective, vacuum — флаги среды. содержат вспомогательную информацию
        """
        self.area = area
        self.Sigma_a = Sigma_a
        self.Sigma_s = Sigma_s
        self.color = color

    # вспомогательная функцию позволяющая извлечь координаты точек внешней и внутренней границ области
    def poly_to_int_points(self, poly):
        
        exterior = [(int(x), int(y)) for x, y in poly.exterior.coords]
        interiors = [[(int(x), int(y)) for x, y in interior.coords] for interior in poly.interiors]
        return exterior, interiors
    
    # функция рисующая области с помощью ПайГейма
    def draw(self, surface, background_color=(30,30,30)):
    
        geom = self.area
        if isinstance(geom, gmt.MultiPolygon):# сначала проверяем соответствие класса объекта классу MultiPolygon из Shapely. это нужно для  корректной отрисовки
            for poly in geom.geoms:
                ext, ints = self.poly_to_int_points(poly)
                pygame.draw.polygon(surface, self.color, ext)
                for interior in ints:
                    pygame.draw.polygon(surface, background_color, interior)
            return

        # 
        if isinstance(geom, gmt.Polygon):# сначала проверяем соответствие класса объекта классу Polygon из Shapely. это нужно для  корректной отрисовки
            ext, ints = self.poly_to_int_points(geom)
            pygame.draw.polygon(surface, self.color, ext)
            for interior in ints:
                pygame.draw.polygon(surface, background_color, interior)
            return

# класс Particle. Родительский класс для класса Neutron. поддерживает работу с частицами с зарядом. В данной версии программы из него используются только хранящиеся параметры.
# все нужные функции реализованы отдельно в классе Neutron
class Particle:
    #задаем параметры
    def __init__(self, mass, radius, charge, x, y, velocity_x, velocity_y, free_way, color):
        self.color = assignment_color(charge, color)
        self.free_way = free_way
        self.radius = radius
        self.mass = mass
        self.charge = charge
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
#не используется в данной версии программы
    def update_Position(self):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
#не используется в данной версии программы
    def update_Velocity(self, other):
        r_x = other.x - self.x
        r_y = other.y - self.y

        dobavka_k_rasstoyaniyu = 0.1
        distance = (r_x ** 2 + r_y ** 2) ** 0.5 + dobavka_k_rasstoyaniyu
        if distance == 0:
            return
        force_magnitude = -k * (self.charge * other.charge) / distance ** 2
        force_x = force_magnitude * (r_x / distance)
        force_y = force_magnitude * (r_y / distance)

        acceleration_x = force_x / self.mass
        acceleration_y = force_y / self.mass
        self.velocity_x += acceleration_x * dt
        self.velocity_y += acceleration_y * dt

        other.velocity_x += -dt * force_x / other.mass
        other.velocity_y += -dt * force_y / other.mass


# класс Neutron. Дочерний класс от Particle. содержит все необходимые параметры(масса, радиус, координаты, составляющие скорости (х и у), цвет и среду в которой он находится)
class Neutron(Particle):
    def __init__(self, mass, radius, x, y, velocity_x, velocity_y, color, Enviroment):
        super().__init__(mass, radius, charge=0, x=x, y=y, velocity_x=velocity_x, velocity_y=velocity_y, free_way=0, color=color)
        self.absorbed = False
        self.lost_in_vacuum = False
        self.alive=True
        self.Enviroment=Enviroment
        self.lambda_free=-log(rnd.random()) / (self.Enviroment.Sigma_a + self.Enviroment.Sigma_s)# основываясь на сечениях поглощения и рассеяания среды, в которой находится нейтрон, рассчитываем  длину свободного пробега

    # функция перемещения нейтрона на путь пройденный за время dt
    def update_Position(self):

        new_x=self.x + self.velocity_x * dt
        new_y=self.y + self.velocity_y * dt
        # рассчитаные новые координаты помещаем в класс "точка" библиотеки Шейпли.
        new_neutron_point = gmt.Point(new_x, new_y)
        # увеличиваем уже пройденный на еще один пройденный отрезок
        self.free_way += sqrt((self.velocity_x * dt) ** 2 + (self.velocity_y * dt) ** 2)
        
        # если уже пройденный путь оказался больше рассчитаного свободного пути, разыгрываем взаимодействие нейтрона
        if self.free_way >= self.lambda_free:
            self.interaction(self.Enviroment.Sigma_a, self.Enviroment.Sigma_s)
            self.free_way=0 # обнуляем уже пройденный путь до взаимодействия
            
        # проверяем, находится ли нейтрон после проходения отрезка за dt в этой же среде
        if not self.Enviroment.area.covers(new_neutron_point):
            self.Enviroment=self.determine_environment(ENVIRONMENTS_LIST, new_neutron_point) # если нейтрон вылетел из текущей среды, определяем новую среду и рассчитываем новый свободный пробег
            self.lambda_free=-log(rnd.random()) / (self.Enviroment.Sigma_a + self.Enviroment.Sigma_s)
            
        # отражение от верхней и нижней стен окна. Вспомогательная функция. Позволяет ограничить область симуляции сверху и снизу. Не исползуется в данной программе
        # if self.y + r1 >= height or self.y - r1 <= 0:
        #     self.velocity_y = -self.velocity_y

        # перемещаем нейтрон в новую точку
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

    # вспомогательная функция определения типа взаимодействия нейтрона с веществом.
    # если Sigma_s / (Sigma_a + Sigma_s) > случайно выбранная вероятность [0,1], то происходит рассеивание; иначе- поглощение
    def interaction(self, Sigma_a, Sigma_s):
        if Sigma_s / (Sigma_a + Sigma_s) > rnd.uniform(0, 1):
            # при рассеивании разыгрываем новое направление движения
            angle = rnd.uniform(0, 2 * pi)
            self.velocity_x = speed * cos(angle)
            self.velocity_y = speed * sin(angle)
            self.lambda_free=-log(rnd.random()) / (Sigma_a + Sigma_s)

        else: 
            # если произошло  поглощение, окрашиваем нейтрон в белый цвет и ставим флаг, что нейтрон больше не живет
            self.alive = False
            self.color=(255,255,255)
    # вспомогательная функция определения среды, в которой находится нейтрон. Принимает список сред и положение нейтрона
    def determine_environment(self, env_list, neutron_point):
        for env in env_list:
            # если среда определена, возвращаем ее
            if env.area.covers(neutron_point): return env

        # если среда не определена, то, возможно, из-за грубого задания границ сред, нейтрон попал на граничную точку, не принадлежащую ни одной из областей.
        # из-за этого среда не определена.

        # рассчитываем направляющие косинусы направления движения 
        vnorm = sqrt(self.velocity_x**2 + self.velocity_y**2)
        if vnorm > 0:
            ux = self.velocity_x / vnorm
            uy = self.velocity_y / vnorm
        else:
            ux, uy = 0.0, 0.0

        # берем маленький шаг shift, смещаем на него нейтрон и оаределяем, в какой среде нейтрон оказался
        for i in range(1, 10+1):
            shift = 1e-5 * i
            # вперед
            p_fw = gmt.Point(neutron_point.x + ux * shift, neutron_point.y + uy * shift)
            for env in env_list:
                if env.area.covers(p_fw) or env.area.touches(p_fw):
                    return env
            # назад
            p_bw = gmt.Point(neutron_point.x - ux * shift, neutron_point.y - uy * shift)
            for env in env_list:
                if env.area.covers(p_bw) or env.area.touches(p_bw):
                    return env

        #если прошлые действия не помогли определить среду нейтрона, то просто вернём ближайшую среду по расстоянию до её границы

        best_env = None
        best_dist = float('inf')
        for env in env_list:
            # distance до area (возвращает 0 если внутри/на границе)
            d = env.area.distance(neutron_point)
            if d < best_dist:
                best_dist = d
                best_env = env
        if best_env is not None:
            return best_env

        # если среда все еще не определена, выдаем ошибку(вспомогательное действие, нужное для отладки программы)
        raise ValueError(f"Neutron at ({neutron_point.x:.6f}, {neutron_point.y:.6f}) is outside all environments")


    # как было пояснено ранее, эта функция позволяет нейтрону взаимодействовать с границей отражателя абсолютно упруго, с 
    # сохранением равенства угла падения и отражения. Такое взаимодействие менее физично, чем представленное, но если необходимо,
    # расскоментировать данную часть.
     
    # def reflect_neutron(self, area):
    #     """
    #     Отражает нейтрон от ближайшей границы Shapely-области.
    #     area - объект Polygon или MultiPolygon (с дырками)
    #     neutron - объект с атрибутами x, y, vx, vy
    #     """
    #     p = gmt.Point(self.x, self.y)

    #     # Все границы: exterior + interiors (если есть)
    #     if area.geom_type == "Polygon":
    #         boundaries = [area.exterior] + list(area.interiors)
    #     elif area.geom_type == "MultiPolygon":
    #         boundaries = []
    #         for poly in area.geoms:
    #             boundaries.append(poly.exterior)
    #             boundaries.extend(poly.interiors)
    #     else:
    #         raise ValueError("Неизвестный тип геометрии: " + area.geom_type)

    #     # Находим ближайшую точку на границе
    #     nearest_point = min(
    #         [nearest_points(p, b)[1] for b in boundaries],
    #         key=lambda pt: p.distance(pt)
    #     )

    #     # Нормаль к границе
    #     nx = self.x - nearest_point.x
    #     ny = self.y - nearest_point.y
    #     norm = sqrt(nx**2 + ny**2)
    #     if norm == 0:
    #         nx, ny = 1.0, 0.0
    #         norm = 1.0
    #     nx /= norm
    #     ny /= norm

    #     # Отражение скорости
    #     v_dot_n = self.velocity_x * nx + self.velocity_y * ny
    #     self.velocity_x -= 2 * v_dot_n * nx
    #     self.velocity_y -= 2 * v_dot_n * ny

# Создание геометрических областей
core_area = gmt.Polygon([(100, 0), (100, 700), (700, 700), (700, 0)])  # активная зона
reflector_area = gmt.Polygon([(0, 0), (100, 0), (100, 700), (0, 700)])  # отражатель
vacuum_area = gmt.Polygon([(700, 0), (800, 0), (800, 700), (700, 700)])  # вакуум


# круглая область:
# core_area = gmt.Point(400, 350).buffer(200)

#создаём области
# Вакуум - большой прямоугольник
# vacuum_shape = gmt.Polygon([
#     (0, 0), (0, 600), (800, 600), (800, 0)
# ])

#Круглый отражатель -вырезается из вакуума
# reflector_circle = gmt.Point(400, 300).buffer(150)

# # 3. Внутренняя среда (топливо, где нейтроны)
# core_circle = gmt.Point(400, 300).buffer(80)

# "вырезаем" из вакуума отражатель
# вакуум теперь это прямоугольник минус отражатель
# vacuum_area = vacuum_shape.difference(reflector_circle)

# отражатель - круг "минус" топливная область
# reflector_area = reflector_circle.difference(core_circle)

# среда - просто внутренний круг
# core_area = core_circle

# блок создания сред. Вакуума, отражателя и самой среды. Задаются их области, сечения, цвета и, по необходимости, вспомогательные флаги
vacuum = Enviroment(
    area=vacuum_area,
    Sigma_a=0.0000000001,
    Sigma_s=0.0000000001,
    color=(0, 0, 255),
    vacuum=True
)
reflective = Enviroment(
    area=reflector_area,
    Sigma_a=0,
    Sigma_s=1.5,  # например, чисто рассеивает
    color=(255, 0, 0),
    reflective=True
)
environment = Enviroment(
    area=core_area,
    Sigma_a=0.0000003,
    Sigma_s=0.3,
    color=(0, 255, 0)
)
# список всех сред
ENVIRONMENTS_LIST=[vacuum, reflective, environment]

# задаем количество нейтронов, которое необходимо симулировать
n_neutrons = 10000  # сколько нейтронов создаём
# задаем скорость каждого нейтрона
speed=5


# создаем n_neutrons нейтронов
particles = []
for _ in range(n_neutrons):
    particles.append(spawn_neutron(environment, speed))


# Главный цикл. Выполнение продолжается, пока не превышено максимальное число итераций/не закрыто окно отображения нейтронов/не нажата клавиша esc
while running and iterations < MAX_iterations:
    # проверка, что окно не закрыто
    check_stop_PyGame()
    # орисовка окна пайгейм
    win.fill((0, 0, 0))
    # отрисовка сред
    vacuum.draw(win)
    reflective.draw(win)
    environment.draw(win)
    
    # массив для хранения координат по абсциссе. Нужен для построения гистрограммы
    x_coordinats=[]

    # счетчик мертвых нейтронов(которые поглотились)
    dead=0 
    for p in particles:
        if p.alive==True:
            p.update_Position()
        else: dead+=1
        # заполняем х координаты
        x_coordinats.append(p.x)
        # рисуем нейтрон с новыми координатами
        pygame.draw.circle(win, p.color, (int(p.x), int(p.y)), p.radius)

    # восполняем потерю мертвых нейтронов, создавая новые    
    for _ in range(dead):
            particles.append(spawn_neutron(environment, speed))


    # удаляем из массива мертвые нейтроны
    particles = [p for p in particles if p.alive]



    # строим гистограмму. 
    plt.hist(x_coordinats, range=(0, 800), color = 'blue', edgecolor = 'black', bins=100)
    # эти 2 строки отвечают за построение на гистограмме границ отражателя и вакуума в конкретно примере с прямоугольниками
    plt.axvline([700], color='red', linestyle='--')
    plt.axvline([100], color='red', linestyle='--')
    # 
    plt.draw()
    plt.pause(0.00001)
    plt.clf()

    # отрисовка окна
    pygame.draw.rect(win, color, pygame.Rect(-r1, -r1, width + 2 * r1, height + 2 * r1), 5)
    pygame.display.update()
    pygame.time.delay(1)

# завершение работы PyGame
pygame.quit()
