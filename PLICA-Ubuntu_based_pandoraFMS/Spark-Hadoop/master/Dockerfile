FROM spark_base

ARG SPARK_VERSION
ARG HADOOP_VERSION

LABEL org.label-schema.name="spark_master" \
      org.label-schema.description="Apache spark" \
      org.label-schema.version="${SPARK_VERSION}_${HADOOP_VERSION}" \
      org.label-schema.schema-version="1.0" \
      maintainer="acallejasz"

COPY master.sh template.sh /
COPY log4j.properties /spark/conf/

RUN  dpkg -i /pandoraAgents/pandorafms.agent_unix_spark_master.deb

EXPOSE 8080 7077 6066

CMD ["/bin/bash", "/master.sh"]
