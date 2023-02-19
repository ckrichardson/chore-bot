if [ $(crontab -l | wc -c) -eq 0 ]; 
then
  echo "crontab is empty"
else
  echo "crontab is not empty"
fi
