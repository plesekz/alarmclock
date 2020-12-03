#if __name__ == "__main__":
#   from main import 
# ^ comment that
import logging
logging.basicConfig(filename='test.log', encoding='utf-8', level=logging.DEBUG)

if __name__ == "__main__":
    from main import sec_s_mn
    test = {'hour': 13,
            'minute': 14,
            'second': 2}
    assert sec_s_mn(test) == 47642

if __name__ == "__main__":
    from main import digest_weather
    test_weather = {'weather':
                    [{'main': 'Clear Skies'},{'main':'Rain'}],
                    'main':
                        {'temp': 275, 'feels_like': 270},
                    'sys':
                        {'sunrise':21600, 'sunset':57600}
                    }
    #print(digest_weather(test_weather))
    test = "Weather is Clear Skies, Rain, and it is 275K, but it feels like 270K."
    test+= "The sunrise is at 6:00:00."
    test+= "The sunset is at 16:00:00."
    #print(test)
    assert digest_weather(test_weather) == test

if __name__ == "__main__":
    from main import save_digest_news
    test_news = { 'articles':[
            {'title':'Matt'
             },
            {'title':'Gerry'
             },
            {'title':'John'
             },
            {'title':'Daniel'
             },
            {'title':'Michael'
             }
                ]
                  }
    assert save_digest_news(test_news) == [['Matt','Gerry','John','Daniel','Michael'],"Top headlines: Matt, Gerry, John, Daniel, Michael, "]

if __name__ == '__main__':
    from main import digest_covid
    test_data = {'data':
                     [
                         {'newCasesByPublishDate':20},
                         {'newCasesByPublishDate':19},
                         {'newCasesByPublishDate':20}
                     ]
                }
    assert digest_covid(test_data) == "There were 19 new cases yesterday. Which makes -5.0% increase. There are 20 cases today as of now."
if __name__ == "__main__":
    from main import sec_t_times
    assert sec_t_times(3840)=="1:04:00"

if __name__ =="__main__":
    from main import rel_t
    test = {'time':
            {'minute': 24,
             'hour': 2,
             'day': 14,
             'month': 2,
             'year': 2010}
            }
    assert rel_t(test) == 201002140224
