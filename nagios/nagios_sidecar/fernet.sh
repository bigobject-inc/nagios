# setup env for python
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# execute script
  choice=(
      "verify"
      "generate"
      "encrypt"
      "decrypt"
  );
  PS3="(fernet) > "
  select action in ${choice[@]}
  do
      case $action in
          "verify"|"generate"|"encrypt"|"decrypt")
              /usr/local/nagios/libexec/pybox/bin/python /usr/local/nagios/libexec/python/sidecar_fernet.py $action;;
          *)
            echo "not a valid action";;
      esac
  done
