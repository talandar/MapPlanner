import math
import os
import random
import numpy as np

import pygame
import great_circle_calculator.great_circle_calculator as gcc

max_framerate = 60

window_size = window_width, window_height = 1920, 1080
black = 0, 0, 0
arc_color_1 = 139, 0, 0
arc_color_2 = 50, 205, 50

ship_speed_km_per_day = 2700
arc_resolution_km = 100


def main():
    pygame.init()
    Clock = pygame.time.Clock()
    random.seed()

    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)

    globeSurface = pygame.transform.scale(
        pygame.image.load('images/GlobeMap.png'),
        window_size)

    display_screen = pygame.display.set_mode(window_size,
                                             pygame.HWSURFACE |
                                             pygame.DOUBLEBUF |
                                             pygame.NOFRAME)

    pygame.event.set_grab(False)

    start_point = None
    end_point = None

    path_overlay = pygame.surface.Surface(window_size, pygame.SRCALPHA)

    quit = False
    while not quit:
        Clock.tick(max_framerate)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit = True
                elif event.key == pygame.K_SPACE:
                    print("clear route")
                    start_point = None
                    end_point = None
                    path_overlay = pygame.surface.Surface(window_size,
                                                          pygame.SRCALPHA)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = pygame.mouse.get_pos()
                click_x = click_pos[0]
                click_y = click_pos[1]
                print('click x/y: ', click_x, click_y)

                lon_lat_point = click_lon, click_lat = screen_x_y_to_lon_lat((click_x, click_y))

                print("click lon/lat:", click_lon, click_lat)
                if start_point is None:
                    start_point = lon_lat_point
                else:
                    end_point = lon_lat_point
                    draw_arc(start_point, end_point, path_overlay)
                    start_point = end_point

        display_screen.fill(black)

        # handle scaling and drawing game
        display_screen.blit(globeSurface, (0, 0))
        display_screen.blit(path_overlay, (0, 0))
        pygame.display.flip()

    pygame.quit()


def screen_x_y_to_lon_lat(point):
    # latitude is up/down
    # longitude is left/right

    # latitude 0 is middle of map/equator, goes from -90 to 90
    lat = ((window_height - point[1])/window_height)*180 - 90

    # longitude -180 is left of map, goes to 180
    lon = (point[0]/window_width)*360 - 180
    return (lon, lat)


def lon_lat_to_screen_x_y(point):
    x = ((point[0] + 180) / 360) * window_width
    y = window_height - (((point[1] + 90) / 180) * window_height)
    return (x, y)


def draw_arc(start_point, end_point, path_overlay):
    dist_km = gcc.distance_between_points(start_point, end_point, unit='kilometers')
    print(dist_km)
    travel_day_count = dist_km / ship_speed_km_per_day

    day_points = []
    print("will take ", travel_day_count, "days")
    for day in range(math.ceil(travel_day_count)):
        frac = day / travel_day_count
        print(frac)
        day_endpoint = gcc.intermediate_point(start_point, end_point, frac)
        day_points.append(day_endpoint)
    day_points.append(end_point)

    for day_index in range(len(day_points) - 1):
        day_color = arc_color_1 if day_index % 2 == 0 else arc_color_2
        s = day_points[day_index]
        e = day_points[day_index + 1]

        p1 = s
        for i in np.linspace(1/20, 1, num=20, endpoint=True):
            p2 = gcc.intermediate_point(s, e, i)
            pygame.draw.line(path_overlay, day_color, lon_lat_to_screen_x_y(p1), lon_lat_to_screen_x_y(p2), 5)
            p1 = p2


if __name__ == "__main__":
    main()
