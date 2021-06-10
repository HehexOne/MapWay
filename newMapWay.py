import mysql.connector
from collections import deque
import math
from PrimAlgo import Graph, prims_mst

class MapWay:

    def __init__(self):
        self.mydb = mysql.connector.connect(
            host='std-mysql',
            user='std_1450_mw',
            passwd='11223344',
            database='std_1450_mw'
        )

    def findBestWay(self,
                    points=None,
                    user=None,
                    number_of_places=1):
        start_point = points[0]
        end_point = points[1]
        ans = [points[0]]

        places_in_zone = self.inZone(first_point=start_point, second_point=end_point)
        start_point.category, end_point.category = 'S', 'E'
        places = places_in_zone
        places += [start_point, end_point]

        if places_in_zone == 0:
            return [start_point, end_point] # Нет точек
        if number_of_places > len(places):
            number_of_places = len(places) # Если у нас полученное число мест меньше нужного, меняем

        full_graph = [[math.inf] * len(places) for _ in range(len(places))]

        for i in range(len(full_graph)):
            for j in range(len(full_graph)):
                if i != j or (i != 0 and j != len(places) - 1):
                    full_graph[i][j] = self.getLength(places[i], places[j])

        g = Graph(representation='matrix', nfverts=len(full_graph))
        g.graph = full_graph
        g.matrix_to_lists()

        MST = prims_mst(g)
        ans = [end_point]
        temp = MST[-1]
        if temp == None: # Случай когда конечная точка - корень
            temp = MST[-2]
            flag = True
            for i in range(number_of_places):
                ans.append(places[temp])
                if MST[temp] == None:
                    flag = False
                    break
                if(temp == len(places) - 2):
                    break
                temp = MST[temp]
            if flag:
                ans.append(places[-2])
            return ans
        elif MST[-2] == None:
            flag = True
            for i in range(number_of_places):
                ans.append(places[temp])
                if MST[temp] == None:
                    flag = False
                    break
                if (temp == len(places) - 2):
                    break
                temp = MST[temp]
            if flag:
                ans.append(places[-2])
            return reversed(ans)
        else:
            # Будем рассматривать несколько случаев
            used = [0] * len(MST)
            temp = MST[-2]
            while MST[temp] != None:
                used[temp] = 1
                if MST[temp] == None:
                    break
                temp = MST[temp]
            road_from_end = [places[-1]]
            temp = MST[-1]
            while MST[temp] != None:
                if used[temp] == 1:
                    break
                road_from_end.append(places[temp])
                if MST[temp] == None:
                    break
                temp = MST[temp]
            road_from_start = [places[-2]]
            temp = MST[-2]
            while MST[temp] != None:
                road_from_start.append(places[temp])
                if used[temp] == 1:
                    break
                if MST[temp] == None:
                    break
                temp = MST[temp]
            if len(road_from_start) + len(road_from_end) <= number_of_places + 2:
                return road_from_start + list(reversed(road_from_end))
            else:
                first_places = (number_of_places + 2) // 2
                second_places = (number_of_places + 2) - first_places
                return road_from_start[:first_places] + list(reversed(road_from_end[:second_places]))

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

        query = f'SELECT * FROM Object WHERE ({left_point.latitude} >= {right_point.latitude} and (Object.longitude <= ' \
                f'{right_point.longitude} and (Object.longitude > {left_point.longitude} and Object.latitude < ' \
                f'{left_point.latitude} and Object.latitude > {right_point.latitude})) or ({left_point.latitude} < ' \
                f'{right_point.latitude} and (Object.longitude < {right_point.longitude} and Object.longitude > ' \
                f'{left_point.longitude} and Object.latitude < {right_point.latitude} and Object.latitude > ' \
                f'{left_point.latitude})));'
        mycursor = self.mydb.cursor()
        mycursor.execute(query)
        places = mycursor.fetchall()
        places_in_zone = []
        for x in places:
            place = Place(id=x[0], name=x[1], category=x[2], latitude=x[3], longitude=x[2])
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
