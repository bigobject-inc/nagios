#### function body ####
    check_nagios_log_mtime(){
        LOG_FILE=$1
            # log file of nagios -> $PROJECT_DIR/share/nagios_var/status.dat
        EXPIRE_MINUTE=$2
            # expire minute -> alert if update time of log file is longer than ...
        
        # verify input
        if [ "$LOG_FILE" == "" ];
        then
            echo "[ERROR] Parameter LOG_FILE not given"
            return 1
        fi
        
        if [ "$EXPIRE_MINUTE" == "" ];
        then
            echo "[ERROR] Parameter EXPIRE_MINUTE not given"
            return 1
        fi
        
        # timestamp now
        now_ts=$(date +%s)
        
        # timestamp of log update time
        log_ts=$(date -r $LOG_FILE +%s)
        
        # compute time difference
        diff_minute=$((($now_ts-$log_ts)/60))
        if [ $diff_minute -gt $EXPIRE_MINUTE ];
        then
            # log update time expired, nagios is not OK
            echo "[WARNING] Nagios may stop working now, last update time is ${diff_minute} minutes ago"
            return 1
        else
            # nagios is fine
            echo "[OK] Nagios is good, last update time is ${diff_minute} minutes ago"
            return 0
        fi
    }