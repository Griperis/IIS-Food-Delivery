python manage.py makemigrations FoodDelivery;
python manage.py migrate FoodDelivery;
python manage.py makemigrations;
python manage.py migrate;
echo "Populating database!"
python populate_db.py;
echo "Database populated!"
