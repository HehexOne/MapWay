class MapWay:

    def __init__(self,
                 nameAlgo=None,
                 arrAsks=None,
                 current_position=None,
                 points=None,
                 model=None,
                 places=None):
        import math
        self.nameAlgo = nameAlgo
        self.arrAsks = arrAsks
        self.points = points
        self.model = model
        self.places = places
        self.infinity = math.inf

    def findBestWay(self, user=None, points=None):
        '''
        user: пользователь для которого мы анализируем
        points: пока что массив на две точки
        [0]: начальная
        [1]: конечная
        '''
        import math
        from collections import deque
        # поиск объектов, которые попадают под интересующую нас зону

        '''
            Переделать всё это в один SQL запрос
            чтобы не ханить все точки в памяти и
            вычисления проводились на сервере

        '''
        #         places_in_zone = []
        #         for place in self.places:
        #             if self.inZone(first_point=points[0],
        #                            second_point=points[1],
        #                            object_place=place):
        #                 places_in_zone.append(place)

        '''
            Добавление начальной и конечной точки,
            можно будет добавить промежуточную
        '''
        places_in_zone = self.inZone(points[0], points[1])
        for point in points:
            places_in_zone.append(point)
        '''
        Построение графа исходя из модели

        1) Возьмём и посмотрим насколько подходит пользователю каждое место из предложенных,
            для этого будем использовать ранг каждого места для посетителя, рачитывать его мы будем по формуле,
            { Формулу я ещё не придумал }

        '''
        self.matrix_size_x = len(places_in_zone)
        matrix_places = [[0] * self.matrix_size_x for _ in range(self.matrix_size_x)]

        for i in range(self.matrix_size_x):
            for j in range(self.matrix_size_x):
                '''
                    Добаляю расстояния в матрицу

                    !!!!  Здесь нам надо будет брать время,
                    которое понадобится для прохода из
                    одной точки в другую с яндекс карт  !!!!

                    Расстояние думаю лучше измерять во времени, которое человек затратит на путь
                '''
                if (((places_in_zone[i].category == 'Start_point' and places_in_zone[j] == 'End_point') or
                     (places_in_zone[i].category == 'End_point' and places_in_zone[j] == 'Start_point')) and
                        self.matrix_size_x > 2):
                    matrix_places[i][j] = math.inf
                else:
                    matrix_places[i][j] = self.getLength(places_in_zone[i], places_in_zone[j])

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

        ans = [points[0]]
        for i in list(reversed(road)):
            ans.append(places_in_zone[i])
        return ans

    def all_pinned_points(self,
                          points=None,
                          start=None,
                          end=None):
        '''
            TODO: Закэшировать все расстояния между объектами, чтобы потом не делать запросы на сервера
            использую алгоритм построения минимального остового дерева (Алгоритм Прима)
        '''
        import math
        import heapq
        import random
        way = [start, end]
        if points == None:
            return way
        way.append(points)

        matrix = [[math.inf] for i in range(len(way))]

        for i in range(len(matrix)):
            for j in range(len(matrix)):
                matrix[i][j] = getLength(())

        key = [math.inf] * len(way)
        p = [None] * len(way)
        r = random.randint(0, len(matrix))
        key[r] = 0

        Q = way
        heapq.heapify(Q)

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
        left_point = None
        right_point = None

        # Problem: make all this with one query

        '''
            У нас есть эти точки изначально, поэтому можно вычислить их положение
        '''
        if first_point.position.longtitude <= second_point.position.longtitude:  #
            left_point = first_point
            right_point = second_point
        else:  #
            left_point = second_point
            right_point = first_point

        '''
            Сравнения с этими точками можно переделать польностью в один запрос


            if (left_point.position.latitude >= right_point.position.latitude) and (object_place.position.longtitude <= right_point.position.longtitude and
                    object_place.position.longtitude >= left_point.position.longtitude and
                    object_place.position.latitude <= left_point.position.latitude and
                    object_place.position.latitude >= right_point.position.latitude):
                return True
            else:
                return False

            if left_point.position.latitude < right_point.position.latitude and (object_place.position.longtitude <= right_point.position.longtitude and
                    object_place.position.longtitude >= left_point.position.longtitude and
                    object_place.position.latitude <= right_point.position.latitude and
                    object_place.position.latitude >= left_point.position.latitude):
                return True
            else:
                return False

            if (left_point.position.latitude >= right_point.position.latitude) and (object_place.position.longtitude <= right_point.position.longtitude and
                    object_place.position.longtitude >= left_point.position.longtitude and
                    object_place.position.latitude <= left_point.position.latitude and
                    object_place.position.latitude >= right_point.position.latitude) and 
                    left_point.position.latitude < right_point.position.latitude and (object_place.position.longtitude <= right_point.position.longtitude and
                    object_place.position.longtitude >= left_point.position.longtitude and
                    object_place.position.latitude <= right_point.position.latitude and
                    object_place.position.latitude >= left_point.position.latitude):
                return True
            else:
                return False


            Всё преобразовано в один запрос

            "SELECT * FROM Place WHERE ({left_point.position.latitude} >= {right_point.position.latitude} and 
                (Place.longtitude <= {right_point.position.longtitude} and
                    Place.longtitude >= {left_point.position.longtitude} and
                    Place.latitude <= {left_point.position.latitude} and
                    Place.latitude >= {right_point.position.latitude)}) or 
                    ({left_point.position.latitude} < {right_point.position.latitude} and 
                    (Place.longtitude <= {right_point.position.longtitude} and
                    Place.longtitude >= {left_point.position.longtitude} and
                    Place.latitude <= {right_point.position.latitude} and
                    Place.latitude >= {left_point.position.latitude)});"

            if left_point.position.latitude >= right_point.position.latitude and (object_place.position.longtitude <= right_point.position.longtitude and
                    object_place.position.longtitude >= left_point.position.longtitude and
                    object_place.position.latitude <= left_point.position.latitude and
                    object_place.position.latitude >= right_point.position.latitude) # 1 
                return True
            else:
                return False

            if left_point.position.latitude < right_point.position.latitude and (object_place.position.longtitude <= right_point.position.longtitude and
                    object_place.position.longtitude >= left_point.position.longtitude and
                    object_place.position.latitude <= right_point.position.latitude and
                    object_place.position.latitude >= left_point.position.latitude)
                return True
            else:
                return False

        '''
        query = f"SELECT * FROM Place WHERE ({left_point.position.latitude} >= {right_point.position.latitude} and (Place.longtitude <= {right_point.position.longtitude} and (Place.longtitude >= {left_point.position.longtitude} and Place.latitude <= {left_point.position.latitude} and Place.latitude >= {right_point.position.latitude})) or ({left_point.position.latitude} < {right_point.position.latitude} and (Place.longtitude <= {right_point.position.longtitude} and Place.longtitude >= {left_point.position.longtitude} and Place.latitude <= {right_point.position.latitude} and Place.latitude >= {left_point.position.latitude})));"

        mycursor = mydb.cursor()
        mycursor.execute(query)
        places = mycursor.fetchall()
        places_in_zone = []
        for x in places:
            place = Place(name=x[1], category=x[2], position=Position(latitude=x[3], longtitude=x[4]))
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
        return math.sqrt((first_point.position.latitude - second_point.position.latitude) ** 2 +
                         (first_point.position.longtitude - second_point.position.longtitude) ** 2)

    '''
    Ниже я буду пытаться сам написать алгоритм
    поиска пути исходя из наших критериев поиска
    а именно предпочтений пользователя и времени
    '''

    def evg_algo(self):
        '''

            Надо взять как минимум одну достопримечательность + (Сделал бесконечное расстояние до конечной точки)
            если она имеется в предложенной области
            и смотреть на время, которое указал пользователь при вводе
            при этом надо взять самые интересные, поэтому мы должны
            отсортировать объекты по степени их интересности и смотреть
            от самого интересного к менее интересному

            ----------------------------------
            |                                |
            |     S----\                     |
            |          -[]                   |
            |                                |
            |     []           []            |
            |                       []       |
            |                                |
            |            []                  |
            |                         E      |
            |                                |
            ----------------------------------
        '''

        pass

    '''
    Ниже представлены алгоритм Куна, думал его можно как-то
    использовать для поиска удовлетворяющего пути,
    но не думаю что он будет эффективен
    '''
    # def kunAlgo(self):
    #     '''
    #     Здесь тоже ошибки, потому что алгоритм написан для общего
    #     случая, надо переделать под нашу ситуацию
    #     '''
    #     fill(matching, -1)
    #     for i in range(n):
    #         fill(used, False)
    #         dfs(i)
    #     for i in range(n):
    #         if(matching[i] != - 1):
    #             print(i + " " + matching[i])
    #     pass
    #
    # def fill(self, graph, number):
    #     '''
    #     Для заполнения матрицы каким-то одним значением
    #     '''
    #     for i in range(len(graph)):
    #         for j in range(len(graph[i])):
    #             graph[i][j] = number

    # def dfs(self, v:int):
    #     '''
    #     Здесь ошибка
    #     '''
    #     if (used[v]):
    #         return False
    #     used[v] = True
    #     for to in g[v]:
    #         if (matching[to] == -1 or dfs(matching[to])): #ошбика где dfs(matching[to])
    #             matching[to] = v
    #             return True
    #     return False


