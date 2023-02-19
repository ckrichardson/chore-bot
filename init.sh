pwd=$(pwd)

if [ $(crontab -l | wc -c) -eq 0 ]; 
then
  echo "0 9 * * fri python3 $pwd/src/chore-picker.py" | crontab -
else
  (crontab -l ; echo "0 9 * * fri python3 $pwd/src/chore-picker.py") | crontab -
fi
