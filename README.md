# BO_WATCH
--------

## 目錄結構：
  - docker-setup: 擺放docker安裝相關的模板
  - share: 擺放與docker共用的volume

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
