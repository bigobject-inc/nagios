# BO_WATCH
--------

## 目錄結構：
  - nagios: nagios server
    - nagios的核心都在這裡
  - nagios-api: nagios-api server
    - nagios-api為輸出nagios的

## Image build指令
### nagios
``` bash
  docker build -t bigobject/nagios:$version ./nagios
```

### nagios-api
``` bash
  docker build -t bigobject/nagios-api:$version ./nagios-api
```

## 使用說明：
  使用方式都在Google Docs上，請參閱「BOWatch使用手冊」。
