from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import cv2
import numpy as np
import matplotlib


#Вместо "2.png" впишите имя обрабатываемого файла с цветовыми пятнами
image = cv2.imread('2.png')
original = image.copy()

height, width = image.shape[:2]

#В "result.png", несмотря на название, будет лежать копия исходного файла
cv2.imwrite("result.png",image)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#Изображение размывается, поэтому используйте в качестве исходного 
#цветогого пятна объекты больше чем 3-5 пикселей в диаметре
blur = cv2.GaussianBlur(gray, (5,5), 0) 
thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]


district_points = []#содержит координаты центров цветовых пятен для разбиения Вороного
district_colors = []#содержит соответствующие цвета в формате (R/255,G/255,B/255)


for c in cnts:
    # Obtain bounding rectangle to get measurements
    x,y,w,h = cv2.boundingRect(c)

    # Find centroid
    M = cv2.moments(c)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    district_points.append((cX,height-cY))
    b,g,r = original[cY,cX]
    district_colors.append((r/255,g/255,b/255))

    # Draw the contour and center of the shape on the image
    cv2.rectangle(image,(x,y),(x+w,y+h),(36,255,12), 1)
    cv2.circle(image, (cX, cY), 3, (22, 100, 320), -1) 

#Я вывожу координаты центров районов на экран для последующего использования
#в CityGenerator. Почему-то у меня проблемы с выводом в файл (
print(district_points)

#Вот тут начинается самый спорный момент, для первоначального запуска я бы убрал 
#или закомментировал этот блок. Здесь я распределяю параметры криминального влияния,
#уровня бгатства и активности полиции по районам.
#Районы я определяю по цвету сових пятен, которые я пипеткой вытащил из рисунка
#Если у вас будут другие цвета и районы, исправьте набор условий ниже.
#Или просто выкиньте.
criminal = []
criminal_cm = matplotlib.cm.get_cmap('OrRd')

para = []

wealth = []
wealth_cm = matplotlib.cm.get_cmap('YlGn')

police = []
police_cm = matplotlib.cm.get_cmap('Blues')

areas = []


#Перебор районов по цветам с задачей параметров. Уберите тройные кавычки,
#чтобы использовать этот код. Впишите свои цвета и названия районов.

'''
for dc in list(district_colors):
    rgb = tuple([255*c for c in dc])
    if rgb == (133,211,196):
        areas+=['Двухэтажная Америка']
        criminal += [2]
        wealth += [2]
        police += [2]
    elif rgb == (12,167,137):
        areas+=['Меркато']
        criminal += [1]
        wealth += [3]
        police += [3]
    elif rgb == (45,155,240):
        areas+=['Даунтаун']
        criminal += [0]
        wealth += [4]
        police += [4]
    elif rgb == (218,0,99):
        areas+=['Особняки Элиты']
        criminal += [2]
        wealth += [4]
        police += [3]
    elif rgb == (101,44,179):
        areas+=['Кампус']
        criminal += [2]
        wealth += [2]
        police += [3]
    elif rgb == (143,209,79):
        areas+=['Латиноамериканское Гетто']
        criminal += [3]
        wealth += [1]
        police += [1]
    elif rgb == (255,168,20):
        areas+=['Фермерские хозяйства']
        criminal += [2]
        wealth += [2]
        police += [1]
    elif rgb == (255,77,22):
        areas+=['Трейлерный парк']
        criminal += [4]
        wealth += [0]
        police += [0]
    elif rgb == (128,128,128):
        areas+=['Порт и склады']
        criminal += [3]
        wealth += [1]
        police += [1]
    elif rgb == (65,75,178):
        areas+=['Океан']
        criminal += [0]
        wealth += [0]
        police += [0]
    elif rgb == (26,26,26):
        areas+=['Тюрьма']
        criminal += [4]
        wealth += [1]
        police += [4]
'''


cv2.imwrite('image.png', image)
cv2.imwrite('thresh.png', thresh)

