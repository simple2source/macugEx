import requests
import time
from multiprocessing import Pool

def create_thousand_request(index):
    start = time.time()

    for i in range(1000):
        response = requests.get("http://queryserver.ptmbcmrn4c.us-west-2.elasticbeanstalk.com/dev/map/pokemons?east=-73.979579269886&south=40.74876479398508&north=40.75126408902728&west=-73.98232048749922")

    end = time.time()

    print end - start


if __name__ == '__main__':
    p = Pool(20)
    print(p.map(create_thousand_request, range(20)))
