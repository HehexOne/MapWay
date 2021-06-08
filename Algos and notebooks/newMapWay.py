import mysql.connector
from collections import deque
import math
from random import randint

class MapWay:

    def __init__(self):
        self.mydb = mysql.connector.connect(
            host='std-mysql',
            user='std_1455_map_way',
            passwd='12345678',
            database='std_1455_map_way'
        )

    def findBestWay(self,
                    points=None):
        start_point = points[0]
        end_point = points[1]
        ans = [points[0]]

        places_in_zone = self.inZone(first_point=start_point, second_point=end_point)
        start_point.category, end_point.category = 'Start_point', 'End_point'
        places_in_zone.append(start_point)
        places_in_zone.append(end_point)
        self.matrix_size_x = len(places_in_zone)
        matrix_places = [[math.inf] * self.matrix_size_x for _ in range(self.matrix_size_x)]

        for i in range(self.matrix_size_x):
            for _ in range(4):
                rnd_num = randint(0, self.matrix_size_x - 1)
                if (((places_in_zone[i].category == 'Start_point' and places_in_zone[rnd_num] == 'End_point') or
                     (places_in_zone[i].category == 'End_point' and places_in_zone[rnd_num] == 'Start_point')) and
                        self.matrix_size_x > 2):
                    matrix_places[i][rnd_num] = math.inf
                else:
                    matrix_places[i][rnd_num] = self.getLength(places_in_zone[i], places_in_zone[rnd_num])

        '''

        S
         \
          \
           \
            *-------E

        Буду использовать алгоритм дейкстры для поиска пути, но буду так же искать по точке,
        которая больше всего нравится пользователю и по времени до конца
        '''

        start_point = len(matrix_places) - len(points)
        end_point = len(matrix_places) - 1
        dist = [math.inf] * len(matrix_places)
        way = [0] * len(matrix_places)
        way[start_point] = 0
        dist[0] = 0
        Q = deque()
        Q.append(len(places_in_zone) - len(points))
        while Q:
            v = Q.pop()
            for u in range(len(matrix_places[v])):
                if (dist[u] > dist[v] + matrix_places[v][u]):
                    dist[u] = dist[v] + matrix_places[v][u]
                    way[u] = v
                    Q.append(u)

        '''

                Чтобы восстановить оптимальный путь от
                начальной вершины до коненой нам нужно просто смотреть на массив
                в котором у нас записаны минимальные расстояния до начальной вершины
                Мы будем жадно брать самое маленькое значение

        '''

        road = [end_point]
        now_point = end_point
        while way[now_point] != now_point:
            now_point = way[end_point]
            road.append(now_point)

        for i in list(reversed(road)):
            ans.append(places_in_zone[i])

        return ans;

    def inZone(self,
               first_point=None,
               second_point=None):
        '''
            TODO: добавить функцию просмотра в окружении на точках, для захвата большего количества возможных мест

            y                                         y
            ^                                         ^
            X----------------------                   --------------------Y
            |         *           |                   |   *               |   *
            |                     | *            *    |            *      |
            |    *         *      |                   |                   |
            |                     |                   |       *           |
        *   |                     |                   |                   |
            |         *       *   |    *              |                   | *
            |                     |               *   |   *               |
          * ----------------------Y > x               X-------------------- > x

        '''

        if first_point.longitude <= second_point.longitude:  #
            left_point = first_point
            right_point = second_point
        else:
            left_point = second_point
            right_point = first_point


        query = f'SELECT * FROM Place WHERE ({left_point.latitude} >= {right_point.latitude} and (Place.longitude <= ' \
                f'{right_point.longitude} and (Place.longitude >= {left_point.longitude} and Place.latitude <= ' \
                f'{left_point.latitude} and Place.latitude >= {right_point.latitude})) or ({left_point.latitude} < ' \
                f'{right_point.latitude} and (Place.longitude <= {right_point.longitude} and Place.longitude >= ' \
                f'{left_point.longitude} and Place.latitude <= {right_point.latitude} and Place.latitude >= ' \
                f'{left_point.latitude})));'
        mycursor = self.mydb.cursor()
        mycursor.execute(query)
        places = mycursor.fetchall()
        places_in_zone = []
        for x in places:
            place = Place(id=x[0], name=x[1], category=x[2], latitude=x[3], longitude=x[4])
            places_in_zone.append(place)

        return places_in_zone

    def getLength(self, first_point, second_point):
        '''
        :param first_point:
        :param second_point:
        Брать
        :return:
        '''
        import math
        return math.sqrt((first_point.latitude - second_point.latitude) ** 2 +
                         (first_point.longitude - second_point.longitude) ** 2)

class Place:

    def __init__(self, id=None, name=None, category=None, longitude=None, latitude=None):
        self.id = id
        self.name = name
        self.category = category
        self.longitude = longitude
        self.latitude = latitude