#загоняем полученные центры районов в массив точек Вороного
voronoi_points = np.array(district_points)
#и добавляем ещё две, очень далёкие точки, чтобы полигоны на краю рисунка не были бесцветными
voronoi_points = np.append(voronoi_points, [[10*width,10*height], [-10*width,10*height], [-10*width,-10*height], [10*width,-10*height]], axis = 0)
vor = Voronoi(voronoi_points)


#Основной результат будет получен здесь: разбиение плоскости на сегменты и сохранение рисунка
fig = plt.figure()
ax = fig.add_subplot(111)

for r in range(len(vor.point_region)):
    region = vor.regions[vor.point_region[r]]
    if not -1 in region:
        polygon = [vor.vertices[i] for i in region]
        #в следующей строчке поменяйте коэффициент alpha для изменения прозрачности
        ax.fill(*zip(*polygon), ls= '-',lw=0., color=district_colors[r],alpha=0.4)
ax.set(xlim=(0, width), ylim=(0, height))
ax.axis('off')
ax.set_aspect('equal')
hSize = 100
hY = np.linspace(0,height,num=height//hSize+2)
hX = np.linspace(0,width,num=width//hSize+2)


plt.savefig('voronoi.jpg',dpi=300,bbox_inches='tight',pad_inches=0)
plt.close('all')


#Дальше код будет аналогичным, но вместо цветов с рисунка будут использоваться цвета
#из выбранного ColorMap'a для создания HeatMap'a. Вам потребуется заполнить предыдущий закомментированный блок
#Я по умолчанию считаю, что величины, которые вписаны в списки criminal, wealth и police находятся на промежутке от 0 до 4
'''

fig = plt.figure()
ax = fig.add_subplot(111)
for r in range(len(vor.point_region)):
    region = vor.regions[vor.point_region[r]]
    if not -1 in region:
        polygon = [vor.vertices[i] for i in region]
        ax.fill(*zip(*polygon), ls= '-',lw=0., color=criminal_cm(criminal[r]/4),alpha=0.4)
ax.set(xlim=(0, width), ylim=(0, height))
ax.axis('off')
ax.set_aspect('equal')
hSize = 100
hY = np.linspace(0,height,num=height//hSize+2)
hX = np.linspace(0,width,num=width//hSize+2)


plt.savefig('criminal.jpg',dpi=300,bbox_inches='tight',pad_inches=0)
plt.close('all')


fig = plt.figure()
ax = fig.add_subplot(111)
for r in range(len(vor.point_region)):
    region = vor.regions[vor.point_region[r]]
    if not -1 in region:
        polygon = [vor.vertices[i] for i in region]
        ax.fill(*zip(*polygon), ls= '-',lw=0., color=wealth_cm(wealth[r]/4),alpha=0.4)
ax.set(xlim=(0, width), ylim=(0, height))
ax.axis('off')
ax.set_aspect('equal')
hSize = 100
hY = np.linspace(0,height,num=height//hSize+2)
hX = np.linspace(0,width,num=width//hSize+2)


plt.savefig('wealth.jpg',dpi=300,bbox_inches='tight',pad_inches=0)
plt.close('all')



fig = plt.figure()
ax = fig.add_subplot(111)
for r in range(len(vor.point_region)):
    region = vor.regions[vor.point_region[r]]
    if not -1 in region:
        polygon = [vor.vertices[i] for i in region]
        ax.fill(*zip(*polygon), ls= '-',lw=0., color=police_cm(police[r]/4),alpha=0.4)
ax.set(xlim=(0, width), ylim=(0, height))
ax.axis('off')
ax.set_aspect('equal')
hSize = 100
hY = np.linspace(0,height,num=height//hSize+2)
hX = np.linspace(0,width,num=width//hSize+2)


plt.savefig('police.jpg',dpi=300,bbox_inches='tight',pad_inches=0)
plt.close('all')
'''