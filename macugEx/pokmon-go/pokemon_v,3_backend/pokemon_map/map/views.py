import logging
import json

import s2sphere
import boto3

from django.shortcuts import render
from django.http import HttpResponse

from db_accessor import get_pokemons_from_db 

SQS_QUEUE_NAME="awseb-e-zg2yhc6ipt-stack-AWSEBWorkerQueue-1BWAGS3AVRPNA"

def break_down_area_to_cell(north, south, west, east):
    """ Return a list of s2 cell id """
    result = []

    region = s2sphere.RegionCoverer()
    region.min_level = 15
    region.max_level = 15
    p1 = s2sphere.LatLng.from_degrees(north, west)
    p2 = s2sphere.LatLng.from_degrees(south, east)

    rect = s2sphere.LatLngRect.from_point_pair(p1, p2)
    area = rect.area()
    if (area * 1000 * 1000 * 100 > 7):
        return result

    cell_ids = region.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))
    result += [ cell_id.id() for cell_id in cell_ids ] 

    return result

def scan_area(north, south, west, east):
    result = []

    # 1. Find all point to search with the area
    cell_ids = break_down_area_to_cell(north, south, west, east)

    # 2. Search each point, get result from api
    work_queue = boto3.resource('sqs', region_name='us-west-2').get_queue_by_name(QueueName=SQS_QUEUE_NAME)
    for cell_id in cell_ids:
        print cell_id
        # 3. Send request to elastic beanstalk worker server
        work_queue.send_message(MessageBody=json.dumps({"cell_id":cell_id})) 

    return result


def pokemons(request):
    # 1. Get longitude latitude info
    north = request.GET["north"]
    south = request.GET["south"]
    west = request.GET["west"]
    east = request.GET["east"]

    # 2. Query database
    result = get_pokemons_from_db(north, south, west, east)

    # 3. Publish crawl job
    scan_area(float(north), float(south), float(west), float(east))
    
    return HttpResponse(json.dumps(result))
