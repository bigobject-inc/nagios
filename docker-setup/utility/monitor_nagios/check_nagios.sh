## Setup root path for app
    APP_ROOT=$( dirname $(readlink -f "$0") )
## load existent function
    source "$APP_ROOT/lib_check_nagios.sh"
    
## setup constant
    LOG_FILE=$1
    EXPIRE_MINUTE=$2
    
## check status and response
    chk_msg=$(check_nagios_log_mtime $LOG_FILE $EXPIRE_MINUTE)
    code=$?
    if [ $code != "0" ];
    then
        #### IMPLEMENTATION: When nagios has something wrong #####
        echo "==== Implement your action here when something wrong with nagios ===="
        echo $chk_msg
    else
        #### IMPLEMENTATION: When nagios is OK #####
        echo "==== Implement your action here when everything is ok with nagios ===="
        echo $chk_msg
    fi