
#set -x

PID=`netstat -napt| grep LISTEN |  grep 4998 |  awk {'print $7'} | cut -d'/' -f1`
option="${1}"


case ${option} in

stop)




if  [[ -f /proc/$PID/exe  ]]
 then
kill -9 $PID
echo "app stoped"
echo $PID killed

else
echo " app is aluready stopped. "
fi





          ;;

start)
     if [ $PID > 0 ]; then
     echo " app is running please stop it first"
     else

#     cd /var/www/vhosts/vkingsolutions.com/public_html/clearsight.live/APIcode
     source api_venv/bin/activate
     nohup python3 app.py &
     sleep 5
     fi
          ;;

status )
     if [[ $PID > 0 ]]; then
     echo " app is running in PID $PID "
     else
     echo "app is not running"
     fi

          ;;
     *)
          echo "please use start|stop|status"
          ;;
esac
