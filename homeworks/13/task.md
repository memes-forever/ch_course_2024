1. Развернуть S3 на базе open-source MinIO/Ceph или воспользуйтесь Object Storage от Yandex Cloud  
2. Установить clickhouse-backup и выполнить настройки storage policy в конфигурационных файлах БД  
3. Создать тестовую БД, в ней несколько тестовых таблиц и наполнить их данными  
4. Произвести бекапирование на удаленный ресурс (s3)  
5. "Испортить" данные в текущем инстансе ClickHouse \- удалить таблицу, изменить строку и пр.  
6. Произвести восстановление из резервной копии  
7. Убедиться, что "испорченные" данные успешно восстановлены