class WorkWithDB:

    def __init__(self):
        pass


class User:

    def __init__(self,
                 time=None,
                 age=None,
                 religion=None,
                 sex=None,
                 marital_status=None,
                 other_info=None):
        '''
            Create or get dataset
            Сделал все метрики для лучшего понимания что собирать с людей
        '''

    #         self.category = model.predict()

    def getCategory(self):
        return self.category


class GraphType:

    def __init__(self,
                 length=None,
                 vertex_number=None):
        self.length = length
        self.vertex_number = vertex_number


class Position:

    def __init__(self,
                 latitude=None,
                 longtitude=None,
                 type_of_point=None):
        self.latitude = latitude  # Широта
        self.longtitude = longtitude  # Долгота


class Place:
    '''
        ---------------------------------------------
        |                                           |
        |   Категории мест:                         |
        |       Start_point: начальная точка        |
        |           пути                            |
        |       Middle_point: точки, которые        |
        |           пользователь отметил между      |
        |           начальной и конечной            |
        |       End_point: конечная точка пути      |
        |       Place_point: точка с местом         |
        |                                           |
        |                                           |
        ---------------------------------------------
    '''

    def __init__(self,
                 name=None,
                 position: Position = None,
                 category=None,
                 rank=None,
                 length=None,
                 visit_time=None):
        self.name = name
        self.position = position
        self.category = category
        self.length = length
        self.rank = rank
        self.visit_time = visit_time


class Metrics_and_algos:

    def __init__(self):
        pass

    def confustion_matrix(self):
        pass

    def accuracy_metric(self):
        '''
        Эту метрику можно назвать базовой.
        Она измеряет количество верно классифицированных объектов
        относительно общего количества всех объектов.
        '''
        pass

    def sensitivity_metric(self):
        '''
        Сколько объектов наша модель смогла правильно классифицировать
        с позитивной меткой из всего множества позитивных.
        '''
        pass

    def precision_metric(self):
        '''
        Сколько из всех объектов, которые классифицируются как положительные,
        действительно являются положительными, относительно общего
        количества полученных от модели позитивных меток.
        '''
        pass

    def f1_score(self):
        '''
        Сочетание precision и recall,
        дает некоторый компромисс между ними двумя,
        оценка F1 достигает своего наилучшего значения в 1 и худшее в 0.
        '''
        pass

