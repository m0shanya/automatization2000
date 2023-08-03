># ChangerTaskTimer
>***This project is about CRUD .timer file's operations.***
>
>## If you need to use this project: in app.py, objects.py and file_maker.py change directory in which program find the .timer files
>
>### Usage
>```
> - Flask, Version=2.3.2
> - crispy-bootstrap5, Version=0.6
> - requests, Version=2.27.1
> - beautifulsoup4, Version=4.10.0
>```

## Http requests and response examples
>#GET
```shell
REQUEST
 
curl -X GET http://127.0.0.1:5000/

RESPONSE

{
  "kns_test.timer": {
    "Install": {
      "wantedby": "timers.targetOnCalendar"
    },
    "Timer": {
      "oncalendar": "test",
      "unit": "kns.service"
    },
    "Unit": {
      "description": "hello",
      "requires": "kns.service"
    }
  },
  "kns_test2.timer": {
    "Install": {
      "wantedby": "123"
    },
    "Timer": {
      "oncalendar": "123",
      "unit": "123"
    },
    "Unit": {
      "description": "test2",
      "requires": "123"
    }
  }
}

Response code: 200 (OK); Time: 294ms; Content length: 477 bytes
```
>#GET request for ANY record
```shell
REQUEST
 
curl -X GET http://127.0.0.1:5000/get/kns_test.timer

RESPONSE

{
  "Install": {
    "wantedby": "timers.targetOnCalendar"
  },
  "Timer": {
    "oncalendar": "test",
    "unit": "kns.service"
  },
  "Unit": {
    "description": "hello",
    "requires": "kns.service"
  }
}

Response code: 200 (OK); Time: 20ms; Content length: 210 bytes
```
>#POST
```shell
REQUEST
 
curl -X POST http://127.0.0.1:5000/post/?description=test&requires=123&oncalendar=123&unit=123&wantedby=123

RESPONSE

{
  "kns_test.timer": {
    "Install": {
      "wantedby": "timers.targetOnCalendar"
    },
    "Timer": {
      "oncalendar": "test",
      "unit": "kns.service"
    },
    "Unit": {
      "description": "hello",
      "requires": "kns.service"
    }
  },
  "kns_test2.timer": {
    "Install": {
      "wantedby": "123"
    },
    "Timer": {
      "oncalendar": "123",
      "unit": "123"
    },
    "Unit": {
      "description": "test2",
      "requires": "123"
    }
  },
  "kns_tester.timer": {
    "Install": {
      "wantedby": "123"
    },
    "Timer": {
      "oncalendar": "123",
      "unit": "123"
    },
    "Unit": {
      "description": "tester",
      "requires": "123"
    }
  }
}

Response code: 200 (OK); Time: 25ms; Content length: 698 bytes
```
>#PATCH
```shell
REQUEST
 
curl -X PATCH http://127.0.0.1:5000/update/kns_tester/?description=hello&oncalendar=test

RESPONSE

{
  "Install": {
    "wantedby": "123"
  },
  "Timer": {
    "oncalendar": "test",
    "unit": "123"
  },
  "Unit": {
    "description": "hello",
    "requires": "123"
  }
}

Response code: 200 (OK); Time: 33ms; Content length: 174 bytes
```
>#DELETE
```shell
REQUEST
 
curl -X DELETE http://127.0.0.1:5000/delete/kns_tester 

RESPONSE

{
  "kns_test.timer": {
    "Install": {
      "wantedby": "timers.targetOnCalendar"
    },
    "Timer": {
      "oncalendar": "test",
      "unit": "kns.service"
    },
    "Unit": {
      "description": "hello",
      "requires": "kns.service"
    }
  },
  "kns_test2.timer": {
    "Install": {
      "wantedby": "123"
    },
    "Timer": {
      "oncalendar": "123",
      "unit": "123"
    },
    "Unit": {
      "description": "test2",
      "requires": "123"
    }
  }
}

Response code: 200 (OK); Time: 25ms; Content length: 477 bytes
```
