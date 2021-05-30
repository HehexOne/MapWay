from MapWay import *

start = Place(name="Start", position=Position(latitude=20, longtitude=2))


'''
    Уже точки не нужны, они в базе данных
'''

# p_in_1 = Place(name="p_in_1", position=Position(latitude=10, longtitude=50))
# p_in_2 = Place(name="p_in_2", position=Position(latitude=18, longtitude=70))
# p_out_1 = Place(name="p_out_1", position=Position(latitude=21, longtitude=135))
# p_out_2 = Place(name="p_out_2", position=Position(latitude=-10, longtitude=-30))

end = Place(name="End", position=Position(latitude=5, longtitude=100))

# places = [p_in_1, p_in_2, p_out_1, p_out_2]
points = [start, end]

algo = MapWay()
# find_way
# algo.findBestWay(points=points)

route = list(algo.findBestWay(points=points))
for place in route:
    print(place.name)