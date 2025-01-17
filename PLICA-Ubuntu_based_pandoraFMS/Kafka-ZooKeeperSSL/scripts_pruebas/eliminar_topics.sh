# Gestor de Flujos v.0 PLICA
# Maintainer: Universidad Politecnica de Madrid
# Contact: a.callejasz@upm.es


#!/bin/bash

# NOTA: En docker (contenedor kafka) es necesario habilitar "delete.topics.enable=true" en el fichero
# "server.properties" en el path del contenedor "/opt/kafka_2.12-0.11.0.1/config".

# Filtrado por puertos expuestos, kafka comparte puerto con el conector de elastic
# Se opta por el filtrado referenciado al nombre del contenedor levantado

kafka_id=$(docker ps -q --filter "name=kafkaSSL")
broker_ip=$(docker network inspect -f '{{range .IPAM.Config}}{{.Gateway}}{{end}}' kafkassl_PLICA)
port=$(docker inspect kafkaSSL | grep HostPort | sort | uniq | grep -o [0-9]*)

declare -a topics=("WF-DATA" "BT-DATA" "CS-DATA" "RF-DATA" "RM-DATA" "TI-DATA" "PF-DATA" "UBA-DATA")

for i in "${topics[@]}"
do
	# Eliminacion de topics desde Kafka instalado en docker
	docker exec -itd $kafka_id /opt/kafka/bin/kafka-topics.sh --delete --bootstrap-server=$broker_ip:$port \
	--command-config=/opt/kafka/config/producer_ssl.properties --topic "$i"

done

echo Topics eliminados