docker exec -u www-data -it practica1_nextcloud_1 php occ app:enable user_ldap
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable accessibility
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable dashboard
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable accessibility
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable firstrunwizard
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable nextcloud_announcements
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable photos
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable weather_status
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable user_status
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable survey_client
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable support
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable recommendations
docker exec -u www-data -it practica1_nextcloud_1 php occ app:disable updatenotification
